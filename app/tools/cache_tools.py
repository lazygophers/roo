"""
缓存工具集
使用装饰器自动注册缓存相关的MCP工具
"""
from app.core.mcp_tool_registry import cache_tool


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
def cache_set():
    """Set cache value"""
    pass


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
def cache_get():
    """Get cache value"""
    pass


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
def cache_delete():
    """Delete cache key"""
    pass


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
def cache_exists():
    """Check if cache key exists"""
    pass


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
def cache_ttl():
    """Get cache key's remaining TTL"""
    pass


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
def cache_expire():
    """Set cache key expiration time"""
    pass


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
def cache_keys():
    """Find cache keys matching pattern"""
    pass


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
def cache_mset():
    """Set multiple cache key-value pairs in batch"""
    pass


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
def cache_mget():
    """Get values of multiple cache keys in batch"""
    pass


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
def cache_incr():
    """Atomically increment numeric cache value"""
    pass


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
    pass


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
    pass