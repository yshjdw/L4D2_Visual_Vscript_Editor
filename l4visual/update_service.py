"""Release discovery and safely staged downloads for the optional GitHub updater.

This module has no Qt dependency, so network and archive validation can be tested
without a graphical desktop. Downloads never mutate the installed editor.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import hashlib
import datetime
import json
import re
import shutil
import stat
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile

from .version import APP_VERSION

REPOSITORY = 'yshjdw/L4D2_Visual_Vscript_Editor'
RELEASES_API = f'https://api.github.com/repos/{REPOSITORY}/releases/latest'
RELEASES_PAGE = f'https://github.com/{REPOSITORY}/releases'
MAX_DOWNLOAD_BYTES = 300 * 1024 * 1024
MAX_UNPACKED_BYTES = 600 * 1024 * 1024
MAX_ENTRIES = 6000
ASSET_PATTERN = re.compile(r'(?i)(?:l4d2[_ -]visual[_ -]vscript(?:[_ -]editor|[_ -]visual[_ -]prototype)?|l4d2[_ -]vscript[_ -]visual[_ -]prototype).*\.zip$')
VERSION_PATTERN = re.compile(r'^v?(\d+(?:\.\d+){1,3})(?:[-+][a-zA-Z0-9._-]+)?$', re.I)
ALLOWED_FILES = {'app.py','start_windows.bat','requirements.txt'}
ALLOWED_DIRS = {'l4visual','resources','tests','examples','tools','CHANGELOGS'}


class UpdateError(Exception):
    """Safe update error with a stable reason for localized UI reporting."""

    def __init__(self, message, *, code='unknown', detail=''):
        super().__init__(message)
        self.code = code
        self.detail = detail


def update_error_text(error, language='en'):
    """Localize expected GitHub/network failures; preserve debugging information."""
    zh = language == 'zh'
    code = getattr(error, 'code', '')
    detail = str(getattr(error, 'detail', '') or '').strip()
    messages = {
        'rate_limited': (
            'GitHub API rate limit reached (HTTP 403). Try again after the limit resets or open Releases in your browser.',
            'GitHub API 请求次数达到上限（HTTP 403）。请在额度恢复后重试，或用浏览器打开 Releases 页面。'),
        'forbidden': (
            'GitHub denied the request (HTTP 403). This may be caused by network/proxy restrictions or API access controls. Try the Releases page in a browser.',
            'GitHub 拒绝了请求（HTTP 403）。可能是网络／代理限制或 API 访问策略导致。请尝试用浏览器打开 Releases 页面。'),
        'no_release': (
            'No public GitHub Release found (HTTP 404). Publish a formal Release with an editor ZIP asset.',
            '未找到公开的 GitHub 正式 Release（HTTP 404）。请发布正式版本并上传编辑器 ZIP 附件。'),
        'unauthorized': (
            'GitHub rejected authentication (HTTP 401). Open Releases in the browser to verify access.',
            'GitHub 认证失败（HTTP 401）。请在浏览器中确认是否可以访问 Releases。'),
        'network': (
            'Unable to connect to GitHub. Check your network or proxy settings; you can still use the editor offline.',
            '无法连接 GitHub。请检查网络或代理设置；编辑器仍可离线使用。'),
    }
    if code in messages:
        result = messages[code][1 if zh else 0]
        if detail:
            if zh and detail.startswith('Reset time (UTC): '):
                detail = '预计额度恢复时间（UTC）：' + detail[len('Reset time (UTC): '):]
                result += '\n' + detail
            else:
                result += ('\n补充信息：' if zh else '\nDetails: ') + detail
        return result
    if isinstance(error, UpdateCancelled):
        return '下载已取消。' if zh else 'Download cancelled.'
    if zh:
        # Keep unexpected server/library details available, rather than wrongly translating them.
        return '更新检查或下载失败。\n技术详情：' + str(error)
    return str(error)


class UpdateCancelled(UpdateError):
    pass


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    tag: str
    html_url: str
    notes: str
    asset_url: str = ''
    asset_name: str = ''
    asset_size: int = 0
    sha256: str = ''


def parse_version(text: str) -> tuple[int, ...]:
    match = VERSION_PATTERN.fullmatch(str(text).strip())
    if match is None:
        raise UpdateError(f'Unsupported version tag: {text!r}')
    parts = [int(piece) for piece in match.group(1).split('.')]
    return tuple((parts + [0] * 4)[:4])


def is_newer(remote: str, local: str = APP_VERSION) -> bool:
    return parse_version(remote) > parse_version(local)


def trusted_download_url(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    host = (parsed.hostname or '').lower()
    return parsed.scheme == 'https' and parsed.username is None and parsed.password is None and (
        host == 'github.com' or host == 'api.github.com' or host.endswith('.githubusercontent.com')
    )


class _GitHubRedirects(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not trusted_download_url(newurl):
            raise UpdateError('Untrusted GitHub download redirect was blocked.')
        return super().redirect_request(req, fp, code, msg, headers, newurl)


_OPENER = urllib.request.build_opener(_GitHubRedirects())


def release_from_json(payload: dict) -> ReleaseInfo:
    if not isinstance(payload, dict) or payload.get('draft') or payload.get('prerelease'):
        raise UpdateError('Latest release is unavailable or is a prerelease.')
    tag = str(payload.get('tag_name', ''))
    parse_version(tag)
    html_url = str(payload.get('html_url', RELEASES_PAGE))
    if not html_url.startswith(f'https://github.com/{REPOSITORY}/releases/'):
        html_url = RELEASES_PAGE
    assets = [asset for asset in payload.get('assets', []) if isinstance(asset, dict)]
    # Prefer the packaged application over GitHub's automatically generated source archive.
    matching = [asset for asset in assets if ASSET_PATTERN.fullmatch(str(asset.get('name', '')))]
    matching.sort(key=lambda asset: ('prototype' not in str(asset.get('name','')).lower(),
                                     len(str(asset.get('name','')))))
    asset = matching[0] if matching else {}
    asset_url = str(asset.get('browser_download_url', ''))
    if asset_url and not trusted_download_url(asset_url):
        asset_url = ''
    digest = str(asset.get('digest') or '')
    digest = digest[7:].lower() if digest.startswith('sha256:') and re.fullmatch(r'sha256:[a-fA-F0-9]{64}', digest) else ''
    return ReleaseInfo(version=tag.lstrip('vV'), tag=tag, html_url=html_url,
                       notes=str(payload.get('body') or ''), asset_url=asset_url,
                       asset_name=str(asset.get('name','')) if asset_url else '',
                       asset_size=int(asset.get('size') or 0) if asset_url else 0,
                       sha256=digest if asset_url else '')


def check_latest_release(timeout: float = 8.0) -> ReleaseInfo:
    request = urllib.request.Request(RELEASES_API, headers={
        'Accept':'application/vnd.github+json',
        'User-Agent':f'L4D2-Visual-VScript-Editor/{APP_VERSION}',
        'X-GitHub-Api-Version':'2022-11-28',
    })
    try:
        with _OPENER.open(request, timeout=timeout) as response:
            raw = response.read(1024 * 1024 + 1)
            if len(raw) > 1024 * 1024:
                raise UpdateError('GitHub release metadata exceeded size limit.')
            return release_from_json(json.loads(raw.decode('utf-8')))
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            raise UpdateError('No public GitHub Release found.', code='no_release') from exc
        if exc.code == 401:
            raise UpdateError('GitHub authentication failed.', code='unauthorized') from exc
        if exc.code == 403:
            remaining = (exc.headers.get('X-RateLimit-Remaining', '') if exc.headers else '')
            reason = ''
            try:
                # Small bounded read; never expose the response body in UI.
                body = json.loads(exc.read(4096).decode('utf-8', errors='replace'))
                reason = str(body.get('message','')).lower() if isinstance(body, dict) else ''
            except (OSError, ValueError, UnicodeError):
                pass
            limited = remaining == '0' or 'rate limit' in reason or 'secondary limit' in reason
            detail = ''
            if limited and exc.headers:
                reset = exc.headers.get('X-RateLimit-Reset','')
                if reset.isdecimal():
                    try:
                        when = datetime.datetime.fromtimestamp(int(reset), datetime.timezone.utc)
                        detail = 'Reset time (UTC): ' + when.strftime('%Y-%m-%d %H:%M')
                    except (OverflowError, OSError, ValueError):
                        pass
            raise UpdateError('GitHub returned HTTP 403.',
                              code='rate_limited' if limited else 'forbidden', detail=detail) from exc
        raise UpdateError(f'GitHub returned HTTP {exc.code}.', code='http_error') from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        raise UpdateError(f'Unable to check GitHub releases: {exc}', code='network') from exc


def _detect_application_prefix(names: list[str]) -> str:
    candidates = [name[:-len('app.py')] for name in names if name.endswith('app.py')]
    for prefix in sorted(candidates, key=len):
        if prefix+'l4visual/ui/main_window.py' in names and prefix+'l4visual/codegen.py' in names:
            return prefix
    raise UpdateError('ZIP is not a L4D2 Visual VScript Editor application package.')


def list_install_files(archive: zipfile.ZipFile) -> list[tuple[zipfile.ZipInfo, str]]:
    infos = archive.infolist()
    if len(infos) > MAX_ENTRIES:
        raise UpdateError('Too many files in the update ZIP.')
    names = [info.filename for info in infos if not info.is_dir()]
    prefix = _detect_application_prefix(names)
    result = []
    total = 0
    seen = set()
    for info in infos:
        name = info.filename
        if '\\' in name or name.startswith('/') or '\x00' in name or re.match(r'^[A-Za-z]:', name):
            raise UpdateError('Unsafe path in update ZIP.')
        parts = PurePosixPath(name).parts
        if '..' in parts:
            raise UpdateError('Parent traversal in update ZIP.')
        if stat.S_IFMT(info.external_attr >> 16) == stat.S_IFLNK:
            raise UpdateError('Symlinks are not permitted in updates.')
        if info.is_dir() or not name.startswith(prefix):
            continue
        rel = name[len(prefix):]
        parts = PurePosixPath(rel).parts
        if rel.lower().endswith('.l4vp'):
            continue
        if not parts or (parts[0] not in ALLOWED_DIRS and rel not in ALLOWED_FILES and
                         not (len(parts) == 1 and rel.lower().endswith(('.md','.txt')))):
            # Never import project files, unknown executables, or user settings.
            continue
        if rel in seen:
            raise UpdateError('Duplicate application file in update ZIP.')
        seen.add(rel)
        total += info.file_size
        if total > MAX_UNPACKED_BYTES or info.file_size > MAX_DOWNLOAD_BYTES:
            raise UpdateError('Update ZIP expands beyond the safety limit.')
        result.append((info, rel))
    if not {'app.py','l4visual/ui/main_window.py','l4visual/codegen.py'}.issubset(seen):
        raise UpdateError('Update ZIP is missing core application files.')
    return result


def validate_update_archive(path: str | Path) -> int:
    try:
        with zipfile.ZipFile(path) as archive:
            files = list_install_files(archive)
            bad = archive.testzip()
            if bad:
                raise UpdateError(f'ZIP integrity check failed: {bad}')
            return len(files)
    except (zipfile.BadZipFile, OSError) as exc:
        raise UpdateError(f'Invalid update ZIP: {exc}') from exc


def download_release(info: ReleaseInfo, progress=None, cancelled=None) -> tuple[Path, Path]:
    if not info.asset_url:
        raise UpdateError('This release has no editor ZIP asset. Open the Release page instead.')
    if not trusted_download_url(info.asset_url):
        raise UpdateError('Untrusted release asset URL.')
    if info.asset_size > MAX_DOWNLOAD_BYTES:
        raise UpdateError('Release asset is larger than the permitted limit.')
    folder = Path(tempfile.mkdtemp(prefix='l4vp-upgrade-'))
    dest = folder / 'editor_update.zip'
    try:
        request = urllib.request.Request(info.asset_url, headers={
            'User-Agent':f'L4D2-Visual-VScript-Editor/{APP_VERSION}'})
        with _OPENER.open(request, timeout=25.0) as response, dest.open('wb') as out:
            length = response.headers.get('Content-Length')
            expected = int(length) if length and length.isdecimal() else info.asset_size
            if expected > MAX_DOWNLOAD_BYTES:
                raise UpdateError('Download is too large.')
            count = 0
            digest = hashlib.sha256()
            while True:
                if cancelled is not None and cancelled.is_set():
                    raise UpdateCancelled('Download cancelled.')
                chunk = response.read(256 * 1024)
                if not chunk:
                    break
                count += len(chunk)
                if count > MAX_DOWNLOAD_BYTES:
                    raise UpdateError('Download exceeded permitted size.')
                digest.update(chunk)
                out.write(chunk)
                if progress:
                    progress(count, expected)
        if info.asset_size and count != info.asset_size:
            raise UpdateError('Downloaded file size does not match GitHub release metadata.')
        if info.sha256 and digest.hexdigest() != info.sha256:
            raise UpdateError('SHA-256 does not match GitHub release digest.')
        validate_update_archive(dest)
        return dest, folder
    except Exception:
        shutil.rmtree(folder, ignore_errors=True)
        raise
