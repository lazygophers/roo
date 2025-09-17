"""
缓存存储后端实现
支持多种存储方案：TinyDB、Redis、DiskCache、Memcached、LMDB
"""

import os
import time
import json
import pickle
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import threading
import logging

from app.core.secure_logging import sanitize_for_log

logger = logging.getLogger(__name__)

@dataclass
class CacheItem:
    """缓存项数据模型"""
    key: str
    value: Any
    ttl: Optional[int] = None  # 生存时间（秒）
    created_at: float = 0.0
    last_accessed: float = 0.0
    access_count: int = 0
    tags: List[str] = None

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
        return time.time() > (self.created_at + self.ttl)

    def update_access(self):
        """更新访问信息"""
        self.last_accessed = time.time()
        self.access_count += 1

    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> 'CacheItem':
        """从字典创建实例"""
        return cls(**data)


class CacheBackend(ABC):
    """缓存后端抽象基类"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._lock = threading.RLock()

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """获取缓存值"""
        pass

    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """设置缓存值"""
        pass

    @abstractmethod
    def delete(self, key: str) -> bool:
        """删除缓存键"""
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        pass

    @abstractmethod
    def ttl(self, key: str) -> int:
        """获取键的剩余TTL（秒），-1表示永不过期，-2表示键不存在"""
        pass

    @abstractmethod
    def expire(self, key: str, ttl: int) -> bool:
        """设置键的过期时间"""
        pass

    @abstractmethod
    def keys(self, pattern: str = "*") -> List[str]:
        """获取匹配模式的键列表"""
        pass

    @abstractmethod
    def mget(self, keys: List[str]) -> Dict[str, Any]:
        """批量获取多个键的值"""
        pass

    @abstractmethod
    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """批量设置多个键值对"""
        pass

    @abstractmethod
    def incr(self, key: str, amount: int = 1) -> int:
        """原子性递增数值"""
        pass

    @abstractmethod
    def flush_all(self) -> bool:
        """清空所有缓存"""
        pass

    @abstractmethod
    def get_info(self) -> Dict[str, Any]:
        """获取缓存系统信息"""
        pass

    @abstractmethod
    def cleanup_expired(self) -> int:
        """清理过期项，返回清理的数量"""
        pass


class TinyDBCacheBackend(CacheBackend):
    """TinyDB缓存后端（默认选项）"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        from app.core.unified_database import get_unified_database, TableNames
        self.unified_db = get_unified_database()
        self.cache_table = self.unified_db.get_table(TableNames.CACHE_DATA)
        logger.info("TinyDB cache backend initialized")

    def _serialize_value(self, value: Any) -> str:
        """序列化值"""
        try:
            return json.dumps(value, ensure_ascii=False)
        except (TypeError, ValueError):
            # 如果JSON序列化失败，使用pickle
            import base64
            return f"__pickle__:{base64.b64encode(pickle.dumps(value)).decode()}"

    def _deserialize_value(self, value_str: str) -> Any:
        """反序列化值"""
        if value_str.startswith("__pickle__:"):
            import base64
            pickle_data = base64.b64decode(value_str[11:])
            return pickle.loads(pickle_data)
        else:
            return json.loads(value_str)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            from tinydb import Query
            result = self.cache_table.search(Query().key == key)
            if not result:
                return None

            item_data = result[0]
            item = CacheItem.from_dict(item_data)

            # 检查是否过期
            if item.is_expired():
                self.delete(key)
                return None

            # 更新访问信息
            item.update_access()
            self.cache_table.update(item.to_dict(), Query().key == key)

            return self._deserialize_value(item.value)

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        with self._lock:
            try:
                serialized_value = self._serialize_value(value)
                item = CacheItem(
                    key=key,
                    value=serialized_value,
                    ttl=ttl or self.config.get('default_ttl', 3600)
                )

                from tinydb import Query
                existing = self.cache_table.search(Query().key == key)
                if existing:
                    self.cache_table.update(item.to_dict(), Query().key == key)
                else:
                    self.cache_table.insert(item.to_dict())
                return True
            except Exception as e:
                logger.error(f"Failed to set cache key {key}: {sanitize_for_log(str(e))}")
                return False

    def delete(self, key: str) -> bool:
        with self._lock:
            from tinydb import Query
            removed = self.cache_table.remove(Query().key == key)
            return len(removed) > 0

    def exists(self, key: str) -> bool:
        with self._lock:
            from tinydb import Query
            result = self.cache_table.search(Query().key == key)
            if not result:
                return False

            item = CacheItem.from_dict(result[0])
            if item.is_expired():
                self.delete(key)
                return False
            return True

    def ttl(self, key: str) -> int:
        with self._lock:
            from tinydb import Query
            result = self.cache_table.search(Query().key == key)
            if not result:
                return -2  # 键不存在

            item = CacheItem.from_dict(result[0])
            if item.ttl is None:
                return -1  # 永不过期

            remaining = item.created_at + item.ttl - time.time()
            if remaining <= 0:
                self.delete(key)
                return -2
            return int(remaining)

    def expire(self, key: str, ttl: int) -> bool:
        with self._lock:
            from tinydb import Query
            result = self.cache_table.search(Query().key == key)
            if not result:
                return False

            item_data = result[0]
            item_data['ttl'] = ttl
            item_data['created_at'] = time.time()  # 重置创建时间

            self.cache_table.update(item_data, Query().key == key)
            return True

    def keys(self, pattern: str = "*") -> List[str]:
        with self._lock:
            import fnmatch
            all_items = self.cache_table.all()
            result_keys = []

            for item_data in all_items:
                item = CacheItem.from_dict(item_data)
                if not item.is_expired() and fnmatch.fnmatch(item.key, pattern):
                    result_keys.append(item.key)

            return result_keys

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        try:
            for key, value in key_values.items():
                self.set(key, value, ttl)
            return True
        except Exception as e:
            logger.error(f"Failed to mset: {sanitize_for_log(str(e))}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        with self._lock:
            current = self.get(key)
            if current is None:
                new_value = amount
            else:
                try:
                    new_value = int(current) + amount
                except (ValueError, TypeError):
                    raise ValueError(f"Cannot increment non-numeric value for key {key}")

            self.set(key, new_value)
            return new_value

    def flush_all(self) -> bool:
        with self._lock:
            try:
                self.cache_table.truncate()
                return True
            except Exception as e:
                logger.error(f"Failed to flush all: {sanitize_for_log(str(e))}")
                return False

    def get_info(self) -> Dict[str, Any]:
        with self._lock:
            all_items = self.cache_table.all()
            total_items = len(all_items)
            expired_count = 0
            memory_items = 0  # TinyDB中所有项都在磁盘上

            for item_data in all_items:
                item = CacheItem.from_dict(item_data)
                if item.is_expired():
                    expired_count += 1

            return {
                "backend": "tinydb",
                "status": "active",
                "total_items": total_items,
                "memory_items": memory_items,
                "persistent_items": total_items,
                "expired_items": expired_count,
                "total_access_count": sum(item.get('access_count', 0) for item in all_items),
                "last_updated": datetime.now().isoformat()
            }

    def cleanup_expired(self) -> int:
        with self._lock:
            from tinydb import Query
            all_items = self.cache_table.all()
            expired_keys = []

            for item_data in all_items:
                item = CacheItem.from_dict(item_data)
                if item.is_expired():
                    expired_keys.append(item.key)

            # 删除过期项
            for key in expired_keys:
                self.cache_table.remove(Query().key == key)

            return len(expired_keys)


class RedisCacheBackend(CacheBackend):
    """Redis缓存后端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import redis
            self.redis_client = redis.Redis(
                host=config.get('host', 'localhost'),
                port=config.get('port', 6379),
                db=config.get('db', 0),
                password=config.get('password'),
                decode_responses=True,
                socket_timeout=config.get('timeout', 5)
            )
            # 测试连接
            self.redis_client.ping()
            logger.info("Redis cache backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis backend: {sanitize_for_log(str(e))}")
            raise

    def _serialize_value(self, value: Any) -> str:
        """序列化值"""
        if isinstance(value, (str, int, float)):
            return str(value)
        return json.dumps(value, ensure_ascii=False)

    def _deserialize_value(self, value_str: str) -> Any:
        """反序列化值"""
        try:
            return json.loads(value_str)
        except (json.JSONDecodeError, TypeError):
            return value_str

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.redis_client.get(key)
            if value is None:
                return None
            return self._deserialize_value(value)
        except Exception as e:
            logger.error(f"Redis GET error for key {key}: {sanitize_for_log(str(e))}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            serialized_value = self._serialize_value(value)
            ex = ttl or self.config.get('default_ttl', 3600)
            return self.redis_client.set(key, serialized_value, ex=ex)
        except Exception as e:
            logger.error(f"Redis SET error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return self.redis_client.delete(key) > 0
        except Exception as e:
            logger.error(f"Redis DELETE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def exists(self, key: str) -> bool:
        try:
            return self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis EXISTS error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def ttl(self, key: str) -> int:
        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {sanitize_for_log(str(e))}")
            return -2

    def expire(self, key: str, ttl: int) -> bool:
        try:
            return self.redis_client.expire(key, ttl)
        except Exception as e:
            logger.error(f"Redis EXPIRE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        try:
            return self.redis_client.keys(pattern)
        except Exception as e:
            logger.error(f"Redis KEYS error for pattern {pattern}: {sanitize_for_log(str(e))}")
            return []

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        try:
            values = self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = self._deserialize_value(value)
            return result
        except Exception as e:
            logger.error(f"Redis MGET error: {sanitize_for_log(str(e))}")
            return {}

    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        try:
            # 序列化所有值
            serialized_kv = {k: self._serialize_value(v) for k, v in key_values.items()}

            # 使用pipeline提高性能
            pipe = self.redis_client.pipeline()
            pipe.mset(serialized_kv)

            # 如果有TTL，为每个键设置过期时间
            if ttl:
                for key in key_values.keys():
                    pipe.expire(key, ttl)

            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Redis MSET error: {sanitize_for_log(str(e))}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Redis INCR error for key {key}: {sanitize_for_log(str(e))}")
            raise

    def flush_all(self) -> bool:
        try:
            return self.redis_client.flushdb()
        except Exception as e:
            logger.error(f"Redis FLUSHALL error: {sanitize_for_log(str(e))}")
            return False

    def get_info(self) -> Dict[str, Any]:
        try:
            info = self.redis_client.info()
            dbsize = self.redis_client.dbsize()

            return {
                "backend": "redis",
                "status": "active",
                "total_items": dbsize,
                "memory_items": dbsize,  # Redis中所有项都在内存中
                "persistent_items": 0,
                "memory_usage": info.get('used_memory', 0),
                "connected_clients": info.get('connected_clients', 0),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Redis INFO error: {sanitize_for_log(str(e))}")
            return {"backend": "redis", "status": "error", "error": str(e)}

    def cleanup_expired(self) -> int:
        # Redis自动处理过期键，无需手动清理
        return 0


class DiskCacheBackend(CacheBackend):
    """DiskCache缓存后端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import diskcache as dc
            cache_dir = config.get('directory', './cache')
            os.makedirs(cache_dir, exist_ok=True)

            self.cache = dc.Cache(
                directory=cache_dir,
                size_limit=config.get('size_limit', 1024**3),  # 1GB默认
                timeout=config.get('timeout', 10)
            )
            logger.info(f"DiskCache backend initialized at {cache_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize DiskCache backend: {sanitize_for_log(str(e))}")
            raise

    def get(self, key: str) -> Optional[Any]:
        try:
            return self.cache.get(key)
        except Exception as e:
            logger.error(f"DiskCache GET error for key {key}: {sanitize_for_log(str(e))}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            expire_time = ttl or self.config.get('default_ttl', 3600)
            return self.cache.set(key, value, expire=expire_time)
        except Exception as e:
            logger.error(f"DiskCache SET error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return self.cache.delete(key)
        except Exception as e:
            logger.error(f"DiskCache DELETE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def exists(self, key: str) -> bool:
        try:
            return key in self.cache
        except Exception as e:
            logger.error(f"DiskCache EXISTS error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def ttl(self, key: str) -> int:
        try:
            # DiskCache没有直接的TTL方法，通过检查过期时间实现
            if key not in self.cache:
                return -2
            # 这是一个简化实现，实际TTL需要更复杂的逻辑
            return -1  # 假设永不过期
        except Exception as e:
            logger.error(f"DiskCache TTL error for key {key}: {sanitize_for_log(str(e))}")
            return -2

    def expire(self, key: str, ttl: int) -> bool:
        try:
            # DiskCache需要重新设置值来更新过期时间
            if key in self.cache:
                value = self.cache.get(key)
                return self.cache.set(key, value, expire=ttl)
            return False
        except Exception as e:
            logger.error(f"DiskCache EXPIRE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        try:
            import fnmatch
            all_keys = list(self.cache)
            return [key for key in all_keys if fnmatch.fnmatch(str(key), pattern)]
        except Exception as e:
            logger.error(f"DiskCache KEYS error: {sanitize_for_log(str(e))}")
            return []

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        try:
            for key, value in key_values.items():
                if not self.set(key, value, ttl):
                    return False
            return True
        except Exception as e:
            logger.error(f"DiskCache MSET error: {sanitize_for_log(str(e))}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        try:
            current = self.cache.get(key, 0)
            new_value = int(current) + amount
            self.cache.set(key, new_value)
            return new_value
        except Exception as e:
            logger.error(f"DiskCache INCR error for key {key}: {sanitize_for_log(str(e))}")
            raise

    def flush_all(self) -> bool:
        try:
            self.cache.clear()
            return True
        except Exception as e:
            logger.error(f"DiskCache FLUSH error: {sanitize_for_log(str(e))}")
            return False

    def get_info(self) -> Dict[str, Any]:
        try:
            stats = self.cache.stats()
            return {
                "backend": "diskcache",
                "status": "active",
                "total_items": len(self.cache),
                "memory_items": 0,
                "persistent_items": len(self.cache),
                "cache_hits": stats.get('cache_hits', 0),
                "cache_misses": stats.get('cache_misses', 0),
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"DiskCache INFO error: {sanitize_for_log(str(e))}")
            return {"backend": "diskcache", "status": "error", "error": str(e)}

    def cleanup_expired(self) -> int:
        try:
            # DiskCache自动清理过期项
            self.cache.expire()
            return 0
        except Exception as e:
            logger.error(f"DiskCache cleanup error: {sanitize_for_log(str(e))}")
            return 0


class MemcachedBackend(CacheBackend):
    """Memcached缓存后端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import pymemcache.client.base as memcache
            self.client = memcache.Client(
                (config.get('host', 'localhost'), config.get('port', 11211)),
                timeout=config.get('timeout', 5),
                ignore_exc=True
            )
            # 测试连接
            self.client.stats()
            logger.info("Memcached backend initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Memcached backend: {sanitize_for_log(str(e))}")
            raise

    def _serialize_value(self, value: Any) -> bytes:
        """序列化值"""
        return pickle.dumps(value)

    def _deserialize_value(self, value_bytes: bytes) -> Any:
        """反序列化值"""
        return pickle.loads(value_bytes)

    def get(self, key: str) -> Optional[Any]:
        try:
            value = self.client.get(key)
            if value is None:
                return None
            return self._deserialize_value(value)
        except Exception as e:
            logger.error(f"Memcached GET error for key {key}: {sanitize_for_log(str(e))}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            serialized_value = self._serialize_value(value)
            expire_time = ttl or self.config.get('default_ttl', 3600)
            return self.client.set(key, serialized_value, expire=expire_time)
        except Exception as e:
            logger.error(f"Memcached SET error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def delete(self, key: str) -> bool:
        try:
            return self.client.delete(key)
        except Exception as e:
            logger.error(f"Memcached DELETE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def exists(self, key: str) -> bool:
        try:
            return self.client.get(key) is not None
        except Exception as e:
            logger.error(f"Memcached EXISTS error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def ttl(self, key: str) -> int:
        # Memcached不支持TTL查询
        return -1

    def expire(self, key: str, ttl: int) -> bool:
        try:
            # Memcached需要重新设置值来更新过期时间
            value = self.client.get(key)
            if value is not None:
                return self.client.set(key, value, expire=ttl)
            return False
        except Exception as e:
            logger.error(f"Memcached EXPIRE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        # Memcached不支持keys操作
        logger.warning("Memcached does not support KEYS operation")
        return []

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        try:
            values = self.client.get_multi(keys)
            result = {}
            for key, value in values.items():
                if value is not None:
                    result[key] = self._deserialize_value(value)
            return result
        except Exception as e:
            logger.error(f"Memcached MGET error: {sanitize_for_log(str(e))}")
            return {}

    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        try:
            serialized_kv = {k: self._serialize_value(v) for k, v in key_values.items()}
            expire_time = ttl or self.config.get('default_ttl', 3600)

            failed_keys = self.client.set_multi(serialized_kv, expire=expire_time)
            return len(failed_keys) == 0
        except Exception as e:
            logger.error(f"Memcached MSET error: {sanitize_for_log(str(e))}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        try:
            # Memcached的incr只能用于整数值
            result = self.client.incr(key, amount)
            if result is None:
                # 键不存在，先设置为0再递增
                self.client.set(key, b'0')
                result = self.client.incr(key, amount)
            return result
        except Exception as e:
            logger.error(f"Memcached INCR error for key {key}: {sanitize_for_log(str(e))}")
            raise

    def flush_all(self) -> bool:
        try:
            return self.client.flush_all()
        except Exception as e:
            logger.error(f"Memcached FLUSH error: {sanitize_for_log(str(e))}")
            return False

    def get_info(self) -> Dict[str, Any]:
        try:
            stats = self.client.stats()
            if stats:
                stats_data = list(stats.values())[0]  # 获取第一个服务器的统计
                return {
                    "backend": "memcached",
                    "status": "active",
                    "total_items": int(stats_data.get(b'curr_items', 0)),
                    "memory_items": int(stats_data.get(b'curr_items', 0)),
                    "persistent_items": 0,
                    "memory_usage": int(stats_data.get(b'bytes', 0)),
                    "get_hits": int(stats_data.get(b'get_hits', 0)),
                    "get_misses": int(stats_data.get(b'get_misses', 0)),
                    "last_updated": datetime.now().isoformat()
                }
            else:
                return {"backend": "memcached", "status": "error", "error": "No stats available"}
        except Exception as e:
            logger.error(f"Memcached INFO error: {sanitize_for_log(str(e))}")
            return {"backend": "memcached", "status": "error", "error": str(e)}

    def cleanup_expired(self) -> int:
        # Memcached自动处理过期键
        return 0


class LMDBBackend(CacheBackend):
    """LMDB缓存后端"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import lmdb
            db_path = config.get('path', './lmdb_cache')
            os.makedirs(db_path, exist_ok=True)

            # 打开LMDB环境
            self.env = lmdb.open(
                db_path,
                max_dbs=1,
                map_size=config.get('map_size', 1024**3),  # 1GB默认
                sync=config.get('sync', True),
                writemap=config.get('writemap', True)
            )
            logger.info(f"LMDB backend initialized at {db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize LMDB backend: {sanitize_for_log(str(e))}")
            raise

    def _make_cache_key(self, key: str) -> bytes:
        """创建缓存键"""
        return f"cache:{key}".encode()

    def _make_meta_key(self, key: str) -> bytes:
        """创建元数据键"""
        return f"meta:{key}".encode()

    def _serialize_item(self, item: CacheItem) -> bytes:
        """序列化缓存项"""
        return pickle.dumps(item)

    def _deserialize_item(self, data: bytes) -> CacheItem:
        """反序列化缓存项"""
        return pickle.loads(data)

    def get(self, key: str) -> Optional[Any]:
        try:
            with self.env.begin() as txn:
                data = txn.get(self._make_cache_key(key))
                if data is None:
                    return None

                item = self._deserialize_item(data)

                # 检查是否过期
                if item.is_expired():
                    self.delete(key)
                    return None

                # 更新访问信息
                item.update_access()
                with self.env.begin(write=True) as write_txn:
                    write_txn.put(self._make_cache_key(key), self._serialize_item(item))

                return item.value
        except Exception as e:
            logger.error(f"LMDB GET error for key {key}: {sanitize_for_log(str(e))}")
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        try:
            item = CacheItem(
                key=key,
                value=value,
                ttl=ttl or self.config.get('default_ttl', 3600)
            )

            with self.env.begin(write=True) as txn:
                return txn.put(self._make_cache_key(key), self._serialize_item(item))
        except Exception as e:
            logger.error(f"LMDB SET error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def delete(self, key: str) -> bool:
        try:
            with self.env.begin(write=True) as txn:
                return txn.delete(self._make_cache_key(key))
        except Exception as e:
            logger.error(f"LMDB DELETE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def exists(self, key: str) -> bool:
        try:
            with self.env.begin() as txn:
                data = txn.get(self._make_cache_key(key))
                if data is None:
                    return False

                item = self._deserialize_item(data)
                if item.is_expired():
                    self.delete(key)
                    return False
                return True
        except Exception as e:
            logger.error(f"LMDB EXISTS error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def ttl(self, key: str) -> int:
        try:
            with self.env.begin() as txn:
                data = txn.get(self._make_cache_key(key))
                if data is None:
                    return -2

                item = self._deserialize_item(data)
                if item.ttl is None:
                    return -1

                remaining = item.created_at + item.ttl - time.time()
                if remaining <= 0:
                    self.delete(key)
                    return -2
                return int(remaining)
        except Exception as e:
            logger.error(f"LMDB TTL error for key {key}: {sanitize_for_log(str(e))}")
            return -2

    def expire(self, key: str, ttl: int) -> bool:
        try:
            with self.env.begin() as txn:
                data = txn.get(self._make_cache_key(key))
                if data is None:
                    return False

                item = self._deserialize_item(data)
                item.ttl = ttl
                item.created_at = time.time()

                with self.env.begin(write=True) as write_txn:
                    return write_txn.put(self._make_cache_key(key), self._serialize_item(item))
        except Exception as e:
            logger.error(f"LMDB EXPIRE error for key {key}: {sanitize_for_log(str(e))}")
            return False

    def keys(self, pattern: str = "*") -> List[str]:
        try:
            import fnmatch
            result_keys = []
            cache_prefix = b"cache:"

            with self.env.begin() as txn:
                cursor = txn.cursor()
                cursor.first()

                for db_key, data in cursor:
                    if db_key.startswith(cache_prefix):
                        item = self._deserialize_item(data)
                        if not item.is_expired() and fnmatch.fnmatch(item.key, pattern):
                            result_keys.append(item.key)

            return result_keys
        except Exception as e:
            logger.error(f"LMDB KEYS error: {sanitize_for_log(str(e))}")
            return []

    def mget(self, keys: List[str]) -> Dict[str, Any]:
        result = {}
        for key in keys:
            value = self.get(key)
            if value is not None:
                result[key] = value
        return result

    def mset(self, key_values: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        try:
            with self.env.begin(write=True) as txn:
                for key, value in key_values.items():
                    item = CacheItem(
                        key=key,
                        value=value,
                        ttl=ttl or self.config.get('default_ttl', 3600)
                    )
                    txn.put(self._make_cache_key(key), self._serialize_item(item))
            return True
        except Exception as e:
            logger.error(f"LMDB MSET error: {sanitize_for_log(str(e))}")
            return False

    def incr(self, key: str, amount: int = 1) -> int:
        try:
            current = self.get(key)
            if current is None:
                new_value = amount
            else:
                new_value = int(current) + amount

            self.set(key, new_value)
            return new_value
        except Exception as e:
            logger.error(f"LMDB INCR error for key {key}: {sanitize_for_log(str(e))}")
            raise

    def flush_all(self) -> bool:
        try:
            with self.env.begin(write=True) as txn:
                # 删除所有缓存键
                cache_prefix = b"cache:"
                cursor = txn.cursor()
                cursor.first()

                keys_to_delete = []
                for db_key, _ in cursor:
                    if db_key.startswith(cache_prefix):
                        keys_to_delete.append(db_key)

                for key in keys_to_delete:
                    txn.delete(key)

            return True
        except Exception as e:
            logger.error(f"LMDB FLUSH error: {sanitize_for_log(str(e))}")
            return False

    def get_info(self) -> Dict[str, Any]:
        try:
            with self.env.begin() as txn:
                stat = txn.stat()
                total_items = 0
                cache_prefix = b"cache:"

                cursor = txn.cursor()
                cursor.first()

                for db_key, _ in cursor:
                    if db_key.startswith(cache_prefix):
                        total_items += 1

                return {
                    "backend": "lmdb",
                    "status": "active",
                    "total_items": total_items,
                    "memory_items": 0,
                    "persistent_items": total_items,
                    "page_size": stat['psize'],
                    "tree_depth": stat['depth'],
                    "last_updated": datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"LMDB INFO error: {sanitize_for_log(str(e))}")
            return {"backend": "lmdb", "status": "error", "error": str(e)}

    def cleanup_expired(self) -> int:
        try:
            expired_keys = []
            cache_prefix = b"cache:"

            with self.env.begin() as txn:
                cursor = txn.cursor()
                cursor.first()

                for db_key, data in cursor:
                    if db_key.startswith(cache_prefix):
                        item = self._deserialize_item(data)
                        if item.is_expired():
                            expired_keys.append(db_key)

            # 删除过期键
            if expired_keys:
                with self.env.begin(write=True) as txn:
                    for key in expired_keys:
                        txn.delete(key)

            return len(expired_keys)
        except Exception as e:
            logger.error(f"LMDB cleanup error: {sanitize_for_log(str(e))}")
            return 0


# 后端工厂函数
def create_cache_backend(backend_type: str, config: Dict[str, Any]) -> CacheBackend:
    """创建缓存后端实例"""
    backend_map = {
        'tinydb': TinyDBCacheBackend,
        'redis': RedisCacheBackend,
        'diskcache': DiskCacheBackend,
        'memcached': MemcachedBackend,
        'lmdb': LMDBBackend
    }

    backend_class = backend_map.get(backend_type)
    if not backend_class:
        raise ValueError(f"Unsupported cache backend: {backend_type}")

    return backend_class(config)