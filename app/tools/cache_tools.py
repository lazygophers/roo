"""
缓存工具集
使用装饰器自动注册缓存相关的MCP工具
"""
import os
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

# DiskCache implementation for persistent storage
class DiskCacheManager:
    def __init__(self, cache_dir: str = "data/mcp/cache", max_size_mb: int = 1024, timeout: int = 10):
        import os
        from pathlib import Path
        from app.core.config import PROJECT_ROOT
        from app.core.tool_config_service import get_tool_config

        # Load configuration from file
        try:
            config = get_tool_config("cache_tools")

            # Apply configuration with fallbacks to parameters
            cache_dir = config.get("cache_dir", cache_dir)
            max_size_mb = config.get("max_size_mb", max_size_mb)
            timeout = config.get("timeout_seconds", timeout)

            # Store configuration for reference
            self.config = config
        except Exception as e:
            # Fallback to default parameters if config loading fails
            self.config = {
                "cache_dir": cache_dir,
                "max_size_mb": max_size_mb,
                "timeout_seconds": timeout
            }

        # Create absolute cache directory path
        self.cache_dir = Path(PROJECT_ROOT) / cache_dir
        if self.config.get("auto_create_dirs", True):
            self.cache_dir.mkdir(parents=True, exist_ok=True)

        try:
            import diskcache as dc

            # Apply DiskCache specific configuration
            diskcache_config = self.config.get("diskcache", {})

            self._cache = dc.Cache(
                directory=str(self.cache_dir),
                size_limit=max_size_mb * 1024 * 1024,  # Convert MB to bytes
                timeout=timeout,
                # DiskCache advanced options from config
                eviction_policy=diskcache_config.get("eviction_policy", "least-recently-stored"),
                disk_min_file_size=diskcache_config.get("disk_min_file_size", 32768),
                disk_pickle_protocol=diskcache_config.get("disk_pickle_protocol", 4),
                statistics=diskcache_config.get("statistics", True),
                tag_index=diskcache_config.get("tag_index", False)
            )
            self._lock = threading.Lock()
        except ImportError:
            raise ImportError("diskcache library is required. Install with: pip install diskcache")

    def set(self, key: str, value: Any, ttl: int = 0):
        with self._lock:
            expire_time = ttl if ttl > 0 else None
            return self._cache.set(key, value, expire=expire_time)

    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            try:
                return self._cache.get(key)
            except KeyError:
                return None

    def delete(self, key: str) -> bool:
        with self._lock:
            try:
                return self._cache.delete(key)
            except KeyError:
                return False

    def exists(self, key: str) -> bool:
        with self._lock:
            return key in self._cache

    def keys(self, pattern: str = "*") -> list:
        with self._lock:
            import fnmatch
            all_keys = list(self._cache)
            if pattern == "*":
                return [str(k) for k in all_keys]
            # Pattern matching with fnmatch
            return [str(k) for k in all_keys if fnmatch.fnmatch(str(k), pattern)]

    def clear(self):
        with self._lock:
            self._cache.clear()

    def info(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics and configuration info"""
        with self._lock:
            try:
                stats = self._cache.stats()

                # Get configuration sections
                monitoring_config = self.config.get("monitoring", {})
                operations_config = self.config.get("operations", {})
                limits_config = self.config.get("limits", {})
                ttl_config = self.config.get("ttl", {})

                return {
                    # Core info
                    "backend": "diskcache",
                    "cache_type": "DiskCache",
                    "version": self.config.get("version", "1.0"),
                    "directory": str(self.cache_dir),

                    # Statistics
                    "statistics": {
                        "total_keys": len(self._cache),
                        "cache_hits": stats.get('cache_hits', 0) if monitoring_config.get("enable_statistics") else "disabled",
                        "cache_misses": stats.get('cache_misses', 0) if monitoring_config.get("enable_statistics") else "disabled",
                        "size_limit_bytes": self._cache.size_limit,
                        "size_limit_mb": self._cache.size_limit / (1024 * 1024),
                        "current_size_bytes": getattr(self._cache, 'volume', 0),
                        "current_size_mb": getattr(self._cache, 'volume', 0) / (1024 * 1024)
                    },

                    # Configuration summary
                    "configuration": {
                        "cache_dir": self.config.get("cache_dir"),
                        "max_size_mb": self.config.get("max_size_mb"),
                        "timeout_seconds": self.config.get("timeout_seconds"),
                        "ttl_enabled": ttl_config.get("enable_ttl", False),
                        "default_ttl_seconds": ttl_config.get("default_ttl_seconds", 0),
                        "thread_safe": operations_config.get("thread_safe", True),
                        "pattern_matching": operations_config.get("pattern_matching", "fnmatch")
                    },

                    # Features
                    "features": [
                        "Persistent Storage",
                        "Thread-Safe Operations" if operations_config.get("thread_safe") else "Non-Thread-Safe",
                        "TTL Support" if ttl_config.get("enable_ttl") else "No TTL",
                        "Size-Limited",
                        "Pattern Matching (" + operations_config.get("pattern_matching", "fnmatch") + ")",
                        "Batch Operations" if operations_config.get("batch_operations") else "Single Operations",
                        "Statistics" if monitoring_config.get("enable_statistics") else "No Statistics"
                    ],

                    # Limits
                    "limits": {
                        "max_key_length": limits_config.get("max_key_length", 250),
                        "max_value_size_mb": limits_config.get("max_value_size_mb", 100),
                        "max_concurrent_operations": limits_config.get("max_concurrent_operations", 10),
                        "blocked_patterns": limits_config.get("blocked_key_patterns", [])
                    },

                    # Health
                    "health": {
                        "status": "healthy",
                        "writable": self.cache_dir.exists() and os.access(self.cache_dir, os.W_OK),
                        "readable": self.cache_dir.exists() and os.access(self.cache_dir, os.R_OK)
                    }
                }
            except Exception as e:
                return {
                    "backend": "diskcache",
                    "cache_type": "DiskCache",
                    "directory": str(self.cache_dir),
                    "statistics": {
                        "total_keys": len(self._cache) if hasattr(self, '_cache') else 0
                    },
                    "health": {
                        "status": "error",
                        "error": str(e)
                    },
                    "features": ["Persistent", "Thread-Safe", "TTL", "Size-Limited"]
                }

# Global cache instance
_cache = DiskCacheManager()


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
        # DiskCache doesn't have direct TTL support, return simplified response
        exists = _cache.exists(key)
        if not exists:
            return {"success": True, "key": key, "ttl": -2, "message": "Key does not exist"}
        else:
            return {"success": True, "key": key, "ttl": -1, "message": "Key exists (TTL not available in DiskCache)"}
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
        # DiskCache doesn't support changing TTL for existing keys
        # We need to re-set the value with new TTL
        if not _cache.exists(key):
            return {"success": False, "key": key, "error": "Key does not exist"}

        # Get current value and re-set with new TTL
        current_value = _cache.get(key)
        if current_value is not None:
            success = _cache.set(key, current_value, ttl)
            if success:
                return {"success": True, "key": key, "ttl": ttl, "message": "Expiration time set (value re-saved)"}
            else:
                return {"success": False, "key": key, "error": "Failed to re-set value with new TTL"}
        else:
            return {"success": False, "key": key, "error": "Failed to retrieve current value"}
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
                    # DiskCache doesn't expose TTL info, just set without TTL
                    _cache.set(key, new_value)
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
        # Use the DiskCacheManager's info method
        info_data = _cache.info()
        current_time = time.time()

        return {
            "success": True,
            "statistics": {
                "total_keys": info_data.get("total_keys", 0),
                "active_keys": info_data.get("total_keys", 0),  # DiskCache auto-manages expired keys
                "expired_keys": 0,  # DiskCache auto-cleans expired keys
                "persistent_keys": info_data.get("total_keys", 0),  # All keys are persistent
                "cache_type": info_data.get("cache_type", "DiskCache"),
                "thread_safe": True,
                "features": info_data.get("features", ["Persistent", "Thread-Safe", "TTL", "Size-Limited"]),
                "directory": info_data.get("directory", ""),
                "cache_hits": info_data.get("cache_hits", 0),
                "cache_misses": info_data.get("cache_misses", 0),
                "size_limit": info_data.get("size_limit", 0),
                "current_size": info_data.get("current_size", 0)
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