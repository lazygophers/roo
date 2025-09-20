"""
缓存工具集
使用装饰器自动注册缓存相关的MCP工具
"""
import time
import threading
from typing import Dict, Any, Optional
from app.tools.registry import cache_tool, mcp_category


# 注册缓存工具分类
@mcp_category(
    category_id="cache",
    name="缓存管理工具",
    description="内存缓存操作、缓存策略管理、性能优化工具",
    icon="🚀",
    enabled=True,
    sort_order=5
)
def register_cache_category():
    """注册缓存工具分类"""
    pass

# Simple in-memory cache implementation
class SimpleCache:
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def set(self, key: str, value: Any, ttl: int = 0):
        with self._lock:
            expire_time = time.time() + ttl if ttl > 0 else None
            self._cache[key] = {"value": value, "expire_time": expire_time}

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                return None
            entry = self._cache[key]
            if entry["expire_time"] and time.time() > entry["expire_time"]:
                del self._cache[key]
                return None
            return entry["value"]

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def keys(self, pattern: str = "*") -> list:
        with self._lock:
            # 先获取所有键的列表副本，避免在遍历时修改字典
            all_keys = list(self._cache.keys())
            if pattern == "*":
                return [k for k in all_keys if self._is_valid(k)]
            # Simple pattern matching
            return [k for k in all_keys if self._match_pattern(k, pattern) and self._is_valid(k)]

    def _is_valid(self, key: str) -> bool:
        entry = self._cache.get(key)
        if not entry:
            return False
        if entry["expire_time"] and time.time() > entry["expire_time"]:
            del self._cache[key]
            return False
        return True

    def _match_pattern(self, key: str, pattern: str) -> bool:
        # Simple wildcard matching
        return pattern.replace("*", "") in key

    def clear(self):
        with self._lock:
            self._cache.clear()

# Global cache instance
_cache = SimpleCache()


@cache_tool(
    name="set",
    description="Set cache value",
    schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Cache key"
            },
            "value": {
                "description": "Cache value (supports strings, numbers, objects, etc.)"
            },
            "ttl": {
                "type": "integer",
                "description": "TTL in seconds, 0 means never expire",
                "default": 0,
                "minimum": 0
            }
        },
        "required": ["key", "value"]
    },
    metadata={
        "tags": ["cache", "SET", "store"],
        "examples": [
            {"key": "user:123", "value": "Alice"},
            {"key": "session", "value": {"user_id": 123, "token": "abc"}, "ttl": 3600}
        ]
    }
)
def cache_set(key: str, value: Any, ttl: int = 0):
    """Set cache value"""
    try:
        _cache.set(key, value, ttl)
        return {"success": True, "key": key, "message": "Value set successfully"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@cache_tool(
    name="get",
    description="Get cache value",
    schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Cache key"
            }
        },
        "required": ["key"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "Whether operation succeeded"},
            "value": {"description": "Cache value (can be any type)"},
            "key": {"type": "string", "description": "Cache key"},
            "exists": {"type": "boolean", "description": "Whether key exists"}
        },
        "required": ["success", "exists"]
    },
    metadata={
        "tags": ["cache", "GET", "read"],
        "examples": [
            {"key": "user:123"},
            {"key": "session"}
        ]
    }
)
def cache_get(key: str):
    """Get cache value"""
    try:
        value = _cache.get(key)
        exists = value is not None
        return {
            "success": True,
            "key": key,
            "value": value,
            "exists": exists
        }
    except Exception as e:
        return {"success": False, "key": key, "exists": False, "error": str(e)}


@cache_tool(
    name="del",
    description="Delete cache key",
    schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Cache key"
            }
        },
        "required": ["key"]
    },
    metadata={
        "tags": ["cache", "DEL", "delete"],
        "examples": [
            {"key": "user:123"}
        ]
    }
)
def cache_delete(key: str):
    """Delete cache key"""
    try:
        deleted = _cache.delete(key)
        return {"success": True, "key": key, "deleted": deleted}
    except Exception as e:
        return {"success": False, "key": key, "error": str(e)}


