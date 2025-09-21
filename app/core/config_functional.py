"""
函数式配置服务

提供配置文件的读取、写入、验证和管理功能，使用纯函数实现
"""

import json
import threading
from typing import Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime

from app.core.functional_base import (
    Result, safe, pipe, merge_dicts, validate_config,
    transform_config, set_default_values, create_logger
)
from app.models.mcp_config import MCPGlobalConfig, EnvironmentType

# =============================================================================
# 配置文件操作
# =============================================================================

def read_config_file(file_path: Path) -> Result:
    """安全读取配置文件"""
    try:
        if not file_path.exists():
            return Result(error=FileNotFoundError(f"Config file not found: {file_path}"))

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return Result(value=data)
    except Exception as e:
        return Result(error=e)

def write_config_file(file_path: Path, config: Dict[str, Any]) -> Result:
    """安全写入配置文件"""
    try:
        # 确保目录存在
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 备份现有文件
        if file_path.exists():
            backup_path = file_path.with_suffix(f'.bak.{int(datetime.now().timestamp())}')
            file_path.rename(backup_path)

        # 写入新配置
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        return Result(value=config)
    except Exception as e:
        return Result(error=e)

def ensure_config_directory(config_path: Path) -> Result:
    """确保配置目录存在"""
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        return Result(value=config_path.parent)
    except Exception as e:
        return Result(error=e)

# =============================================================================
# 默认配置生成
# =============================================================================

def create_default_mcp_config() -> Dict[str, Any]:
    """创建默认MCP配置"""
    return MCPGlobalConfig().to_dict()

def create_default_database_config() -> Dict[str, Any]:
    """创建默认数据库配置"""
    return {
        'use_unified_db': True,
        'cache_ttl': 3600,
        'max_cache_size': 1000,
        'auto_cleanup': True
    }

def create_default_server_config() -> Dict[str, Any]:
    """创建默认服务器配置"""
    return {
        'host': '0.0.0.0',
        'port': 8000,
        'debug': False,
        'log_level': 'INFO',
        'cors_origins': ['*'],
        'cors_allow_credentials': True
    }

# =============================================================================
# 配置验证
# =============================================================================

def validate_mcp_config(config: Dict[str, Any]) -> Result:
    """验证MCP配置"""
    try:
        # 使用Pydantic模型验证
        validated_config = MCPGlobalConfig.from_dict(config)
        return Result(value=validated_config.to_dict())
    except Exception as e:
        return Result(error=e)

def validate_database_config(config: Dict[str, Any]) -> Result:
    """验证数据库配置"""
    schema = {
        'use_unified_db': bool,
        'cache_ttl': int,
        'max_cache_size': int,
        'auto_cleanup': bool
    }
    return validate_config(schema, config)

def validate_server_config(config: Dict[str, Any]) -> Result:
    """验证服务器配置"""
    schema = {
        'host': str,
        'port': int,
        'debug': bool,
        'log_level': str,
        'cors_origins': list,
        'cors_allow_credentials': bool
    }
    return validate_config(schema, config)

# =============================================================================
# 配置转换器
# =============================================================================

def normalize_mcp_config() -> Callable:
    """MCP配置规范化转换器"""
    def transformer(config: Dict[str, Any]) -> Dict[str, Any]:
        # 确保所有必需字段存在
        defaults = create_default_mcp_config()
        normalized = merge_dicts(defaults, config)

        # 特殊处理
        if 'environment' in normalized:
            if isinstance(normalized['environment'], str):
                normalized['environment'] = EnvironmentType(normalized['environment'])

        return normalized

    return transformer

def apply_environment_overrides(environment: str) -> Callable:
    """应用环境特定的配置覆盖"""
    def transformer(config: Dict[str, Any]) -> Dict[str, Any]:
        env_overrides = {}

        if environment == 'development':
            env_overrides = {
                'debug': True,
                'log_level': 'DEBUG'
            }
        elif environment == 'production':
            env_overrides = {
                'debug': False,
                'log_level': 'INFO'
            }

        return merge_dicts(config, env_overrides)

    return transformer

# =============================================================================
# 配置管理函数
# =============================================================================

def load_config(file_path: Path, default_factory: Callable = None,
               validators: Optional[list] = None,
               transformers: Optional[list] = None) -> Result:
    """加载配置文件"""
    logger = create_logger('config_loader')

    # 尝试读取文件
    result = read_config_file(file_path)

    if result.is_error and default_factory:
        # 使用默认配置
        config = default_factory()
        logger.info(f"Using default config for {file_path}")
    elif result.is_error:
        return result
    else:
        config = result.value

    # 应用验证器
    if validators:
        for validator in validators:
            validation_result = validator(config)
            if validation_result.is_error:
                return validation_result
            config = validation_result.value

    # 应用转换器
    if transformers:
        config = transform_config(transformers, config)

    return Result(value=config)

def save_config(file_path: Path, config: Dict[str, Any],
               validators: Optional[list] = None) -> Result:
    """保存配置文件"""
    # 验证配置
    if validators:
        for validator in validators:
            validation_result = validator(config)
            if validation_result.is_error:
                return validation_result

    # 写入文件
    return write_config_file(file_path, config)

def update_config(file_path: Path, updates: Dict[str, Any],
                 default_factory: Callable = None,
                 validators: Optional[list] = None,
                 transformers: Optional[list] = None) -> Result:
    """更新配置文件"""
    # 加载现有配置
    load_result = load_config(file_path, default_factory, validators, transformers)
    if load_result.is_error:
        return load_result

    current_config = load_result.value

    # 合并更新
    updated_config = merge_dicts(current_config, updates)

    # 应用转换器
    if transformers:
        updated_config = transform_config(transformers, updated_config)

    # 保存配置
    return save_config(file_path, updated_config, validators)

