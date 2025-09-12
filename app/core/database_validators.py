"""
数据库字段验证和约束工具
Database Field Validation and Constraints

提供统一的数据验证、字段约束和数据完整性检查功能
"""

import re
import uuid
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from pydantic import BaseModel, Field, validator
from app.core.logging import setup_logging

logger = setup_logging("INFO")

class ValidationError(Exception):
    """数据验证错误"""
    pass

class DatabaseValidator:
    """数据库验证器基类"""
    
    @staticmethod
    def validate_file_path(path: str, max_length: int = 255) -> str:
        """验证文件路径"""
        if not path or not isinstance(path, str):
            raise ValidationError("文件路径不能为空")
        
        if len(path) > max_length:
            raise ValidationError(f"文件路径长度不能超过 {max_length} 字符")
        
        # 检查路径格式（相对路径，不能包含 .. 等危险字符）
        if path.startswith('/') or '..' in path or path.startswith('\\'):
            raise ValidationError("文件路径必须是安全的相对路径")
        
        return path.strip()
    
    @staticmethod
    def validate_md5_hash(hash_value: str) -> str:
        """验证MD5哈希值"""
        if not hash_value or not isinstance(hash_value, str):
            raise ValidationError("MD5哈希值不能为空")
        
        if len(hash_value) != 32:
            raise ValidationError("MD5哈希值必须是32位字符串")
        
        if not re.match(r'^[a-f0-9]{32}$', hash_value.lower()):
            raise ValidationError("MD5哈希值格式无效")
        
        return hash_value.lower()
    
    @staticmethod
    def validate_uuid(uuid_str: str) -> str:
        """验证UUID格式"""
        if not uuid_str or not isinstance(uuid_str, str):
            raise ValidationError("UUID不能为空")
        
        try:
            uuid_obj = uuid.UUID(uuid_str)
            return str(uuid_obj)
        except ValueError:
            raise ValidationError("UUID格式无效")
    
    @staticmethod
    def validate_datetime_string(dt_str: str) -> str:
        """验证ISO 8601日期时间字符串"""
        if not dt_str or not isinstance(dt_str, str):
            raise ValidationError("日期时间字符串不能为空")
        
        try:
            datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
            return dt_str
        except ValueError:
            raise ValidationError("日期时间格式无效，必须是ISO 8601格式")
    
    @staticmethod
    def validate_json_object(json_data: Any) -> Dict:
        """验证JSON对象"""
        if json_data is None:
            return {}
        
        if isinstance(json_data, dict):
            return json_data
        
        if isinstance(json_data, str):
            try:
                return json.loads(json_data)
            except json.JSONDecodeError:
                raise ValidationError("JSON字符串格式无效")
        
        raise ValidationError("JSON对象必须是字典类型或有效的JSON字符串")
    
    @staticmethod
    def validate_json_array(json_data: Any) -> List:
        """验证JSON数组"""
        if json_data is None:
            return []
        
        if isinstance(json_data, list):
            return json_data
        
        if isinstance(json_data, str):
            try:
                data = json.loads(json_data)
                if isinstance(data, list):
                    return data
                else:
                    raise ValidationError("JSON字符串必须表示数组")
            except json.JSONDecodeError:
                raise ValidationError("JSON字符串格式无效")
        
        raise ValidationError("JSON数组必须是列表类型或有效的JSON数组字符串")
    
    @staticmethod
    def validate_enum_value(value: str, allowed_values: List[str], field_name: str = "字段") -> str:
        """验证枚举值"""
        if not value or not isinstance(value, str):
            raise ValidationError(f"{field_name}不能为空")
        
        if value not in allowed_values:
            raise ValidationError(f"{field_name}值无效，允许的值: {', '.join(allowed_values)}")
        
        return value
    
    @staticmethod
    def validate_string_length(value: str, max_length: int, field_name: str = "字段", min_length: int = 0) -> str:
        """验证字符串长度"""
        if value is None:
            value = ""
        
        if not isinstance(value, str):
            raise ValidationError(f"{field_name}必须是字符串类型")
        
        if len(value) < min_length:
            raise ValidationError(f"{field_name}长度不能少于 {min_length} 字符")
        
        if len(value) > max_length:
            raise ValidationError(f"{field_name}长度不能超过 {max_length} 字符")
        
        return value.strip()
    
    @staticmethod
    def validate_integer_range(value: int, min_value: int = None, max_value: int = None, field_name: str = "数值") -> int:
        """验证整数范围"""
        if not isinstance(value, int):
            raise ValidationError(f"{field_name}必须是整数类型")
        
        if min_value is not None and value < min_value:
            raise ValidationError(f"{field_name}不能小于 {min_value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name}不能大于 {max_value}")
        
        return value

