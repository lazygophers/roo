"""
文件操作工具
"""
import os
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def extract_file_info(file_path: str) -> Dict[str, Any]:
    """提取文件基本信息"""
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    stat = file_path.stat()

    return {
        "name": file_path.name,
        "path": str(file_path.absolute()),
        "size": stat.st_size,
        "extension": file_path.suffix.lower(),
        "created_at": datetime.fromtimestamp(stat.st_ctime),
        "modified_at": datetime.fromtimestamp(stat.st_mtime)
    }


def validate_file_path(file_path: str) -> bool:
    """验证文件路径是否安全和有效"""
    try:
        path = Path(file_path).resolve()

        # 检查路径是否安全（不包含..等危险字符）
        if ".." in str(path):
            return False

        # 检查是否是文件
        if path.exists() and not path.is_file():
            return False

        return True
    except Exception:
        return False


def get_supported_extensions() -> set:
    """获取支持的文件扩展名"""
    return {'.txt', '.md', '.pdf', '.doc', '.docx', '.html', '.htm'}