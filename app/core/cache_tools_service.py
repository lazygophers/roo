"""
缓存工具集服务
Cache Tools Service

实现基于Redis协议的缓存功能，支持字符串、哈希、列表、集合等数据类型。
提供类似Redis的命令接口，包括过期时间、持久化等功能。
"""

from typing import Dict, Any, Optional, List, Union, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import time
import threading
from enum import Enum
import logging

from app.core.unified_database import get_unified_database, TableNames
from app.core.secure_logging import sanitize_for_log
from app.core.cache_backends import create_cache_backend, CacheBackend
from tinydb import Query

logger = logging.getLogger(__name__)

class CacheDataType(str, Enum):
    """缓存数据类型"""
    STRING = "string"
    HASH = "hash"
    LIST = "list"
    SET = "set"
    ZSET = "zset"  # 有序集合
    JSON = "json"

@dataclass
class CacheItem:
    """缓存项数据模型"""
    key: str
    value: Any
    data_type: CacheDataType
    ttl: Optional[int] = None  # 生存时间（秒）
    created_at: float = 0.0
    last_accessed: float = 0.0
    access_count: int = 0
    tags: List[str] = None  # 标签用于批量操作

    def __post_init__(self):
        if self.created_at == 0.0:
            self.created_at = time.time()
        if self.last_accessed == 0.0:
            self.last_accessed = time.time()
        if self.tags is None:
            self.tags = []

    def is_expired(self) -> bool:
        """检查是否已过期"""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl

    def get_remaining_ttl(self) -> int:
        """获取剩余TTL（秒）"""
        if self.ttl is None:
            return -1
        remaining = self.ttl - (time.time() - self.created_at)
        return max(0, int(remaining))

    def update_access(self):
        """更新访问信息"""
        self.last_accessed = time.time()
        self.access_count += 1

@dataclass
class CacheToolsConfig:
    """缓存工具配置数据模型"""
    config_type: str
    name: str
    value: Any
    description: str
    created_at: str = ""
    updated_at: str = ""