@cache_tool(
    name="exists",
    description="Check if cache key exists",
    schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Cache key"
            }
        },
        "required": ["key"]
    },
    metadata={
        "tags": ["cache", "EXISTS", "check"],
        "examples": [
            {"key": "user:123"}
        ]
    }
)
def cache_exists(key: str):
    """Check if cache key exists"""
    try:
        exists = _cache.exists(key)
        return {"success": True, "key": key, "exists": exists}
    except Exception as e:
        return {"success": False, "key": key, "error": str(e)}


@cache_tool(
    name="ttl",
    description="Get cache key's remaining TTL",
    schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Cache key"
            }
        },
        "required": ["key"]
    },
    metadata={
        "tags": ["cache", "TTL", "expiry"],
        "examples": [
            {"key": "user:123"}
        ]
    }
)
def cache_ttl(key: str):
    """Get cache key's remaining TTL"""
    try:
        with _cache._lock:
            if key not in _cache._cache:
                return {"success": True, "key": key, "ttl": -2, "message": "Key does not exist"}

            entry = _cache._cache[key]
            if entry["expire_time"] is None:
                return {"success": True, "key": key, "ttl": -1, "message": "Key never expires"}

            remaining = entry["expire_time"] - time.time()
            if remaining <= 0:
                del _cache._cache[key]
                return {"success": True, "key": key, "ttl": -2, "message": "Key has expired"}

            return {"success": True, "key": key, "ttl": int(remaining)}
    except Exception as e:
        return {"success": False, "key": key, "error": str(e)}


@cache_tool(
    name="expire",
    description="Set cache key expiration time",
    schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Cache key"
            },
            "ttl": {
                "type": "integer",
                "description": "Expiration time in seconds",
                "minimum": 1
            }
        },
        "required": ["key", "ttl"]
    },
    metadata={
        "tags": ["cache", "EXPIRE", "set_expiry"],
        "examples": [
            {"key": "user:123", "ttl": 3600}
        ]
    }
)
def cache_expire(key: str, ttl: int):
    """Set cache key expiration time"""
    try:
        with _cache._lock:
            if key not in _cache._cache:
                return {"success": False, "key": key, "error": "Key does not exist"}

            entry = _cache._cache[key]
            entry["expire_time"] = time.time() + ttl if ttl > 0 else None
            return {"success": True, "key": key, "ttl": ttl, "message": "Expiration time set"}
    except Exception as e:
        return {"success": False, "key": key, "error": str(e)}


@cache_tool(
    name="keys",
    description="Find cache keys matching pattern",
    schema={
        "type": "object",
        "properties": {
            "pattern": {
                "type": "string",
                "description": "Match pattern (supports * wildcards)",
                "default": "*"
            }
        },
        "required": []
    },
    metadata={
        "tags": ["cache", "KEYS", "search"],
        "examples": [
            {},
            {"pattern": "user:*"},
            {"pattern": "session:*"}
        ]
    }
)
def cache_keys(pattern: str = "*"):
    """Find cache keys matching pattern"""
    try:
        keys = _cache.keys(pattern)
        return {"success": True, "pattern": pattern, "keys": keys}
    except Exception as e:
        return {"success": False, "pattern": pattern, "error": str(e)}