class TableValidator:
    """表级别的验证器"""
    
    @staticmethod
    def validate_cache_file_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """验证缓存文件记录"""
        validator = DatabaseValidator()
        
        # 必填字段验证
        record['file_path'] = validator.validate_file_path(record.get('file_path'), 255)
        record['absolute_path'] = validator.validate_file_path(record.get('absolute_path'), 512)
        record['file_name'] = validator.validate_string_length(
            record.get('file_name'), 100, "文件名", 1
        )
        record['file_hash'] = validator.validate_md5_hash(record.get('file_hash'))
        record['file_size'] = validator.validate_integer_range(
            record.get('file_size', 0), 0, None, "文件大小"
        )
        record['last_modified'] = validator.validate_integer_range(
            record.get('last_modified'), 1, None, "最后修改时间"
        )
        record['scan_time'] = validator.validate_datetime_string(
            record.get('scan_time', datetime.now().isoformat())
        )
        record['content'] = validator.validate_json_object(record.get('content'))
        record['config_name'] = validator.validate_string_length(
            record.get('config_name'), 50, "配置名称", 1
        )
        
        return record
    
    @staticmethod
    def validate_mcp_tool_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """验证MCP工具记录"""
        validator = DatabaseValidator()
        
        # 生成或验证UUID
        if not record.get('id'):
            record['id'] = str(uuid.uuid4())
        else:
            record['id'] = validator.validate_uuid(record['id'])
        
        record['name'] = validator.validate_string_length(
            record.get('name'), 100, "工具名称", 1
        )
        record['description'] = validator.validate_string_length(
            record.get('description'), 500, "工具描述", 1
        )
        record['category'] = validator.validate_string_length(
            record.get('category'), 50, "工具分类", 1
        )
        
        # 验证实现类型
        record['implementation_type'] = validator.validate_enum_value(
            record.get('implementation_type', 'builtin'),
            ['builtin', 'external', 'plugin'],
            "实现类型"
        )
        
        record['schema'] = validator.validate_json_object(record.get('schema'))
        record['enabled'] = bool(record.get('enabled', True))
        
        # 设置时间戳
        current_time = datetime.now().isoformat()
        if not record.get('created_at'):
            record['created_at'] = current_time
        else:
            record['created_at'] = validator.validate_datetime_string(record['created_at'])
        
        record['updated_at'] = validator.validate_datetime_string(
            record.get('updated_at', current_time)
        )
        
        record['metadata'] = validator.validate_json_object(record.get('metadata'))
        
        return record
    
    @staticmethod
    def validate_security_paths_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """验证安全路径记录"""
        validator = DatabaseValidator()
        
        record['id'] = validator.validate_string_length(
            record.get('id'), 50, "配置ID", 1
        )
        record['config_type'] = validator.validate_enum_value(
            record.get('config_type'),
            ['readable', 'writable', 'deletable', 'forbidden'],
            "配置类型"
        )
        record['name'] = validator.validate_string_length(
            record.get('name'), 100, "配置名称", 1
        )
        record['description'] = validator.validate_string_length(
            record.get('description'), 500, "配置描述"
        )
        
        paths = validator.validate_json_array(record.get('paths'))
        if not paths:
            raise ValidationError("路径列表不能为空")
        record['paths'] = paths
        
        record['enabled'] = bool(record.get('enabled', True))
        
        # 设置时间戳
        current_time = datetime.now().isoformat()
        if not record.get('created_at'):
            record['created_at'] = current_time
        else:
            record['created_at'] = validator.validate_datetime_string(record['created_at'])
        
        record['updated_at'] = validator.validate_datetime_string(
            record.get('updated_at', current_time)
        )
        
        record['metadata'] = validator.validate_json_object(record.get('metadata'))
        
        return record
    
    @staticmethod
    def validate_security_limits_record(record: Dict[str, Any]) -> Dict[str, Any]:
        """验证安全限制记录"""
        validator = DatabaseValidator()
        
        record['id'] = validator.validate_string_length(
            record.get('id'), 50, "限制ID", 1
        )
        record['limit_type'] = validator.validate_enum_value(
            record.get('limit_type'),
            ['max_file_size', 'max_read_lines', 'strict_mode'],
            "限制类型"
        )
        record['name'] = validator.validate_string_length(
            record.get('name'), 100, "限制名称", 1
        )
        record['value'] = validator.validate_integer_range(
            record.get('value', 0), 0, None, "限制值"
        )
        record['description'] = validator.validate_string_length(
            record.get('description'), 500, "限制描述"
        )
        
        record['enabled'] = bool(record.get('enabled', True))
        
        # 设置时间戳
        current_time = datetime.now().isoformat()
        if not record.get('created_at'):
            record['created_at'] = current_time
        else:
            record['created_at'] = validator.validate_datetime_string(record['created_at'])
        
        record['updated_at'] = validator.validate_datetime_string(
            record.get('updated_at', current_time)
        )
        
        return record