class CacheToolsService:
    """缓存工具集服务"""

    def __init__(self, use_unified_db: bool = True):
        """初始化缓存工具服务"""
        self.use_unified_db = use_unified_db
        self._cache_lock = threading.RLock()  # 线程安全锁

        if use_unified_db:
            self.unified_db = get_unified_database()
            self.cache_table = self.unified_db.get_table(TableNames.CACHE_DATA)
            self.config_table = self.unified_db.get_table(TableNames.CACHE_CONFIG)

        # 内存缓存（用于高性能访问）
        self._memory_cache: Dict[str, CacheItem] = {}

        logger.info(f"CacheToolsService initialized with unified db: {use_unified_db}")

        # 初始化默认配置和启动后台任务
        self._initialize_default_config()
        self._start_background_tasks()

    def _initialize_default_config(self):
        """初始化默认缓存配置"""
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
                    description="是否压缩大型缓存值"
                ),
                CacheToolsConfig(
                    config_type="stats_enabled",
                    name="启用统计",
                    value=True,
                    description="是否收集缓存统计信息"
                )
            ]

            for config in default_configs:
                self._create_or_update_config(config)

            logger.info("Cache tools default config initialized")

        except Exception as e:
            logger.error(f"Failed to initialize cache config: {sanitize_for_log(str(e))}")

    def _create_or_update_config(self, config: CacheToolsConfig) -> bool:
        """创建或更新配置项"""
        try:
            Query_obj = Query()
            existing = self.config_table.get(Query_obj.config_type == config.config_type)

            config_data = {
                'config_type': config.config_type,
                'name': config.name,
                'value': config.value,
                'description': config.description,
                'updated_at': datetime.now().isoformat()
            }

            if existing:
                self.config_table.update(config_data, Query_obj.config_type == config.config_type)
                return False
            else:
                config_data['created_at'] = datetime.now().isoformat()
                self.config_table.insert(config_data)
                return True

        except Exception as e:
            logger.error(f"Failed to create/update cache config '{config.config_type}': {sanitize_for_log(str(e))}")
            return False

    def _start_background_tasks(self):
        """启动后台任务"""
        try:
            # 启动过期清理任务（固定5分钟间隔）
            cleanup_interval = 300  # 5分钟
            threading.Timer(cleanup_interval, self._cleanup_expired_items).start()
            logger.info(f"Started cache cleanup task with interval: {cleanup_interval}s")
        except Exception as e:
            logger.error(f"Failed to start background tasks: {sanitize_for_log(str(e))}")

    def _get_config_value(self, config_type: str, default_value: Any) -> Any:
        """获取配置值"""
        try:
            Query_obj = Query()
            config = self.config_table.get(Query_obj.config_type == config_type)
            return config.get('value', default_value) if config else default_value
        except Exception as e:
            logger.error(f"Failed to get config value: {sanitize_for_log(str(e))}")
            return default_value

    def _cleanup_expired_items(self):
        """清理过期的缓存项"""
        try:
            with self._cache_lock:
                expired_keys = []

                # 清理内存缓存中的过期项
                for key, item in self._memory_cache.items():
                    if item.is_expired():
                        expired_keys.append(key)

                for key in expired_keys:
                    del self._memory_cache[key]

                # 清理数据库中的过期项
                if self._get_config_value("persistence_enabled", True):
                    current_time = time.time()
                    Query_obj = Query()

                    # 查找过期项
                    expired_items = self.cache_table.search(
                        (Query_obj.ttl != None) &
                        (Query_obj.created_at + Query_obj.ttl < current_time)
                    )

                    for item in expired_items:
                        self.cache_table.remove(Query_obj.key == item['key'])

                if expired_keys or (hasattr(self, 'expired_items') and len(expired_items) > 0):
                    total_expired = len(expired_keys) + (len(expired_items) if 'expired_items' in locals() else 0)
                    logger.info(f"Cleaned up {total_expired} expired cache items")

                # 重新调度下次清理（固定5分钟间隔）
                cleanup_interval = 300  # 5分钟
                threading.Timer(cleanup_interval, self._cleanup_expired_items).start()

        except Exception as e:
            logger.error(f"Failed to cleanup expired items: {sanitize_for_log(str(e))}")

    def _serialize_value(self, value: Any) -> str:
        """序列化值用于存储"""
        try:
            if isinstance(value, (str, int, float, bool)):
                return json.dumps(value)
            else:
                # 使用pickle序列化复杂对象
                pickled = pickle.dumps(value)
                return base64.b64encode(pickled).decode('utf-8')
        except Exception as e:
            logger.error(f"Failed to serialize value: {sanitize_for_log(str(e))}")
            return json.dumps(str(value))

    def _deserialize_value(self, serialized_value: str) -> Any:
        """反序列化存储的值"""
        try:
            # 首先尝试JSON反序列化
            try:
                return json.loads(serialized_value)
            except json.JSONDecodeError:
                # 如果JSON失败，尝试base64+pickle
                pickled = base64.b64decode(serialized_value.encode('utf-8'))
                return pickle.loads(pickled)
        except Exception as e:
            logger.error(f"Failed to deserialize value: {sanitize_for_log(str(e))}")
            return serialized_value

    def _persist_to_db(self, item: CacheItem):
        """将缓存项持久化到数据库"""
        try:
            if not self._get_config_value("persistence_enabled", True):
                return

            Query_obj = Query()

            # 序列化数据
            item_data = {
                'key': item.key,
                'value': self._serialize_value(item.value),
                'data_type': item.data_type.value,
                'ttl': item.ttl,
                'created_at': item.created_at,
                'last_accessed': item.last_accessed,
                'access_count': item.access_count,
                'tags': json.dumps(item.tags)
            }

            existing = self.cache_table.get(Query_obj.key == item.key)
            if existing:
                self.cache_table.update(item_data, Query_obj.key == item.key)
            else:
                self.cache_table.insert(item_data)

        except Exception as e:
            logger.error(f"Failed to persist cache item: {sanitize_for_log(str(e))}")

    def _load_from_db(self, key: str) -> Optional[CacheItem]:
        """从数据库加载缓存项"""
        try:
            if not self._get_config_value("persistence_enabled", True):
                return None

            Query_obj = Query()
            data = self.cache_table.get(Query_obj.key == key)

            if not data:
                return None

            # 反序列化数据
            item = CacheItem(
                key=data['key'],
                value=self._deserialize_value(data['value']),
                data_type=CacheDataType(data['data_type']),
                ttl=data.get('ttl'),
                created_at=data['created_at'],
                last_accessed=data['last_accessed'],
                access_count=data['access_count'],
                tags=json.loads(data.get('tags', '[]'))
            )

            # 检查是否过期
            if item.is_expired():
                self.cache_table.remove(Query_obj.key == key)
                return None

            return item

        except Exception as e:
            logger.error(f"Failed to load cache item from db: {sanitize_for_log(str(e))}")
            return None

    # Redis风格的字符串操作命令
    def set(self, key: str, value: Any, ttl: Optional[int] = None, tags: List[str] = None) -> bool:
        """SET命令：设置字符串值"""
        try:
            with self._cache_lock:
                if ttl is None:
                    ttl = self._get_config_value("default_ttl", 3600)

                item = CacheItem(
                    key=key,
                    value=value,
                    data_type=CacheDataType.STRING,
                    ttl=ttl,
                    tags=tags or []
                )

                self._memory_cache[key] = item
                self._persist_to_db(item)

                logger.info(f"SET: {sanitize_for_log(key)} (TTL: {ttl})")
                return True

        except Exception as e:
            logger.error(f"Failed to set cache key '{sanitize_for_log(key)}': {sanitize_for_log(str(e))}")
            return False

    def get(self, key: str) -> Any:
        """GET命令：获取字符串值"""
        try:
            with self._cache_lock:
                # 首先检查内存缓存
                if key in self._memory_cache:
                    item = self._memory_cache[key]
                    if item.is_expired():
                        del self._memory_cache[key]
                        return None

                    item.update_access()
                    self._persist_to_db(item)  # 更新访问统计
                    return item.value

                # 从数据库加载
                item = self._load_from_db(key)
                if item:
                    # 加载到内存缓存（固定上限10000项）
                    max_memory_items = 10000
                    if len(self._memory_cache) < max_memory_items:
                        self._memory_cache[key] = item

                    item.update_access()
                    return item.value

                return None

        except Exception as e:
            logger.error(f"Failed to get cache key '{sanitize_for_log(key)}': {sanitize_for_log(str(e))}")
            return None

    def delete(self, key: str) -> bool:
        """DEL命令：删除键"""
        try:
            with self._cache_lock:
                deleted = False

                # 从内存缓存删除
                if key in self._memory_cache:
                    del self._memory_cache[key]
                    deleted = True

                # 从数据库删除
                if self._get_config_value("persistence_enabled", True):
                    Query_obj = Query()
                    result = self.cache_table.remove(Query_obj.key == key)
                    if result:
                        deleted = True

                if deleted:
                    logger.info(f"DEL: {sanitize_for_log(key)}")

                return deleted

        except Exception as e:
            logger.error(f"Failed to delete cache key '{sanitize_for_log(key)}': {sanitize_for_log(str(e))}")
            return False

    def exists(self, key: str) -> bool:
        """EXISTS命令：检查键是否存在"""
        try:
            with self._cache_lock:
                # 检查内存缓存
                if key in self._memory_cache:
                    item = self._memory_cache[key]
                    if item.is_expired():
                        del self._memory_cache[key]
                        return False
                    return True

                # 检查数据库
                item = self._load_from_db(key)
                return item is not None

        except Exception as e:
            logger.error(f"Failed to check existence of key '{sanitize_for_log(key)}': {sanitize_for_log(str(e))}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """EXPIRE命令：设置键的过期时间"""
        try:
            with self._cache_lock:
                # 更新内存缓存
                if key in self._memory_cache:
                    item = self._memory_cache[key]
                    if not item.is_expired():
                        item.ttl = ttl
                        item.created_at = time.time()  # 重置创建时间
                        self._persist_to_db(item)
                        return True

                # 从数据库加载并更新
                item = self._load_from_db(key)
                if item:
                    item.ttl = ttl
                    item.created_at = time.time()
                    self._persist_to_db(item)

                    # 加载到内存缓存（固定上限10000项）
                    max_memory_items = 10000
                    if len(self._memory_cache) < max_memory_items:
                        self._memory_cache[key] = item

                    return True

                return False

        except Exception as e:
            logger.error(f"Failed to set expiry for key '{sanitize_for_log(key)}': {sanitize_for_log(str(e))}")
            return False

    def ttl(self, key: str) -> int:
        """TTL命令：获取键的剩余生存时间"""
        try:
            with self._cache_lock:
                # 检查内存缓存
                if key in self._memory_cache:
                    item = self._memory_cache[key]
                    if item.is_expired():
                        del self._memory_cache[key]
                        return -2  # 键不存在
                    return item.get_remaining_ttl()

                # 从数据库加载
                item = self._load_from_db(key)
                if item:
                    return item.get_remaining_ttl()

                return -2  # 键不存在

        except Exception as e:
            logger.error(f"Failed to get TTL for key '{sanitize_for_log(key)}': {sanitize_for_log(str(e))}")
            return -2

    def keys(self, pattern: str = "*") -> List[str]:
        """KEYS命令：查找匹配模式的键"""
        try:
            with self._cache_lock:
                all_keys = set()

                # 从内存缓存获取键
                for key in self._memory_cache.keys():
                    item = self._memory_cache[key]
                    if not item.is_expired():
                        all_keys.add(key)

                # 从数据库获取键
                if self._get_config_value("persistence_enabled", True):
                    db_items = self.cache_table.all()
                    for item_data in db_items:
                        item = CacheItem(
                            key=item_data['key'],
                            value=None,  # 不需要完整数据
                            data_type=CacheDataType(item_data['data_type']),
                            ttl=item_data.get('ttl'),
                            created_at=item_data['created_at']
                        )
                        if not item.is_expired():
                            all_keys.add(item.key)

                # 简单模式匹配（支持*通配符）
                if pattern == "*":
                    return list(all_keys)
                else:
                    import fnmatch
                    return [key for key in all_keys if fnmatch.fnmatch(key, pattern)]

        except Exception as e:
            logger.error(f"Failed to get keys with pattern '{sanitize_for_log(pattern)}': {sanitize_for_log(str(e))}")
            return []

    def flushall(self) -> bool:
        """FLUSHALL命令：清空所有缓存"""
        try:
            with self._cache_lock:
                # 清空内存缓存
                self._memory_cache.clear()

                # 清空数据库
                if self._get_config_value("persistence_enabled", True):
                    self.cache_table.drop_table()
                    # 重新创建表
                    self.cache_table = self.unified_db.get_table(TableNames.CACHE_DATA)

                logger.info("FLUSHALL: Cleared all cache data")
                return True

        except Exception as e:
            logger.error(f"Failed to flush all cache: {sanitize_for_log(str(e))}")
            return False

    def info(self) -> Dict[str, Any]:
        """INFO命令：获取缓存信息"""
        try:
            with self._cache_lock:
                memory_count = len(self._memory_cache)

                # 计算数据库中的项目数
                db_count = 0
                if self._get_config_value("persistence_enabled", True):
                    db_count = len(self.cache_table.all())

                # 统计内存使用情况
                total_access = sum(item.access_count for item in self._memory_cache.values())

                # 按数据类型统计
                type_stats = {}
                for item in self._memory_cache.values():
                    data_type = item.data_type.value
                    type_stats[data_type] = type_stats.get(data_type, 0) + 1

                return {
                    "status": "active",
                    "memory_items": memory_count,
                    "persistent_items": db_count,
                    "total_items": memory_count + db_count,
                    "total_access_count": total_access,
                    "type_statistics": type_stats,
                    "configuration": {
                        "persistence_enabled": self._get_config_value("persistence_enabled", True),
                        "default_ttl": self._get_config_value("default_ttl", 3600),
                        "compression_enabled": self._get_config_value("compression_enabled", False),
                        "stats_enabled": self._get_config_value("stats_enabled", True)
                    },
                    "last_updated": datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Failed to get cache info: {sanitize_for_log(str(e))}")
            return {"status": "error", "error": str(e)}

    # 高级功能
    def mget(self, keys: List[str]) -> List[Any]:
        """MGET命令：批量获取多个键的值"""
        try:
            return [self.get(key) for key in keys]
        except Exception as e:
            logger.error(f"Failed to mget keys: {sanitize_for_log(str(e))}")
            return [None] * len(keys)

    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """MSET命令：批量设置多个键值对"""
        try:
            success_count = 0
            for key, value in key_values.items():
                if self.set(key, value, ttl):
                    success_count += 1

            logger.info(f"MSET: Set {success_count}/{len(key_values)} key-value pairs")
            return success_count == len(key_values)

        except Exception as e:
            logger.error(f"Failed to mset: {sanitize_for_log(str(e))}")
            return False

    def incr(self, key: str, amount: int = 1) -> Optional[int]:
        """INCR命令：原子性递增"""
        try:
            with self._cache_lock:
                current_value = self.get(key)

                if current_value is None:
                    new_value = amount
                elif isinstance(current_value, (int, float)):
                    new_value = int(current_value) + amount
                else:
                    logger.warning(f"Cannot increment non-numeric value for key '{sanitize_for_log(key)}'")
                    return None

                self.set(key, new_value)
                return new_value

        except Exception as e:
            logger.error(f"Failed to increment key '{sanitize_for_log(key)}': {sanitize_for_log(str(e))}")
            return None


# 全局服务实例
_cache_tools_service: Optional[CacheToolsService] = None

def get_cache_tools_service(use_unified_db: bool = True) -> CacheToolsService:
    """获取缓存工具服务实例"""
    global _cache_tools_service
    if _cache_tools_service is None:
        _cache_tools_service = CacheToolsService(use_unified_db=use_unified_db)
    return _cache_tools_service

def init_cache_tools_service(use_unified_db: bool = True) -> CacheToolsService:
    """初始化缓存工具服务"""
    global _cache_tools_service
    _cache_tools_service = CacheToolsService(use_unified_db=use_unified_db)
    return _cache_tools_service