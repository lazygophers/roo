"""
数据库验证器全面测试
目标：将database_validators.py的测试覆盖率从0%提升到95%+
涵盖数据验证、字段约束、表级验证等核心功能
"""
import pytest
import json
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

# 尝试导入模块
try:
    from app.core.database_validators import (
        ValidationError, DatabaseValidator, TableValidator
    )
    DATABASE_VALIDATORS_AVAILABLE = True
except ImportError as e:
    DATABASE_VALIDATORS_AVAILABLE = False
    print(f"Database validators import failed: {e}")


@pytest.mark.skipif(not DATABASE_VALIDATORS_AVAILABLE, reason="Database validators module not available")
class TestDatabaseValidatorsComprehensive:
    """数据库验证器全面测试套件"""

    # ==== ValidationError 测试 ====

    def test_validation_error_creation(self):
        """测试验证错误创建"""
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    # ==== DatabaseValidator 文件路径验证测试 ====

    def test_validate_file_path_valid(self):
        """测试有效文件路径验证"""
        valid_paths = [
            "models/test.yaml",
            "data/config.json",
            "resources/templates/template.txt",
            "simple.txt"
        ]

        for path in valid_paths:
            result = DatabaseValidator.validate_file_path(path)
            assert result == path

    def test_validate_file_path_empty(self):
        """测试空文件路径"""
        with pytest.raises(ValidationError, match="文件路径不能为空"):
            DatabaseValidator.validate_file_path("")

        with pytest.raises(ValidationError, match="文件路径不能为空"):
            DatabaseValidator.validate_file_path(None)

    def test_validate_file_path_non_string(self):
        """测试非字符串文件路径"""
        with pytest.raises(ValidationError, match="文件路径不能为空"):
            DatabaseValidator.validate_file_path(123)

        with pytest.raises(ValidationError, match="文件路径不能为空"):
            DatabaseValidator.validate_file_path([])

    def test_validate_file_path_too_long(self):
        """测试过长文件路径"""
        long_path = "a" * 300  # 超过默认255字符限制
        with pytest.raises(ValidationError, match="文件路径长度不能超过 255 字符"):
            DatabaseValidator.validate_file_path(long_path)

        # 自定义长度限制
        with pytest.raises(ValidationError, match="文件路径长度不能超过 100 字符"):
            DatabaseValidator.validate_file_path("a" * 150, max_length=100)

    def test_validate_file_path_dangerous_paths(self):
        """测试危险文件路径"""
        dangerous_paths = [
            "/absolute/path",
            "../parent/directory",
            "folder/../other",
            "\\windows\\path",
            "/etc/passwd",
            "..\\windows",
            "path\\..\\danger"
        ]

        for path in dangerous_paths:
            with pytest.raises(ValidationError, match="文件路径必须是安全的相对路径"):
                DatabaseValidator.validate_file_path(path)

    def test_validate_file_path_with_whitespace(self):
        """测试包含空白字符的文件路径"""
        path_with_whitespace = "  models/test.yaml  "
        result = DatabaseValidator.validate_file_path(path_with_whitespace)
        assert result == "models/test.yaml"  # 应该去除前后空白

    # ==== MD5哈希验证测试 ====

    def test_validate_md5_hash_valid(self):
        """测试有效MD5哈希"""
        valid_hashes = [
            "5d41402abc4b2a76b9719d911017c592",  # "hello"的MD5
            "098f6bcd4621d373cade4e832627b4f6",  # "test"的MD5
            "ABCDEF1234567890ABCDEF1234567890",  # 大写字母
            "abcdef1234567890abcdef1234567890"   # 小写字母
        ]

        for hash_value in valid_hashes:
            result = DatabaseValidator.validate_md5_hash(hash_value)
            assert result == hash_value.lower()  # 结果应该是小写

    def test_validate_md5_hash_empty(self):
        """测试空MD5哈希"""
        with pytest.raises(ValidationError, match="MD5哈希值不能为空"):
            DatabaseValidator.validate_md5_hash("")

        with pytest.raises(ValidationError, match="MD5哈希值不能为空"):
            DatabaseValidator.validate_md5_hash(None)

    def test_validate_md5_hash_non_string(self):
        """测试非字符串MD5哈希"""
        with pytest.raises(ValidationError, match="MD5哈希值不能为空"):
            DatabaseValidator.validate_md5_hash(123)

    def test_validate_md5_hash_wrong_length(self):
        """测试错误长度MD5哈希"""
        with pytest.raises(ValidationError, match="MD5哈希值必须是32位字符串"):
            DatabaseValidator.validate_md5_hash("abc123")  # 太短

        with pytest.raises(ValidationError, match="MD5哈希值必须是32位字符串"):
            DatabaseValidator.validate_md5_hash("a" * 40)  # 太长

    def test_validate_md5_hash_invalid_format(self):
        """测试无效格式MD5哈希"""
        invalid_hashes = [
            "g" * 32,  # 包含非16进制字符
            "123-456-789-abc-def-123-456-789",  # 包含连字符
            "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",  # 包含非16进制字符
            "12345678901234567890123456789012"   # 数字但包含无效字符
        ]

        for invalid_hash in invalid_hashes:
            with pytest.raises(ValidationError, match="MD5哈希值格式无效"):
                DatabaseValidator.validate_md5_hash(invalid_hash)

    # ==== UUID验证测试 ====

    def test_validate_uuid_valid(self):
        """测试有效UUID"""
        valid_uuids = [
            "550e8400-e29b-41d4-a716-446655440000",
            "123e4567-e89b-12d3-a456-426614174000",
            str(uuid.uuid4()),
            str(uuid.uuid1())
        ]

        for uuid_str in valid_uuids:
            result = DatabaseValidator.validate_uuid(uuid_str)
            assert result == uuid_str

    def test_validate_uuid_empty(self):
        """测试空UUID"""
        with pytest.raises(ValidationError, match="UUID不能为空"):
            DatabaseValidator.validate_uuid("")

        with pytest.raises(ValidationError, match="UUID不能为空"):
            DatabaseValidator.validate_uuid(None)

    def test_validate_uuid_non_string(self):
        """测试非字符串UUID"""
        with pytest.raises(ValidationError, match="UUID不能为空"):
            DatabaseValidator.validate_uuid(123)

    def test_validate_uuid_invalid_format(self):
        """测试无效UUID格式"""
        invalid_uuids = [
            "not-a-uuid",
            "123-456-789",
            "550e8400-e29b-41d4-a716",  # 太短
            "550e8400-e29b-41d4-a716-446655440000-extra",  # 太长
            "gggggggg-gggg-gggg-gggg-gggggggggggg"  # 无效字符
        ]

        for invalid_uuid in invalid_uuids:
            with pytest.raises(ValidationError, match="UUID格式无效"):
                DatabaseValidator.validate_uuid(invalid_uuid)

    # ==== 日期时间验证测试 ====

    def test_validate_datetime_string_valid(self):
        """测试有效日期时间字符串"""
        valid_datetimes = [
            "2023-12-25T10:30:00",
            "2023-12-25T10:30:00.123456",
            "2023-12-25T10:30:00Z",
            "2023-12-25T10:30:00+08:00",
            "2023-12-25T10:30:00-05:00",
            datetime.now().isoformat()
        ]

        for dt_str in valid_datetimes:
            result = DatabaseValidator.validate_datetime_string(dt_str)
            assert result == dt_str

    def test_validate_datetime_string_empty(self):
        """测试空日期时间字符串"""
        with pytest.raises(ValidationError, match="日期时间字符串不能为空"):
            DatabaseValidator.validate_datetime_string("")

        with pytest.raises(ValidationError, match="日期时间字符串不能为空"):
            DatabaseValidator.validate_datetime_string(None)

    def test_validate_datetime_string_non_string(self):
        """测试非字符串日期时间"""
        with pytest.raises(ValidationError, match="日期时间字符串不能为空"):
            DatabaseValidator.validate_datetime_string(123)

    def test_validate_datetime_string_invalid_format(self):
        """测试无效日期时间格式"""
        invalid_datetimes = [
            "not-a-date",
            "2023-13-25T10:30:00",  # 无效月份
            "2023-12-32T10:30:00",  # 无效日期
            "2023-12-25T25:30:00",  # 无效小时
            "2023/12/25 10:30:00",  # 错误格式
            "25-12-2023T10:30:00"   # 错误格式
        ]

        for invalid_dt in invalid_datetimes:
            with pytest.raises(ValidationError, match="日期时间格式无效"):
                DatabaseValidator.validate_datetime_string(invalid_dt)

    # ==== JSON对象验证测试 ====

    def test_validate_json_object_dict(self):
        """测试字典类型JSON对象"""
        test_dict = {"key": "value", "number": 123}
        result = DatabaseValidator.validate_json_object(test_dict)
        assert result == test_dict

    def test_validate_json_object_none(self):
        """测试None值JSON对象"""
        result = DatabaseValidator.validate_json_object(None)
        assert result == {}

    def test_validate_json_object_valid_string(self):
        """测试有效JSON字符串"""
        json_strings = [
            '{"key": "value"}',
            '{"numbers": [1, 2, 3]}',
            '{}',
            '{"nested": {"object": true}}'
        ]

        for json_str in json_strings:
            expected = json.loads(json_str)
            result = DatabaseValidator.validate_json_object(json_str)
            assert result == expected

    def test_validate_json_object_invalid_string(self):
        """测试无效JSON字符串"""
        invalid_json_strings = [
            "not json",
            "{key: value}",  # 无引号
            '{"key": }',     # 不完整
            '{"key": "value",}'  # 尾随逗号在某些情况下无效
        ]

        for invalid_json in invalid_json_strings:
            with pytest.raises(ValidationError, match="JSON字符串格式无效"):
                DatabaseValidator.validate_json_object(invalid_json)

    def test_validate_json_object_wrong_type(self):
        """测试错误类型JSON对象"""
        with pytest.raises(ValidationError, match="JSON对象必须是字典类型或有效的JSON字符串"):
            DatabaseValidator.validate_json_object(123)

        with pytest.raises(ValidationError, match="JSON对象必须是字典类型或有效的JSON字符串"):
            DatabaseValidator.validate_json_object([1, 2, 3])

    # ==== JSON数组验证测试 ====

    def test_validate_json_array_list(self):
        """测试列表类型JSON数组"""
        test_list = [1, 2, 3, "test"]
        result = DatabaseValidator.validate_json_array(test_list)
        assert result == test_list

    def test_validate_json_array_none(self):
        """测试None值JSON数组"""
        result = DatabaseValidator.validate_json_array(None)
        assert result == []

    def test_validate_json_array_valid_string(self):
        """测试有效JSON数组字符串"""
        json_arrays = [
            '[1, 2, 3]',
            '["a", "b", "c"]',
            '[]',
            '[{"key": "value"}]'
        ]

        for json_str in json_arrays:
            expected = json.loads(json_str)
            result = DatabaseValidator.validate_json_array(json_str)
            assert result == expected

    def test_validate_json_array_string_not_array(self):
        """测试JSON字符串但不是数组"""
        with pytest.raises(ValidationError, match="JSON字符串必须表示数组"):
            DatabaseValidator.validate_json_array('{"key": "value"}')

    def test_validate_json_array_invalid_string(self):
        """测试无效JSON数组字符串"""
        with pytest.raises(ValidationError, match="JSON字符串格式无效"):
            DatabaseValidator.validate_json_array("[1, 2, 3")  # 不完整

    def test_validate_json_array_wrong_type(self):
        """测试错误类型JSON数组"""
        with pytest.raises(ValidationError, match="JSON数组必须是列表类型或有效的JSON数组字符串"):
            DatabaseValidator.validate_json_array(123)

        with pytest.raises(ValidationError, match="JSON数组必须是列表类型或有效的JSON数组字符串"):
            DatabaseValidator.validate_json_array({"key": "value"})

    # ==== 枚举值验证测试 ====

    def test_validate_enum_value_valid(self):
        """测试有效枚举值"""
        allowed_values = ["option1", "option2", "option3"]

        for value in allowed_values:
            result = DatabaseValidator.validate_enum_value(value, allowed_values)
            assert result == value

    def test_validate_enum_value_empty(self):
        """测试空枚举值"""
        allowed_values = ["option1", "option2"]

        with pytest.raises(ValidationError, match="字段不能为空"):
            DatabaseValidator.validate_enum_value("", allowed_values)

        with pytest.raises(ValidationError, match="字段不能为空"):
            DatabaseValidator.validate_enum_value(None, allowed_values)

    def test_validate_enum_value_non_string(self):
        """测试非字符串枚举值"""
        allowed_values = ["option1", "option2"]

        with pytest.raises(ValidationError, match="字段不能为空"):
            DatabaseValidator.validate_enum_value(123, allowed_values)

    def test_validate_enum_value_invalid(self):
        """测试无效枚举值"""
        allowed_values = ["option1", "option2", "option3"]

        with pytest.raises(ValidationError, match="字段值无效，允许的值: option1, option2, option3"):
            DatabaseValidator.validate_enum_value("invalid_option", allowed_values)

    def test_validate_enum_value_custom_field_name(self):
        """测试自定义字段名的枚举值验证"""
        allowed_values = ["red", "green", "blue"]

        with pytest.raises(ValidationError, match="颜色不能为空"):
            DatabaseValidator.validate_enum_value("", allowed_values, "颜色")

        with pytest.raises(ValidationError, match="颜色值无效，允许的值: red, green, blue"):
            DatabaseValidator.validate_enum_value("yellow", allowed_values, "颜色")

    # ==== 字符串长度验证测试 ====

    def test_validate_string_length_valid(self):
        """测试有效字符串长度"""
        result = DatabaseValidator.validate_string_length("test", 10)
        assert result == "test"

        result = DatabaseValidator.validate_string_length("  test  ", 10)
        assert result == "test"  # 应该去除前后空白

    def test_validate_string_length_none_to_empty(self):
        """测试None值转为空字符串"""
        result = DatabaseValidator.validate_string_length(None, 10)
        assert result == ""

    def test_validate_string_length_non_string(self):
        """测试非字符串类型"""
        with pytest.raises(ValidationError, match="字段必须是字符串类型"):
            DatabaseValidator.validate_string_length(123, 10)

    def test_validate_string_length_too_short(self):
        """测试字符串太短"""
        with pytest.raises(ValidationError, match="字段长度不能少于 5 字符"):
            DatabaseValidator.validate_string_length("abc", 10, min_length=5)

    def test_validate_string_length_too_long(self):
        """测试字符串太长"""
        with pytest.raises(ValidationError, match="字段长度不能超过 5 字符"):
            DatabaseValidator.validate_string_length("abcdefgh", 5)

    def test_validate_string_length_custom_field_name(self):
        """测试自定义字段名的字符串长度验证"""
        with pytest.raises(ValidationError, match="用户名必须是字符串类型"):
            DatabaseValidator.validate_string_length(123, 10, "用户名")

        with pytest.raises(ValidationError, match="用户名长度不能超过 5 字符"):
            DatabaseValidator.validate_string_length("username", 5, "用户名")

    # ==== 整数范围验证测试 ====

    def test_validate_integer_range_valid(self):
        """测试有效整数范围"""
        result = DatabaseValidator.validate_integer_range(5)
        assert result == 5

        result = DatabaseValidator.validate_integer_range(10, min_value=1, max_value=20)
        assert result == 10

    def test_validate_integer_range_non_integer(self):
        """测试非整数类型"""
        with pytest.raises(ValidationError, match="数值必须是整数类型"):
            DatabaseValidator.validate_integer_range("123")

        with pytest.raises(ValidationError, match="数值必须是整数类型"):
            DatabaseValidator.validate_integer_range(12.5)

    def test_validate_integer_range_too_small(self):
        """测试整数太小"""
        with pytest.raises(ValidationError, match="数值不能小于 10"):
            DatabaseValidator.validate_integer_range(5, min_value=10)

    def test_validate_integer_range_too_large(self):
        """测试整数太大"""
        with pytest.raises(ValidationError, match="数值不能大于 20"):
            DatabaseValidator.validate_integer_range(25, max_value=20)

    def test_validate_integer_range_custom_field_name(self):
        """测试自定义字段名的整数范围验证"""
        with pytest.raises(ValidationError, match="年龄必须是整数类型"):
            DatabaseValidator.validate_integer_range("25", field_name="年龄")

        with pytest.raises(ValidationError, match="年龄不能小于 18"):
            DatabaseValidator.validate_integer_range(15, min_value=18, field_name="年龄")

    # ==== TableValidator 测试 ====

    def test_validate_cache_file_record_valid(self):
        """测试有效缓存文件记录验证"""
        valid_record = {
            'file_path': 'models/test.yaml',
            'absolute_path': 'project/models/test.yaml',
            'file_name': 'test.yaml',
            'file_hash': '5d41402abc4b2a76b9719d911017c592',
            'file_size': 1024,
            'last_modified': 1640995200,
            'scan_time': '2023-12-25T10:30:00',
            'content': '{"key": "value"}',
            'config_name': 'test_config'
        }

        result = TableValidator.validate_cache_file_record(valid_record)

        assert result['file_path'] == 'models/test.yaml'
        assert result['file_name'] == 'test.yaml'
        assert result['file_hash'] == '5d41402abc4b2a76b9719d911017c592'
        assert result['file_size'] == 1024
        assert result['content'] == {"key": "value"}

    def test_validate_cache_file_record_missing_fields(self):
        """测试缺少必填字段的缓存文件记录"""
        incomplete_record = {
            'file_name': 'test.yaml',
            'file_size': 1024
        }

        with pytest.raises(ValidationError):
            TableValidator.validate_cache_file_record(incomplete_record)

    def test_validate_cache_file_record_invalid_fields(self):
        """测试无效字段的缓存文件记录"""
        invalid_record = {
            'file_path': '../dangerous/path',  # 危险路径
            'absolute_path': 'project/models/test.yaml',
            'file_name': '',  # 空文件名
            'file_hash': 'invalid_hash',  # 无效哈希
            'file_size': -1,  # 负数大小
            'last_modified': 0,  # 无效时间
            'scan_time': 'invalid_date',
            'content': 'invalid json',
            'config_name': ''  # 空配置名
        }

        with pytest.raises(ValidationError):
            TableValidator.validate_cache_file_record(invalid_record)

    def test_validate_mcp_tool_record_without_id(self):
        """测试没有ID的MCP工具记录验证"""
        record_without_id = {
            'name': 'test_tool',
            'description': 'Test tool description'
        }

        result = TableValidator.validate_mcp_tool_record(record_without_id)

        # 应该自动生成UUID
        assert 'id' in result
        assert len(result['id']) == 36  # UUID长度
        assert '-' in result['id']  # UUID格式

    def test_validate_mcp_tool_record_with_id(self):
        """测试有ID的MCP工具记录验证"""
        test_uuid = str(uuid.uuid4())
        record_with_id = {
            'id': test_uuid,
            'name': 'test_tool',
            'description': 'Test tool description'
        }

        result = TableValidator.validate_mcp_tool_record(record_with_id)

        assert result['id'] == test_uuid

    def test_validate_mcp_tool_record_invalid_id(self):
        """测试无效ID的MCP工具记录验证"""
        record_invalid_id = {
            'id': 'invalid-uuid',
            'name': 'test_tool'
        }

        with pytest.raises(ValidationError, match="UUID格式无效"):
            TableValidator.validate_mcp_tool_record(record_invalid_id)

    # ==== 边界条件和特殊情况测试 ====

    def test_edge_cases_empty_allowed_values(self):
        """测试空的允许值列表"""
        with pytest.raises(ValidationError, match="字段值无效，允许的值: "):
            DatabaseValidator.validate_enum_value("any_value", [])

    def test_edge_cases_zero_length_constraints(self):
        """测试零长度约束"""
        # 最小长度为0应该允许空字符串
        result = DatabaseValidator.validate_string_length("", 10, min_length=0)
        assert result == ""

        # 最大长度为0应该只允许空字符串
        result = DatabaseValidator.validate_string_length("", 0, min_length=0)
        assert result == ""

        with pytest.raises(ValidationError):
            DatabaseValidator.validate_string_length("a", 0)

    def test_edge_cases_extreme_integer_values(self):
        """测试极值整数"""
        # 测试极大值
        large_int = 2**31 - 1
        result = DatabaseValidator.validate_integer_range(large_int)
        assert result == large_int

        # 测试极小值
        small_int = -(2**31)
        result = DatabaseValidator.validate_integer_range(small_int)
        assert result == small_int

    def test_performance_with_large_data(self):
        """测试大数据量性能"""
        # 测试大JSON对象
        large_dict = {f"key_{i}": f"value_{i}" for i in range(1000)}
        result = DatabaseValidator.validate_json_object(large_dict)
        assert len(result) == 1000

        # 测试大JSON数组
        large_list = [f"item_{i}" for i in range(1000)]
        result = DatabaseValidator.validate_json_array(large_list)
        assert len(result) == 1000

        # 测试长字符串
        long_string = "a" * 10000
        result = DatabaseValidator.validate_string_length(long_string, 20000)
        assert result == long_string