class DatabaseConstraints:
    """数据库约束检查器"""
    
    def __init__(self, unified_db):
        self.db = unified_db
    
    def check_file_path_uniqueness(self, file_path: str, config_name: str, exclude_doc_id: int = None) -> bool:
        """检查文件路径唯一性"""
        from app.core.unified_database import TableNames
        
        table = self.db.get_table(TableNames.CACHE_FILES)
        from tinydb import Query
        q = Query()
        
        query = (q.file_path == file_path) & (q.config_name == config_name)
        if exclude_doc_id:
            query = query & (q.doc_id != exclude_doc_id)
        
        existing = table.search(query)
        return len(existing) == 0
    
    def check_tool_name_uniqueness(self, name: str, category: str, exclude_doc_id: int = None) -> bool:
        """检查工具名称在分类中的唯一性"""
        from app.core.unified_database import TableNames
        
        table = self.db.get_table(TableNames.MCP_TOOLS)
        from tinydb import Query
        q = Query()
        
        query = (q.name == name) & (q.category == category)
        if exclude_doc_id:
            query = query & (q.doc_id != exclude_doc_id)
        
        existing = table.search(query)
        return len(existing) == 0
    
    def check_category_exists(self, category_id: str) -> bool:
        """检查分类是否存在"""
        from app.core.unified_database import TableNames
        
        table = self.db.get_table(TableNames.MCP_CATEGORIES)
        from tinydb import Query
        q = Query()
        
        existing = table.search(q.id == category_id)
        return len(existing) > 0
    
    def validate_referential_integrity(self, table_name: str, record: Dict[str, Any]) -> List[str]:
        """验证引用完整性"""
        errors = []
        
        # MCP工具的分类引用检查
        if table_name == 'mcp_tools':
            category = record.get('category')
            if category and not self.check_category_exists(category):
                errors.append(f"分类 '{category}' 不存在")
        
        return errors

def create_table_validator(table_name: str) -> Optional[Callable]:
    """创建表验证器"""
    validators = {
        'cache_files': TableValidator.validate_cache_file_record,
        'models_cache': TableValidator.validate_cache_file_record,
        'hooks_cache': TableValidator.validate_cache_file_record,
        'rules_cache': TableValidator.validate_cache_file_record,
        'mcp_tools': TableValidator.validate_mcp_tool_record,
        'security_paths': TableValidator.validate_security_paths_record,
        'security_limits': TableValidator.validate_security_limits_record,
    }
    
    return validators.get(table_name)

def validate_record(table_name: str, record: Dict[str, Any]) -> Dict[str, Any]:
    """验证记录数据"""
    validator = create_table_validator(table_name)
    
    if validator:
        try:
            return validator(record)
        except ValidationError as e:
            logger.error(f"数据验证失败 ({table_name}): {e}")
            raise
        except Exception as e:
            logger.error(f"验证器异常 ({table_name}): {e}")
            raise ValidationError(f"数据验证过程中发生错误: {e}")
    else:
        logger.warning(f"表 {table_name} 没有对应的验证器")
        return record

# 示例用法和测试
if __name__ == "__main__":
    # 测试文件缓存记录验证
    test_record = {
        'file_path': 'resources/models/test.yaml',
        'absolute_path': '/Users/test/project/resources/models/test.yaml',
        'file_name': 'test.yaml',
        'file_hash': 'a1b2c3d4e5f6789012345678901234567890abcd',  # 错误的哈希长度，应该会失败
        'file_size': 1024,
        'last_modified': 1694505600,
        'content': {'slug': 'test-model'},
        'config_name': 'models'
    }
    
    try:
        validated = validate_record('cache_files', test_record)
        print("验证通过:", validated)
    except ValidationError as e:
        print("验证失败:", e)