"""
缓存工具集服务 v2
Cache Tools Service v2

支持多种存储后端：TinyDB、DiskCache、Memcached、LMDB
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import threading
import logging

from app.core.unified_database import get_unified_database, TableNames
from app.core.secure_logging import sanitize_for_log
from app.core.cache_backends import create_cache_backend, CacheBackend
from tinydb import Query

logger = logging.getLogger(__name__)

@dataclass
class CacheToolsConfig:
    """缓存工具配置模型"""
    config_type: str
    name: str
    value: Any
    description: str


class CacheToolsService:
    """缓存工具服务类 - 支持多种存储后端"""

    def __init__(self, use_unified_db: bool = True, backend_type: str = "tinydb", backend_config: Optional[Dict[str, Any]] = None):
        """初始化缓存工具服务"""
        self.use_unified_db = use_unified_db
        self._cache_lock = threading.RLock()  # 线程安全锁
        self.backend_type = backend_type
        self.backend_config = backend_config or {}

        # 初始化配置表（仅在使用统一数据库时）
        if use_unified_db:
            self.unified_db = get_unified_database()
            self.config_table = self.unified_db.get_table(TableNames.CACHE_CONFIG)

        # 创建缓存后端
        self._initialize_backend()

        logger.info(f"CacheToolsService v2 initialized with backend: {backend_type}")

        # 初始化默认配置和启动后台任务
        self._initialize_default_config()
        self._start_background_tasks()

    def _initialize_backend(self):
        """初始化缓存后端"""
        try:
            # 合并默认配置和用户配置
            config = {
                'default_ttl': self._get_config_value("default_ttl", 3600),
                **self.backend_config
            }

            # 为不同后端设置特定默认值
            if self.backend_type == 'diskcache':
                config.setdefault('directory', './cache')
                config.setdefault('size_limit', 1024**3)  # 1GB
            elif self.backend_type == 'memcached':
                config.setdefault('host', 'localhost')
                config.setdefault('port', 11211)
            elif self.backend_type == 'lmdb':
                config.setdefault('path', './lmdb_cache')
                config.setdefault('map_size', 1024**3)  # 1GB

            self.backend: CacheBackend = create_cache_backend(self.backend_type, config)
            logger.info(f"Cache backend '{self.backend_type}' initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize cache backend '{self.backend_type}': {sanitize_for_log(str(e))}")
            # 回退到TinyDB后端
            logger.info("Falling back to TinyDB backend")
            self.backend_type = 'tinydb'
            config = {'default_ttl': self._get_config_value("default_ttl", 3600)}
            self.backend = create_cache_backend('tinydb', config)

    def _initialize_default_config(self):
        """初始化默认缓存配置"""
        if not self.use_unified_db:
            return

        try:
            default_configs = [
                CacheToolsConfig(
                    config_type="default_ttl",
                    name="默认过期时间",
                    value=3600,  # 1小时
                    description="缓存项的默认生存时间（秒）"
                ),
                CacheToolsConfig(
                    config_type="persistence_enabled",
                    name="启用持久化",
                    value=True,
                    description="是否将缓存数据持久化到数据库"
                ),
                CacheToolsConfig(
                    config_type="compression_enabled",
                    name="启用压缩",
                    value=False,
                    description="是否启用数据压缩"
                ),
                CacheToolsConfig(
                    config_type="stats_enabled",
                    name="启用统计",
                    value=True,
                    description="是否收集统计信息"
                ),
                CacheToolsConfig(
                    config_type="backend_type",
                    name="存储后端类型",
                    value=self.backend_type,
                    description="当前使用的存储后端类型"
                )
            ]

            # 检查并插入缺少的配置项
            for config in default_configs:
                existing = self.config_table.search(Query().config_type == config.config_type)
                if not existing:
                    config_dict = {
                        'config_type': config.config_type,
                        'name': config.name,
                        'value': config.value,
                        'description': config.description,
                        'created_at': datetime.now().isoformat(),
                        'updated_at': datetime.now().isoformat()
                    }
                    self.config_table.insert(config_dict)

            logger.info("Default cache configurations initialized")

        except Exception as e:
            logger.error(f"Failed to initialize default config: {sanitize_for_log(str(e))}")

    def _start_background_tasks(self):
        """启动后台任务"""
        try:
            # 只为支持清理的后端启动清理任务
            if hasattr(self.backend, 'cleanup_expired'):
                cleanup_interval = 300  # 5分钟
                threading.Timer(cleanup_interval, self._cleanup_expired_items).start()
                logger.info(f"Started cache cleanup task with interval: {cleanup_interval}s")
        except Exception as e:
            logger.error(f"Failed to start background tasks: {sanitize_for_log(str(e))}")

    def _cleanup_expired_items(self):
        """清理过期的缓存项"""
        try:
            with self._cache_lock:
                # 使用后端的清理方法
                if hasattr(self.backend, 'cleanup_expired'):
                    expired_count = self.backend.cleanup_expired()
                    if expired_count > 0:
                        logger.info(f"Cleaned up {expired_count} expired cache items")

                # 重新调度下次清理（固定5分钟间隔）
                cleanup_interval = 300  # 5分钟
                threading.Timer(cleanup_interval, self._cleanup_expired_items).start()

        except Exception as e:
            logger.error(f"Failed to cleanup expired items: {sanitize_for_log(str(e))}")

    def _get_config_value(self, config_type: str, default_value: Any) -> Any:
        """获取配置值"""
        if not self.use_unified_db:
            return default_value

        try:
            result = self.config_table.search(Query().config_type == config_type)
            if result:
                return result[0]['value']
            return default_value
        except Exception as e:
            logger.error(f"Failed to get config value for {config_type}: {sanitize_for_log(str(e))}")
            return default_value

    def set_config_value(self, config_type: str, value: Any) -> bool:
        """设置配置值"""
        if not self.use_unified_db:
            return False

        try:
            existing = self.config_table.search(Query().config_type == config_type)
            if existing:
                self.config_table.update(
                    {'value': value, 'updated_at': datetime.now().isoformat()},
                    Query().config_type == config_type
                )
            else:
                config_dict = {
                    'config_type': config_type,
                    'name': config_type,
                    'value': value,
                    'description': f"Configuration for {config_type}",
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
                self.config_table.insert(config_dict)
            return True
        except Exception as e:
            logger.error(f"Failed to set config value for {config_type}: {sanitize_for_log(str(e))}")
            return False

    def get_backend_type(self) -> str:
        """获取当前存储后端类型"""
        return self.backend_type

    def switch_backend(self, backend_type: str, backend_config: Optional[Dict[str, Any]] = None) -> bool:
        """切换存储后端"""
        try:
            old_backend_type = self.backend_type
            old_backend = self.backend

            # 尝试初始化新后端
            self.backend_type = backend_type
            self.backend_config = backend_config or {}
            self._initialize_backend()

            # 更新配置
            if self.use_unified_db:
                self.set_config_value("backend_type", backend_type)

            logger.info(f"Successfully switched from {old_backend_type} to {backend_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to switch backend to {backend_type}: {sanitize_for_log(str(e))}")
            # 恢复旧后端
            self.backend_type = old_backend_type
            self.backend = old_backend
            return False

    # 缓存操作方法（代理到后端）
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        if not key:
            return None

        try:
            return self.backend.get(key)
        except Exception as e:
            logger.error(f"Failed to get cache key {key}: {sanitize_for_log(str(e))}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        if not key:
            return False

        try:
            # 获取TTL配置
            if ttl is None:
                ttl = self._get_config_value("default_ttl", 3600)

            return self.backend.set(key, value, ttl)
        except Exception as e:
            logger.error(f"Failed to set cache key {key}: {sanitize_for_log(str(e))}")
            return False

    def delete(self, key: str) -> bool:
        """删除缓存键"""
        if not key:
            return False

        try:
            return self.backend.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete cache key {key}: {sanitize_for_log(str(e))}")
            return False

    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if not key:
            return False

        try:
            return self.backend.exists(key)
        except Exception as e:
            logger.error(f"Failed to check existence of key {key}: {sanitize_for_log(str(e))}")
            return False

    def ttl(self, key: str) -> int:
        """获取键的剩余生存时间（秒）

        Returns:
            -1: 键存在但没有设置过期时间
            -2: 键不存在
            >0: 剩余秒数
        """
        if not key:
            return -2

        try:
            return self.backend.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for key {key}: {sanitize_for_log(str(e))}")
            return -2

    def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间"""
        if not key or ttl <= 0:
            return False

        try:
            return self.backend.expire(key, ttl)
        except Exception as e:
            logger.error(f"Failed to set expiration for key {key}: {sanitize_for_log(str(e))}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键列表"""
        try:
            return self.backend.keys(pattern)
        except Exception as e:
            logger.error(f"Failed to get keys with pattern {pattern}: {sanitize_for_log(str(e))}")
            return []

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取多个键的值"""
        if not keys:
            return {}

        try:
            return self.backend.mget(keys)
        except Exception as e:
            logger.error(f"Failed to mget keys: {sanitize_for_log(str(e))}")
            return {}

    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置多个键值对"""
        if not key_values:
            return True

        try:
            # 获取TTL配置
            if ttl is None:
                ttl = self._get_config_value("default_ttl", 3600)

            return self.backend.mset(key_values, ttl)
        except Exception as e:
            logger.error(f"Failed to mset: {sanitize_for_log(str(e))}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        """原子性递增数值型缓存值"""
        if not key:
            raise ValueError("Key cannot be empty")

        try:
            return self.backend.incr(key, amount)
        except Exception as e:
            logger.error(f"Failed to increment key {key}: {sanitize_for_log(str(e))}")
            raise

    def flush_all(self) -> bool:
        """清空所有缓存数据"""
        try:
            return self.backend.flush_all()
        except Exception as e:
            logger.error(f"Failed to flush all cache: {sanitize_for_log(str(e))}")
            return False

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存系统信息和统计"""
        try:
            backend_info = self.backend.get_info()

            # 添加服务级别信息
            service_info = {
                "service_version": "v2",
                "backend_type": self.backend_type,
                "backend_config": self.backend_config,
                "configuration": {
                    "persistence_enabled": self._get_config_value("persistence_enabled", True),
                    "default_ttl": self._get_config_value("default_ttl", 3600),
                    "compression_enabled": self._get_config_value("compression_enabled", False),
                    "stats_enabled": self._get_config_value("stats_enabled", True)
                },
                "last_updated": datetime.now().isoformat()
            }

            # 合并后端信息和服务信息
            return {**backend_info, **service_info}

        except Exception as e:
            logger.error(f"Failed to get cache info: {sanitize_for_log(str(e))}")
            return {
                "service_version": "v2",
                "backend_type": self.backend_type,
                "status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }


# 全局缓存服务实例
_cache_service_instance: Optional[CacheToolsService] = None
_cache_service_lock = threading.Lock()


def get_cache_tools_service() -> CacheToolsService:
    """获取全局缓存工具服务实例"""
    global _cache_service_instance
    if _cache_service_instance is None:
        with _cache_service_lock:
            if _cache_service_instance is None:
                _cache_service_instance = CacheToolsService()
    return _cache_service_instance


def init_cache_tools_service(use_unified_db: bool = True, backend_type: str = "tinydb", backend_config: Optional[Dict[str, Any]] = None) -> CacheToolsService:
    """初始化缓存工具服务"""
    global _cache_service_instance
    with _cache_service_lock:
        _cache_service_instance = CacheToolsService(
            use_unified_db=use_unified_db,
            backend_type=backend_type,
            backend_config=backend_config
        )
    return _cache_service_instance


def switch_cache_backend(backend_type: str, backend_config: Optional[Dict[str, Any]] = None) -> bool:
    """切换缓存存储后端"""
    service = get_cache_tools_service()
    return service.switch_backend(backend_type, backend_config)


def get_available_backends() -> Dict[str, Dict[str, Any]]:
    """获取可用的缓存后端列表"""
    return {
        "tinydb": {
            "name": "TinyDB",
            "description": "基于文件的轻量级数据库，默认选项",
            "persistent": True,
            "requires_external_service": False,
            "config_fields": []
        },
        "diskcache": {
            "name": "DiskCache",
            "description": "磁盘缓存，支持大容量存储",
            "persistent": True,
            "requires_external_service": False,
            "config_fields": ["directory", "size_limit"]
        },
        "memcached": {
            "name": "Memcached",
            "description": "分布式内存缓存系统",
            "persistent": False,
            "requires_external_service": True,
            "config_fields": ["host", "port"]
        },
        "lmdb": {
            "name": "LMDB",
            "description": "高性能嵌入式数据库",
            "persistent": True,
            "requires_external_service": False,
            "config_fields": ["path", "map_size"]
        }
    }