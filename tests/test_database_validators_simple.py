"""
简化的数据库验证器单元测试
Simplified Database Validators Unit Tests
"""

import pytest
import uuid
from app.core.database_validators import ValidationError, DatabaseValidator


class TestDatabaseValidator:
    """测试数据库验证器基类"""

    def test_validate_file_path_valid(self):
        """测试有效文件路径验证"""
        valid_paths = [
            "test.txt",
            "folder/test.txt",
            "config/settings.yaml",
            "data/models.json"
        ]

        for path in valid_paths:
            result = DatabaseValidator.validate_file_path(path)
            assert result == path.strip()

    def test_validate_file_path_invalid(self):
        """测试无效文件路径验证"""
        invalid_paths = [
            "",
            None,
            "/absolute/path",
            "../parent/path",
            "\\windows\\path",
            "folder/../escape",
            "a" * 300  # 超长路径
        ]

        for path in invalid_paths:
            with pytest.raises(ValidationError):
                DatabaseValidator.validate_file_path(path)

    def test_validate_md5_hash_valid(self):
        """测试有效MD5哈希值验证"""
        valid_hashes = [
            "5d41402abc4b2a76b9719d911017c592",
            "098f6bcd4621d373cade4e832627b4f6",
            "d41d8cd98f00b204e9800998ecf8427e"
        ]

        for hash_value in valid_hashes:
            result = DatabaseValidator.validate_md5_hash(hash_value)
            assert result == hash_value.lower()

    def test_validate_md5_hash_invalid(self):
        """测试无效MD5哈希值验证"""
        invalid_hashes = [
            "",
            None,
            "invalid",
            "5d41402abc4b2a76b9719d911017c59",  # 31位
            "5d41402abc4b2a76b9719d911017c592a",  # 33位
            "5d41402abc4b2a76b9719d911017c59g"  # 包含非法字符
        ]

        for hash_value in invalid_hashes:
            with pytest.raises(ValidationError):
                DatabaseValidator.validate_md5_hash(hash_value)

    def test_validate_uuid_valid(self):
        """测试有效UUID验证"""
        valid_uuids = [
            str(uuid.uuid4()),
            "550e8400-e29b-41d4-a716-446655440000",
            "6ba7b810-9dad-11d1-80b4-00c04fd430c8"
        ]

        for uuid_str in valid_uuids:
            result = DatabaseValidator.validate_uuid(uuid_str)
            assert result == uuid_str

    def test_validate_uuid_invalid(self):
        """测试无效UUID验证"""
        invalid_uuids = [
            "",
            None,
            "invalid-uuid",
            "550e8400-e29b-41d4-a716-44665544000",  # 少一位
            "550e8400-e29b-41d4-a716-44665544000g"  # 包含非法字符
        ]

        for uuid_str in invalid_uuids:
            with pytest.raises(ValidationError):
                DatabaseValidator.validate_uuid(uuid_str)

    def test_validate_json_object_basic(self):
        """测试基本JSON对象验证"""
        # 测试有效的字典对象
        valid_dict = {"key": "value", "number": 42}
        result = DatabaseValidator.validate_json_object(valid_dict)
        assert result == valid_dict

        # 测试None值
        result = DatabaseValidator.validate_json_object(None)
        assert result == {}

        # 测试有效的JSON字符串
        json_str = '{"key": "value"}'
        result = DatabaseValidator.validate_json_object(json_str)
        assert result == {"key": "value"}

    def test_validate_datetime_string(self):
        """测试日期时间字符串验证"""
        # 测试有效的ISO 8601格式
        valid_datetime = "2023-01-01T12:00:00"
        result = DatabaseValidator.validate_datetime_string(valid_datetime)
        assert result == valid_datetime

        # 测试无效格式
        with pytest.raises(ValidationError):
            DatabaseValidator.validate_datetime_string("invalid-date")

        with pytest.raises(ValidationError):
            DatabaseValidator.validate_datetime_string("")

        with pytest.raises(ValidationError):
            DatabaseValidator.validate_datetime_string(None)