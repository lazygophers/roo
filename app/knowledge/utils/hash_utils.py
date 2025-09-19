"""
哈希计算工具
"""
import hashlib
from pathlib import Path


def calculate_file_hash(file_path: str) -> str:
    """计算文件MD5哈希值"""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def calculate_content_hash(content: str) -> str:
    """计算内容MD5哈希值"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()