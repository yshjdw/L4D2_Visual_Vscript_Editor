"""Detached standard-library-only updater, executed after the GUI has exited.

The GUI copies this script outside the installation before launching it. No
other l4visual imports are needed while editor files are being replaced.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import time
import zipfile

ALLOWED_FILES = {'app.py', 'start_windows.bat', 'requirements.txt'}
ALLOWED_DIRS = {'l4visual', 'resources', 'tests', 'examples', 'tools', 'CHANGELOGS'}
MAX_UNPACKED_BYTES = 600 * 1024 * 1024


def _wait_for_exit(pid: int, seconds: int = 90) -> None:
    if pid <= 0:
        raise RuntimeError('Missing parent application PID.')
    if os.name == 'nt':
        import ctypes
        kernel = ctypes.windll.kernel32
        kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
        kernel.OpenProcess.restype = ctypes.c_void_p
        kernel.WaitForSingleObject.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        kernel.CloseHandle.argtypes = [ctypes.c_void_p]
        handle = kernel.OpenProcess(0x00100000, False, pid)
        if handle:
            try:
                if kernel.WaitForSingleObject(handle, seconds * 1000) != 0:
                    raise RuntimeError('Editor did not exit before update timeout.')
            finally:
                kernel.CloseHandle(handle)
    else:
        for _ in range(seconds * 10):
            try:
                os.kill(pid, 0)
            except ProcessLookupError:
                return
            time.sleep(0.1)
        raise RuntimeError('Editor did not exit before update timeout.')


def _select_files(archive: zipfile.ZipFile):
    infos = archive.infolist()
    if len(infos) > 6000:
        raise RuntimeError('Too many files in update archive.')
    names = {item.filename for item in infos if not item.is_dir()}
    candidates = sorted((name[:-6] for name in names if name.endswith('app.py')), key=len)
    prefix = next((pre for pre in candidates if pre + 'l4visual/ui/main_window.py' in names
                   and pre + 'l4visual/codegen.py' in names), None)
    if prefix is None:
        raise RuntimeError('Not an editor application update package.')
    chosen, seen, total = [], set(), 0
    for item in infos:
        name = item.filename
        if ('\\' in name or name.startswith('/') or '\x00' in name or
                '..' in PurePosixPath(name).parts or re.match(r'^[A-Za-z]:', name)):
            raise RuntimeError('Unsafe filename in update ZIP.')
        if stat.S_IFMT(item.external_attr >> 16) == stat.S_IFLNK:
            raise RuntimeError('Symlinks are not allowed in updates.')
        if item.is_dir() or not name.startswith(prefix):
            continue
        relative = name[len(prefix):]
        parts = PurePosixPath(relative).parts
        if relative.lower().endswith('.l4vp'):
            continue
        if not parts or (parts[0] not in ALLOWED_DIRS and relative not in ALLOWED_FILES and
                         not (len(parts) == 1 and relative.lower().endswith(('.md', '.txt')))):
            continue
        if relative in seen:
            raise RuntimeError('Duplicate update file.')
        seen.add(relative)
        total += item.file_size
        if total > MAX_UNPACKED_BYTES:
            raise RuntimeError('Update expanded size exceeds safety limit.')
        chosen.append((item, relative))
    if not {'app.py', 'l4visual/ui/main_window.py', 'l4visual/codegen.py',
            'l4visual/version.py'}.issubset(seen):
        raise RuntimeError('Editor update ZIP is missing mandatory files.')
    return chosen


def _safe_target(root: Path, relative: str) -> Path:
    target = root.joinpath(*PurePosixPath(relative).parts)
    # Reject pre-existing symlinks and junction-like redirects in managed paths.
    curr = root
    for part in PurePosixPath(relative).parts:
        curr = curr / part
        if curr.is_symlink():
            raise RuntimeError(f'Update destination contains a symlink: {relative}')
    if target.exists() and not target.is_file():
        raise RuntimeError(f'Update destination is not a file: {relative}')
    return target


def _atomic_copy(source: Path, target: Path):
    target.parent.mkdir(parents=True, exist_ok=True)
    staging = target.with_name(target.name + f'.l4vp-update-{os.getpid()}.tmp')
    try:
        shutil.copy2(source, staging)
        os.replace(staging, target)
    finally:
        staging.unlink(missing_ok=True)


def install_archive(zip_file: Path, install_dir: Path, working_dir: Path, expected_version: str = '') -> int:
    root = install_dir.resolve(strict=True)
    if not (root / 'app.py').is_file() or not (root / 'l4visual' / 'ui' / 'main_window.py').is_file():
        raise RuntimeError('Target is not an existing editor installation.')
    extracted = working_dir / 'payload'
    backup = working_dir / 'backup'
    extracted.mkdir(parents=True, exist_ok=True)
    backup.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_file) as archive:
        files = _select_files(archive)
        for info, relative in files:
            target = extracted.joinpath(*PurePosixPath(relative).parts)
            target.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(info) as reader, target.open('wb') as writer:
                shutil.copyfileobj(reader, writer, 256 * 1024)
    if expected_version:
        version_source = (extracted / 'l4visual' / 'version.py').read_text(encoding='utf-8')
        match = re.search(r'APP_VERSION\s*=\s*[\'\"]([^\'\"]+)', version_source)
        if not match or match.group(1).lstrip('vV') != expected_version.lstrip('vV'):
            raise RuntimeError('Downloaded application version does not match the selected Release.')
    # Validate all paths, and create recovery copies before changing ANY file.
    to_install = []
    for _, relative in files:
        dest = _safe_target(root, relative)
        source = extracted.joinpath(*PurePosixPath(relative).parts)
        existed = dest.exists()
        if existed:
            preserved = backup.joinpath(*PurePosixPath(relative).parts)
            preserved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(dest, preserved)
        to_install.append((source, dest, relative, existed))
    touched = []
    try:
        for source, dest, relative, existed in to_install:
            _atomic_copy(source, dest)
            touched.append((dest, relative, existed))
    except Exception:
        for dest, relative, existed in reversed(touched):
            if existed:
                _atomic_copy(backup.joinpath(*PurePosixPath(relative).parts), dest)
            else:
                dest.unlink(missing_ok=True)
        raise
    return len(touched)


def _report(success: bool, message: str, version: str):
    path = Path.home() / '.l4vp_visual_editor' / 'update_status.json'
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({'success': success, 'message': message, 'version': version},
                                   ensure_ascii=False), encoding='utf-8')
    except OSError:
        pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--parent-pid', type=int, required=True)
    parser.add_argument('--install-dir', required=True)
    parser.add_argument('--archive', required=True)
    parser.add_argument('--working-dir', required=True)
    parser.add_argument('--version', required=True)
    args = parser.parse_args()
    try:
        _wait_for_exit(args.parent_pid)
        number = install_archive(Path(args.archive), Path(args.install_dir),
                                 Path(args.working_dir), args.version)
        _report(True, f'Updated {number} application files.', args.version)
        subprocess.Popen([sys.executable, 'app.py'], cwd=args.install_dir,
                         creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0))
        return 0
    except Exception as exc:
        _report(False, str(exc), args.version)
        return 1
    finally:
        # Running updater_worker.py may be locked on Windows; deletion is best effort.
        shutil.rmtree(args.working_dir, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