# =============================================================================
# 线程安全的配置管理器
# =============================================================================

def create_config_manager(file_path: Path, default_factory: Callable = None,
                         validators: Optional[list] = None,
                         transformers: Optional[list] = None) -> Dict[str, Any]:
    """创建配置管理器"""
    return {
        'file_path': file_path,
        'default_factory': default_factory,
        'validators': validators or [],
        'transformers': transformers or [],
        'lock': threading.RLock(),
        'cache': None,
        'logger': create_logger('config_manager')
    }

def get_config_from_manager(manager: Dict[str, Any], force_reload: bool = False) -> Result:
    """从管理器获取配置"""
    with manager['lock']:
        if manager['cache'] is None or force_reload:
            result = load_config(
                manager['file_path'],
                manager['default_factory'],
                manager['validators'],
                manager['transformers']
            )

            if result.is_success:
                manager['cache'] = result.value
                manager['logger'].debug(f"Config loaded from {manager['file_path']}")
            else:
                manager['logger'].error(f"Failed to load config: {result.error}")
                return result

        return Result(value=manager['cache'])

def update_config_in_manager(manager: Dict[str, Any], updates: Dict[str, Any]) -> Result:
    """更新管理器中的配置"""
    with manager['lock']:
        result = update_config(
            manager['file_path'],
            updates,
            manager['default_factory'],
            manager['validators'],
            manager['transformers']
        )

        if result.is_success:
            # 更新缓存
            manager['cache'] = result.value
            manager['logger'].info(f"Config updated: {manager['file_path']}")

        return result

def reset_config_in_manager(manager: Dict[str, Any]) -> Result:
    """重置管理器配置为默认值"""
    with manager['lock']:
        if not manager['default_factory']:
            return Result(error=ValueError("No default factory provided"))

        default_config = manager['default_factory']()
        return update_config_in_manager(manager, default_config)

# =============================================================================
# 预定义配置管理器
# =============================================================================

def create_mcp_config_manager(config_file: str = "data/mcp_config.json") -> Dict[str, Any]:
    """创建MCP配置管理器"""
    return create_config_manager(
        file_path=Path(config_file),
        default_factory=create_default_mcp_config,
        validators=[validate_mcp_config],
        transformers=[normalize_mcp_config()]
    )

def create_database_config_manager(config_file: str = "data/db_config.json") -> Dict[str, Any]:
    """创建数据库配置管理器"""
    return create_config_manager(
        file_path=Path(config_file),
        default_factory=create_default_database_config,
        validators=[validate_database_config]
    )

def create_server_config_manager(config_file: str = "data/server_config.json",
                                environment: str = "development") -> Dict[str, Any]:
    """创建服务器配置管理器"""
    return create_config_manager(
        file_path=Path(config_file),
        default_factory=create_default_server_config,
        validators=[validate_server_config],
        transformers=[apply_environment_overrides(environment)]
    )

# =============================================================================
# 配置同步函数
# =============================================================================

def sync_configs(source_manager: Dict[str, Any], target_manager: Dict[str, Any],
                keys_to_sync: Optional[list] = None) -> Result:
    """同步配置管理器之间的配置"""
    try:
        # 获取源配置
        source_result = get_config_from_manager(source_manager)
        if source_result.is_error:
            return source_result

        source_config = source_result.value

        # 选择要同步的键
        if keys_to_sync:
            sync_data = {k: source_config[k] for k in keys_to_sync if k in source_config}
        else:
            sync_data = source_config

        # 更新目标配置
        return update_config_in_manager(target_manager, sync_data)

    except Exception as e:
        return Result(error=e)

def backup_config(manager: Dict[str, Any], backup_dir: Path) -> Result:
    """备份配置文件"""
    try:
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = int(datetime.now().timestamp())
        backup_name = f"{manager['file_path'].stem}_{timestamp}.json"
        backup_path = backup_dir / backup_name

        # 获取当前配置
        config_result = get_config_from_manager(manager)
        if config_result.is_error:
            return config_result

        # 写入备份文件
        return write_config_file(backup_path, config_result.value)

    except Exception as e:
        return Result(error=e)

# =============================================================================
# 导出的高级API
# =============================================================================

# MCP配置API
def get_mcp_config(config_file: str = "data/mcp_config.json") -> Result:
    """获取MCP配置"""
    manager = create_mcp_config_manager(config_file)
    return get_config_from_manager(manager)

def update_mcp_config(updates: Dict[str, Any], config_file: str = "data/mcp_config.json") -> Result:
    """更新MCP配置"""
    manager = create_mcp_config_manager(config_file)
    return update_config_in_manager(manager, updates)

# 数据库配置API
def get_database_config(config_file: str = "data/db_config.json") -> Result:
    """获取数据库配置"""
    manager = create_database_config_manager(config_file)
    return get_config_from_manager(manager)

def update_database_config(updates: Dict[str, Any], config_file: str = "data/db_config.json") -> Result:
    """更新数据库配置"""
    manager = create_database_config_manager(config_file)
    return update_config_in_manager(manager, updates)

# 服务器配置API
def get_server_config(config_file: str = "data/server_config.json", environment: str = "development") -> Result:
    """获取服务器配置"""
    manager = create_server_config_manager(config_file, environment)
    return get_config_from_manager(manager)

def update_server_config(updates: Dict[str, Any], config_file: str = "data/server_config.json",
                        environment: str = "development") -> Result:
    """更新服务器配置"""
    manager = create_server_config_manager(config_file, environment)
    return update_config_in_manager(manager, updates)