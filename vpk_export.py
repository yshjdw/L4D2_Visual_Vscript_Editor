"""Minimal single-file Valve VPK version 1 packer for L4D2 add-ons.

No external vpk.exe required. Archive data is stored in the directory archive
using archive index 0x7fff; suitable for modest generated VScript add-ons.
"""
from __future__ import annotations
import struct
import zlib
from pathlib import Path, PurePosixPath

MAGIC=0x55AA1234
AUTHOR_SUFFIX='/Vscript Visual Maker'

def author_credit(name: str) -> str:
    name=(name or '').strip()
    return name if name.endswith(AUTHOR_SUFFIX) else name+AUTHOR_SUFFIX

def _escape_kv(value: object) -> str:
    return str(value).replace('\\','\\\\').replace('"', '\\"').replace('\n','\\n').replace('\r','')

def addoninfo(name: str, author: str, version: str, description: str) -> str:
    return ('"AddonInfo"\n{\n'
            f'    "addonTitle" "{_escape_kv(name)}"\n'
            f'    "addonAuthor" "{_escape_kv(author_credit(author))}"\n'
            f'    "addonVersion" "{_escape_kv(version)}"\n'
            f'    "addonDescription" "{_escape_kv(description)}"\n'
            '}\n')

def _entry_name(path: str) -> tuple[str,str,str]:
    posix=PurePosixPath(path.replace('\\','/'))
    if posix.is_absolute() or '..' in posix.parts or not posix.name or posix.name.startswith('.'):
        raise ValueError('不合法的归档路径: '+path)
    name=posix.stem
    ext=posix.suffix[1:]
    folder=str(posix.parent)
    if not name or not ext:
        raise ValueError('文件必须有扩展名: '+path)
    return ext, folder if folder!='.' else ' ', name

def make_vpk(path: str | Path, files: dict[str, bytes]) -> Path:
    """Writes a Valve VPK v1 directory archive containing all payload bytes."""
    if not files:raise ValueError('不能创建空 VPK')
    tree_groups: dict[str,dict[str,list[tuple[str,bytes]]]]={}
    for path_name,data in files.items():
        if not isinstance(data,bytes):raise TypeError('VPK 文件内容必须是 bytes')
        ext,folder,name=_entry_name(path_name)
        bucket=tree_groups.setdefault(ext,{}).setdefault(folder,[])
        if any(n==name for n,_ in bucket):raise ValueError('重复的文件路径: '+path_name)
        bucket.append((name,data))
    tree=bytearray();body=bytearray()
    def cs(value):return value.encode('utf-8')+b'\0'
    for ext in sorted(tree_groups):
        tree+=cs(ext)
        for folder in sorted(tree_groups[ext]):
            tree+=cs(folder)
            for name,data in sorted(tree_groups[ext][folder]):
                tree+=cs(name)
                tree+=struct.pack('<IHHIIH',zlib.crc32(data)&0xffffffff,0,0x7fff,len(body),len(data),0xffff)
                body+=data
            tree+=b'\0'
        tree+=b'\0'
    tree+=b'\0'
    dest=Path(path);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(struct.pack('<III',MAGIC,1,len(tree))+tree+body)
    return dest

def package_scripts(path: str | Path, scripts: dict[str,str], *, title: str,author: str='',version: str='1.0',description: str='') -> Path:
    payload={'addoninfo.txt':addoninfo(title,author,version,description).encode('utf-8')}
    for name,source in scripts.items():
        normalized=PurePosixPath(name.replace('\\','/'))
        if normalized.is_absolute() or '..' in normalized.parts or normalized.suffix.lower()!='.nut':
            raise ValueError('不安全的 .nut 路径: '+name)
        payload['scripts/vscripts/'+str(normalized)]=source.encode('utf-8')
    return make_vpk(path,payload)