@cache_tool(
    name="mset",
    description="Set multiple cache key-value pairs in batch",
    schema={
        "type": "object",
        "properties": {
            "key_values": {
                "type": "object",
                "description": "Key-value pairs object"
            },
            "ttl": {
                "type": "integer",
                "description": "Unified expiration time in seconds, 0 means never expire",
                "default": 0,
                "minimum": 0
            }
        },
        "required": ["key_values"]
    },
    metadata={
        "tags": ["cache", "MSET", "batch_set", "batch"],
        "examples": [
            {"key_values": {"user:1": "Alice", "user:2": "Bob"}},
            {"key_values": {"temp:1": "data1", "temp:2": "data2"}, "ttl": 300}
        ]
    }
)
def cache_mset(key_values: dict, ttl: int = 0):
    """Set multiple cache key-value pairs in batch"""
    try:
        success_count = 0
        errors = []

        for key, value in key_values.items():
            try:
                _cache.set(key, value, ttl)
                success_count += 1
            except Exception as e:
                errors.append({"key": key, "error": str(e)})

        return {
            "success": True,
            "total_keys": len(key_values),
            "success_count": success_count,
            "errors": errors,
            "ttl": ttl
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@cache_tool(
    name="mget",
    description="Get values of multiple cache keys in batch",
    schema={
        "type": "object",
        "properties": {
            "keys": {
                "type": "array",
                "items": {"type": "string"},
                "description": "List of keys to retrieve"
            }
        },
        "required": ["keys"]
    },
    metadata={
        "tags": ["cache", "MGET", "batch_get", "batch"],
        "examples": [
            {"keys": ["user:1", "user:2", "user:3"]}
        ]
    }
)
def cache_mget(keys: list):
    """Get values of multiple cache keys in batch"""
    try:
        results = {}
        for key in keys:
            value = _cache.get(key)
            results[key] = value

        return {
            "success": True,
            "results": results,
            "total_keys": len(keys),
            "found_keys": len([k for k, v in results.items() if v is not None])
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@cache_tool(
    name="incr",
    description="Atomically increment numeric cache value",
    schema={
        "type": "object",
        "properties": {
            "key": {
                "type": "string",
                "description": "Cache key"
            },
            "amount": {
                "type": "integer",
                "description": "Increment amount",
                "default": 1
            }
        },
        "required": ["key"]
    },
    metadata={
        "tags": ["cache", "INCR", "increment", "counter"],
        "examples": [
            {"key": "counter"},
            {"key": "visits", "amount": 5}
        ]
    }
)
def cache_incr(key: str, amount: int = 1):
    """Atomically increment numeric cache value"""
    try:
        with _cache._lock:
            current_value = _cache.get(key)

            if current_value is None:
                # Initialize with the increment amount
                new_value = amount
                _cache.set(key, new_value)
            else:
                # Try to convert to int and increment
                try:
                    current_int = int(current_value)
                    new_value = current_int + amount
                    # Preserve the original entry's TTL
                    entry = _cache._cache.get(key)
                    expire_time = entry["expire_time"] if entry else None
                    ttl = int(expire_time - time.time()) if expire_time else 0
                    _cache.set(key, new_value, ttl if ttl > 0 else 0)
                except (ValueError, TypeError):
                    return {"success": False, "key": key, "error": "Value is not a number"}

            return {"success": True, "key": key, "value": new_value, "increment": amount}
    except Exception as e:
        return {"success": False, "key": key, "error": str(e)}


@cache_tool(
    name="info",
    description="Get cache system information and statistics",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    metadata={
        "tags": ["cache", "INFO", "statistics", "system_info"],
        "examples": [{}]
    }
)
def cache_info():
    """Get cache system information and statistics"""
    try:
        with _cache._lock:
            total_keys = len(_cache._cache)
            expired_keys = 0
            persistent_keys = 0
            current_time = time.time()

            # Analyze cache entries
            for entry in _cache._cache.values():
                if entry["expire_time"] is None:
                    persistent_keys += 1
                elif entry["expire_time"] <= current_time:
                    expired_keys += 1

            active_keys = total_keys - expired_keys

            return {
                "success": True,
                "statistics": {
                    "total_keys": total_keys,
                    "active_keys": active_keys,
                    "expired_keys": expired_keys,
                    "persistent_keys": persistent_keys,
                    "cache_type": "SimpleCache",
                    "thread_safe": True,
                    "features": ["TTL", "Thread-Safe", "Pattern Matching"]
                },
                "timestamp": int(current_time)
            }
    except Exception as e:
        return {"success": False, "error": str(e)}


@cache_tool(
    name="flushall",
    description="Clear all cache data",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    metadata={
        "tags": ["cache", "FLUSHALL", "clear", "delete_all"],
        "examples": [{}]
    }
)
def cache_flushall():
    """Clear all cache data"""
    try:
        _cache.clear()
        return {"success": True, "message": "All cache data cleared"}
    except Exception as e:
        return {"success": False, "error": str(e)}