import os
import shutil
import tempfile
from pathlib import Path

import pytest

from src.tools.file_operations import (
    copy_file,
    create_directory,
    get_file_metadata,
    move_file,
)


class TestFileOperations:
    def test_create_directory_success(self, tmp_path: Path):
        """测试成功创建目录"""
        new_dir = tmp_path / "new_dir"
        result = create_directory(str(new_dir))
        assert new_dir.exists()
        assert new_dir.is_dir()
        assert result == {"status": "success", "directory_path": str(new_dir)}

    def test_create_directory_already_exists(self, tmp_path: Path):
        """测试创建已存在的目录"""
        existing_dir = tmp_path / "existing_dir"
        existing_dir.mkdir()
        result = create_directory(str(existing_dir))
        assert result["status"] == "error"
        assert "already exists" in result["message"]

    def test_create_directory_permission_denied(self):
        """测试无权限创建目录"""
        # 在一个已知无权限的路径尝试创建目录
        # 注意：此测试在 root 用户下可能会失败
        if os.geteuid() == 0:
            pytest.skip("Cannot test permission errors as root")
            
        # 我们期望函数能捕获异常并返回一个错误字典
        result = create_directory("/permission_denied_dir")
        assert result["status"] == "error"
        # 检查更具体的、跨平台更可能一致的错误信息
        assert "Read-only file system" in result["message"]

    def test_move_file_success(self, tmp_path: Path):
        """测试成功移动文件"""
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_file = dest_dir / "dest.txt"
        
        result = move_file(str(source_file), str(dest_file))
        
        assert not source_file.exists()
        assert dest_file.exists()
        assert dest_file.read_text() == "content"
        assert result == {"status": "success", "destination_path": str(dest_file)}

    def test_move_file_source_not_found(self, tmp_path: Path):
        """测试源文件不存在"""
        source_file = tmp_path / "non_existent.txt"
        dest_file = tmp_path / "dest.txt"
        
        result = move_file(str(source_file), str(dest_file))
        
        assert result["status"] == "error"
        assert "Source file not found" in result["message"]

    def test_move_file_destination_exists(self, tmp_path: Path):
        """测试目标文件已存在"""
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")
        dest_file = tmp_path / "dest.txt"
        dest_file.write_text("existing content")
        
        result = move_file(str(source_file), str(dest_file))
        
        assert result["status"] == "error"
        assert "Destination already exists" in result["message"]

    def test_get_file_metadata_success(self, tmp_path: Path):
        """测试成功获取文件元数据"""
        file_path = tmp_path / "test_file.txt"
        file_path.write_text("hello")
        
        result = get_file_metadata(str(file_path))
        
        assert result["status"] == "success"
        assert result["metadata"]["file_path"] == str(file_path)
        assert result["metadata"]["size_bytes"] == 5
        assert "last_modified_time" in result["metadata"]
        assert "created_time" in result["metadata"]

    def test_get_file_metadata_not_found(self, tmp_path: Path):
        """测试文件不存在时获取元数据"""
        file_path = tmp_path / "non_existent.txt"
        
        result = get_file_metadata(str(file_path))
        
        assert result["status"] == "error"
        assert "File not found" in result["message"]

    def test_copy_file_success(self, tmp_path: Path):
        """测试成功复制文件"""
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")
        dest_dir = tmp_path / "dest"
        dest_dir.mkdir()
        dest_file = dest_dir / "dest.txt"
        
        result = copy_file(str(source_file), str(dest_file))
        
        assert source_file.exists()
        assert dest_file.exists()
        assert dest_file.read_text() == "content"
        assert result == {"status": "success", "destination_path": str(dest_file)}

    def test_copy_file_source_not_found(self, tmp_path: Path):
        """测试源文件不存在"""
        source_file = tmp_path / "non_existent.txt"
        dest_file = tmp_path / "dest.txt"
        
        result = copy_file(str(source_file), str(dest_file))
        
        assert result["status"] == "error"
        assert "Source file not found" in result["message"]

    def test_copy_file_destination_exists(self, tmp_path: Path):
        """测试目标文件已存在"""
        source_file = tmp_path / "source.txt"
        source_file.write_text("content")
        dest_file = tmp_path / "dest.txt"
        dest_file.write_text("existing content")
        
        result = copy_file(str(source_file), str(dest_file))
        
        assert result["status"] == "error"
        assert "Destination already exists" in result["message"]