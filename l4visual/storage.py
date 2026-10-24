import json
import os
import tempfile
import hashlib
import struct
import zlib
from pathlib import Path
from .models import Project

MAGIC = b'L4DVPROJ\x00\x01'
MAX_SIZE = 24 * 1024 * 1024


def save_project(path, project: Project):
    raw = json.dumps(project.to_dict(), ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf-8')
    if len(raw) > MAX_SIZE:
        raise ValueError('工程过大')
    payload = zlib.compress(raw, 9)
    blob = MAGIC + struct.pack('<II', len(raw), len(payload)) + hashlib.sha256(raw).digest() + payload
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', prefix='.l4vp-', suffix='.tmp',
                                         dir=destination.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(blob)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def load_project(path):
    binary = Path(path).read_bytes()
    header_size = len(MAGIC) + 8 + 32
    if not binary.startswith(MAGIC) or len(binary) < header_size:
        raise ValueError('这不是受支持的 .l4vp 工程文件')
    original_size, compressed_size = struct.unpack('<II', binary[len(MAGIC):len(MAGIC)+8])
    if original_size > MAX_SIZE or compressed_size > MAX_SIZE or len(binary) != header_size + compressed_size:
        raise ValueError('文件大小异常或工程已损坏')
    expected = binary[len(MAGIC)+8:header_size]
    decoder = zlib.decompressobj()
    raw = decoder.decompress(binary[header_size:], original_size + 1)
    if len(raw) != original_size or decoder.unconsumed_tail or not decoder.eof or decoder.unused_data:
        raise ValueError('压缩数据无效')
    if hashlib.sha256(raw).digest() != expected:
        raise ValueError('工程校验失败')
    return Project.from_dict(json.loads(raw.decode('utf-8')))
