"""
Tool Configuration Service
管理基于文件的工具配置系统，支持 GitHub API 等工具的配置文件管理
"""
import os
import json
import threading
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.config import PROJECT_ROOT

logger = setup_logging()


class ToolConfigService:
    """工具配置服务 - 基于文件的配置管理"""

    def __init__(self, config_dir: str = "data/mcp"):
        self.config_dir = Path(PROJECT_ROOT) / config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._config_cache: Dict[str, Dict[str, Any]] = {}
        logger.info(f"Tool config service initialized with directory: {self.config_dir}")

    def _get_config_file_path(self, tool_name: str) -> Path:
        """获取工具配置文件路径"""
        return self.config_dir / f"{tool_name}.json"

    def _load_config_from_file(self, tool_name: str) -> Dict[str, Any]:
        """从文件加载配置"""
        config_file = self._get_config_file_path(tool_name)

        if not config_file.exists():
            # 如果配置文件不存在，返回默认配置
            return self._get_default_config(tool_name)

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"Loaded {tool_name} config from file: {config_file}")
            return config
        except Exception as e:
            logger.error(f"Failed to load {tool_name} config from {config_file}: {e}")
            return self._get_default_config(tool_name)

    def _save_config_to_file(self, tool_name: str, config: Dict[str, Any]) -> bool:
        """保存配置到文件"""
        config_file = self._get_config_file_path(tool_name)

        try:
            # 更新时间戳
            config['last_updated'] = datetime.now().isoformat()

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {tool_name} config to file: {config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save {tool_name} config to {config_file}: {e}")
            return False

    def _get_default_config(self, tool_name: str) -> Dict[str, Any]:
        """获取工具的默认配置"""
        if tool_name == "github":
            return {
                "enabled": True,
                "api_base_url": "https://api.github.com",
                "timeout": 30,
                "retry_count": 3,
                "rate_limit": {
                    "enabled": True,
                    "max_requests_per_hour": 5000
                },
                "features": {
                    "repository_management": True,
                    "issue_management": True,
                    "pull_request_management": True,
                    "release_management": True,
                    "organization_access": True,
                    "gist_management": True
                },
                "security": {
                    "verify_ssl": True,
                    "log_api_calls": False,
                    "mask_sensitive_data": True
                },
                "cache": {
                    "enabled": True,
                    "ttl_seconds": 300,
                    "max_entries": 1000
                },
                "version": "1.0",
                "last_updated": None
            }
        elif tool_name == "file_tools":
            return {
                "enabled": True,
                "security": {
                    "allowed_operations": [
                        "read",
                        "write",
                        "list",
                        "create_directory",
                        "delete",
                        "move",
                        "copy"
                    ],
                    "allowed_extensions": [
                        ".txt",
                        ".md",
                        ".json",
                        ".yaml",
                        ".yml",
                        ".py",
                        ".js",
                        ".ts",
                        ".html",
                        ".css",
                        ".xml",
                        ".csv",
                        ".log"
                    ],
                    "blocked_paths": [
                        "/etc",
                        "/bin",
                        "/sbin",
                        "/usr/bin",
                        "/usr/sbin",
                        "/system",
                        "/windows",
                        "/program files"
                    ],
                    "allowed_base_paths": [
                        "/Users/luoxin/persons/knowledge/roo",
                        "/tmp",
                        "/var/tmp"
                    ],
                    "max_file_size_mb": 100,
                    "max_files_per_operation": 50,
                    "enable_path_traversal_protection": True,
                    "enable_symlink_protection": True,
                    "log_file_operations": True
                },
                "features": {
                    "file_compression": True,
                    "file_encryption": False,
                    "batch_operations": True,
                    "backup_before_modify": True,
                    "version_control_integration": False
                },
                "performance": {
                    "cache_enabled": True,
                    "cache_ttl_seconds": 300,
                    "concurrent_operations": 5,
                    "timeout_seconds": 30
                },
                "version": "1.0",
                "last_updated": None
            }
        elif tool_name == "time_tools":
            return {
                "enabled": True,
                "timezone": {
                    "default_timezone": "Asia/Shanghai",
                    "auto_detect": False,
                    "display_timezone_info": True,
                    "supported_timezones": [
                        "UTC",
                        "Asia/Shanghai",
                        "America/New_York",
                        "Europe/London",
                        "Asia/Tokyo",
                        "Australia/Sydney"
                    ]
                },
                "format": {
                    "default_format": "iso",
                    "available_formats": [
                        "iso",
                        "unix",
                        "formatted",
                        "relative"
                    ],
                    "custom_format_patterns": {
                        "date_only": "%Y-%m-%d",
                        "time_only": "%H:%M:%S",
                        "datetime": "%Y-%m-%d %H:%M:%S",
                        "full": "%A, %B %d, %Y at %H:%M:%S %Z"
                    }
                },
                "features": {
                    "duration_calculation": True,
                    "timezone_conversion": True,
                    "business_hours": {
                        "enabled": True,
                        "start_hour": 9,
                        "end_hour": 17,
                        "working_days": [1, 2, 3, 4, 5]
                    },
                    "holiday_detection": False,
                    "scheduling_helpers": True
                },
                "performance": {
                    "cache_timezone_data": True,
                    "cache_ttl_seconds": 3600,
                    "max_time_range_days": 365
                },
                "security": {
                    "prevent_time_manipulation": True,
                    "log_time_queries": False,
                    "rate_limit_per_minute": 60
                },
                "version": "1.0",
                "last_updated": None
            }
        elif tool_name == "cache_tools":
            return {
                "enabled": True,
                "version": "1.0",
                "last_updated": None,
                "backend": "diskcache",
                "description": "DiskCache 持久化缓存系统配置",

                # DiskCache 核心配置 - 直接对应 DiskCacheManager.__init__ 参数
                "cache_dir": "data/mcp/cache",          # 缓存目录路径
                "max_size_mb": 1024,                    # 缓存最大大小 (MB)
                "timeout_seconds": 10,                  # DiskCache 操作超时时间
                "auto_create_dirs": True,               # 自动创建目录

                # TTL 和过期配置
                "ttl": {
                    "default_ttl_seconds": 3600,        # 默认TTL (1小时)
                    "enable_ttl": True,                  # 启用TTL功能
                    "ttl_precision": "seconds",          # TTL精度
                    "max_ttl_seconds": 86400 * 7        # 最大TTL (7天)
                },

                # DiskCache 特性配置
                "diskcache": {
                    "eviction_policy": "least-recently-stored",  # DiskCache 默认淘汰策略
                    "disk_min_file_size": 32768,                  # 最小文件大小 (32KB)
                    "disk_pickle_protocol": 4,                    # Pickle 协议版本
                    "statistics": True,                           # 启用统计
                    "tag_index": False,                           # 标签索引 (高级功能)
                    "retry": True                                 # 重试机制
                },

                # 操作配置
                "operations": {
                    "thread_safe": True,                 # 线程安全 (固定为True)
                    "pattern_matching": "fnmatch",       # 模式匹配类型
                    "batch_operations": True,            # 支持批量操作
                    "atomic_operations": True            # 原子操作
                },

                # 安全和限制
                "limits": {
                    "max_key_length": 250,              # 最大键长度
                    "max_value_size_mb": 100,           # 最大值大小
                    "max_concurrent_operations": 10,    # 最大并发操作
                    "blocked_key_patterns": [           # 禁止的键模式
                        "password*",
                        "secret*",
                        "*token*",
                        "*key*",
                        "*credential*"
                    ]
                },

                # 监控和日志
                "monitoring": {
                    "enable_statistics": True,           # 启用统计信息
                    "log_operations": False,             # 记录操作日志
                    "log_performance": False,            # 记录性能日志
                    "metrics_collection": True,          # 收集指标
                    "health_check": True                 # 健康检查
                },

                # 性能优化
                "performance": {
                    "read_timeout": 5.0,                # 读取超时
                    "write_timeout": 10.0,              # 写入超时
                    "sync_frequency": "on_close",       # 同步频率
                    "cache_warmup": False               # 缓存预热
                }
            }
        else:
            return {
                "enabled": True,
                "version": "1.0",
                "last_updated": None
            }

    def get_config(self, tool_name: str, use_cache: bool = True) -> Dict[str, Any]:
        """获取工具配置"""
        with self._lock:
            # 检查缓存
            if use_cache and tool_name in self._config_cache:
                return self._config_cache[tool_name].copy()

            # 从文件加载配置
            config = self._load_config_from_file(tool_name)

            # 更新缓存
            self._config_cache[tool_name] = config.copy()

            return config.copy()

    def update_config(self, tool_name: str, updates: Dict[str, Any]) -> bool:
        """更新工具配置"""
        with self._lock:
            # 获取当前配置
            current_config = self.get_config(tool_name, use_cache=False)

            # 应用更新
            current_config.update(updates)

            # 保存到文件
            success = self._save_config_to_file(tool_name, current_config)

            if success:
                # 更新缓存
                self._config_cache[tool_name] = current_config.copy()
                logger.info(f"Updated {tool_name} config: {sanitize_for_log(list(updates.keys()))}")

            return success

    def set_config(self, tool_name: str, config: Dict[str, Any]) -> bool:
        """设置完整的工具配置"""
        with self._lock:
            # 保存到文件
            success = self._save_config_to_file(tool_name, config)

            if success:
                # 更新缓存
                self._config_cache[tool_name] = config.copy()
                logger.info(f"Set complete {tool_name} config")

            return success

    def delete_config(self, tool_name: str) -> bool:
        """删除工具配置文件"""
        with self._lock:
            config_file = self._get_config_file_path(tool_name)

            try:
                if config_file.exists():
                    config_file.unlink()
                    logger.info(f"Deleted {tool_name} config file: {config_file}")

                # 从缓存中移除
                if tool_name in self._config_cache:
                    del self._config_cache[tool_name]

                return True
            except Exception as e:
                logger.error(f"Failed to delete {tool_name} config file: {e}")
                return False

    def list_configs(self) -> Dict[str, Dict[str, Any]]:
        """列出所有工具配置"""
        configs = {}

        try:
            for config_file in self.config_dir.glob("*.json"):
                tool_name = config_file.stem
                configs[tool_name] = self.get_config(tool_name)
        except Exception as e:
            logger.error(f"Failed to list configs: {e}")

        return configs

    def config_exists(self, tool_name: str) -> bool:
        """检查工具配置文件是否存在"""
        config_file = self._get_config_file_path(tool_name)
        return config_file.exists()

    def get_config_file_info(self, tool_name: str) -> Dict[str, Any]:
        """获取配置文件信息"""
        config_file = self._get_config_file_path(tool_name)

        if not config_file.exists():
            return {
                "exists": False,
                "path": str(config_file),
                "size": 0,
                "modified": None
            }

        try:
            stat = config_file.stat()
            return {
                "exists": True,
                "path": str(config_file),
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to get file info for {tool_name}: {e}")
            return {
                "exists": True,
                "path": str(config_file),
                "size": 0,
                "modified": None,
                "error": str(e)
            }

    def clear_cache(self, tool_name: Optional[str] = None):
        """清除配置缓存"""
        with self._lock:
            if tool_name:
                if tool_name in self._config_cache:
                    del self._config_cache[tool_name]
                    logger.debug(f"Cleared cache for {tool_name}")
            else:
                self._config_cache.clear()
                logger.debug("Cleared all config cache")

    def reload_config(self, tool_name: str) -> Dict[str, Any]:
        """重新加载工具配置（忽略缓存）"""
        with self._lock:
            # 清除缓存
            if tool_name in self._config_cache:
                del self._config_cache[tool_name]

            # 重新加载
            return self.get_config(tool_name, use_cache=False)

    def backup_config(self, tool_name: str) -> Optional[str]:
        """备份工具配置文件"""
        config_file = self._get_config_file_path(tool_name)

        if not config_file.exists():
            logger.warning(f"Config file does not exist for backup: {tool_name}")
            return None

        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = config_file.with_suffix(f".backup.{timestamp}.json")

            import shutil
            shutil.copy2(config_file, backup_file)

            logger.info(f"Backed up {tool_name} config to: {backup_file}")
            return str(backup_file)
        except Exception as e:
            logger.error(f"Failed to backup {tool_name} config: {e}")
            return None

    def restore_config(self, tool_name: str, backup_file: str) -> bool:
        """从备份文件恢复工具配置"""
        backup_path = Path(backup_file)

        if not backup_path.exists():
            logger.error(f"Backup file does not exist: {backup_file}")
            return False

        try:
            config_file = self._get_config_file_path(tool_name)

            import shutil
            shutil.copy2(backup_path, config_file)

            # 清除缓存以强制重新加载
            self.clear_cache(tool_name)

            logger.info(f"Restored {tool_name} config from backup: {backup_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore {tool_name} config from backup: {e}")
            return False


# 全局工具配置服务实例
_tool_config_service: Optional[ToolConfigService] = None


def init_tool_config_service(config_dir: str = "data/mcp") -> ToolConfigService:
    """初始化工具配置服务"""
    global _tool_config_service
    if _tool_config_service is None:
        _tool_config_service = ToolConfigService(config_dir)
    return _tool_config_service


def get_tool_config_service() -> ToolConfigService:
    """获取工具配置服务单例"""
    global _tool_config_service
    if _tool_config_service is None:
        _tool_config_service = ToolConfigService()
    return _tool_config_service


def get_tool_config(tool_name: str) -> Dict[str, Any]:
    """获取工具配置的便捷函数"""
    return get_tool_config_service().get_config(tool_name)


def update_tool_config(tool_name: str, updates: Dict[str, Any]) -> bool:
    """更新工具配置的便捷函数"""
    return get_tool_config_service().update_config(tool_name, updates)