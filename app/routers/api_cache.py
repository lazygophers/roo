"""
缓存工具 API 路由
提供多存储后端的缓存管理功能
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.cache_tools_service_v2 import get_cache_tools_service, switch_cache_backend, get_available_backends

logger = setup_logging()

router = APIRouter(prefix="/cache", tags=["Cache"])

class BackendSwitchRequest(BaseModel):
    backend_type: str
    backend_config: Optional[Dict[str, Any]] = None

class CacheSetRequest(BaseModel):
    key: str
    value: Any
    ttl: Optional[int] = None

class CacheGetRequest(BaseModel):
    key: str

class CacheDeleteRequest(BaseModel):
    key: str

class CacheKeysRequest(BaseModel):
    pattern: str = "*"

class CacheMSetRequest(BaseModel):
    key_values: Dict[str, Any]
    ttl: Optional[int] = None

class CacheIncrRequest(BaseModel):
    key: str
    amount: int = 1

@router.get("/info")
async def get_cache_info():
    """获取缓存系统信息"""
    try:
        service = get_cache_tools_service()
        info = service.get_cache_info()

        return {
            "success": True,
            "message": "Cache info retrieved successfully",
            "data": info
        }
    except Exception as e:
        logger.error(f"Failed to get cache info: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get cache info",
            "error": str(e)
        }

@router.get("/backends")
async def get_available_cache_backends():
    """获取可用的存储后端"""
    try:
        backends = get_available_backends()
        service = get_cache_tools_service()
        current_backend = service.get_backend_type()

        return {
            "success": True,
            "message": "Available backends retrieved successfully",
            "data": {
                "backends": backends,
                "current_backend": current_backend
            }
        }
    except Exception as e:
        logger.error(f"Failed to get available backends: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get available backends",
            "error": str(e)
        }

@router.post("/switch-backend")
async def switch_backend(request: BackendSwitchRequest):
    """切换存储后端"""
    try:
        success = switch_cache_backend(request.backend_type, request.backend_config)

        if success:
            return {
                "success": True,
                "message": f"Successfully switched to {request.backend_type} backend"
            }
        else:
            return {
                "success": False,
                "message": f"Failed to switch to {request.backend_type} backend"
            }
    except Exception as e:
        logger.error(f"Failed to switch backend: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to switch backend",
            "error": str(e)
        }

@router.post("/set")
async def cache_set(request: CacheSetRequest):
    """设置缓存值"""
    try:
        service = get_cache_tools_service()
        success = service.set(request.key, request.value, request.ttl)

        if success:
            return {
                "success": True,
                "message": "Cache value set successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to set cache value"
            }
    except Exception as e:
        logger.error(f"Failed to set cache: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to set cache value",
            "error": str(e)
        }

@router.post("/get")
async def cache_get(request: CacheGetRequest):
    """获取缓存值"""
    try:
        service = get_cache_tools_service()
        value = service.get(request.key)

        return {
            "success": True,
            "message": "Cache value retrieved successfully",
            "data": {
                "key": request.key,
                "value": value,
                "exists": value is not None
            }
        }
    except Exception as e:
        logger.error(f"Failed to get cache: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get cache value",
            "error": str(e)
        }

@router.post("/delete")
async def cache_delete(request: CacheDeleteRequest):
    """删除缓存键"""
    try:
        service = get_cache_tools_service()
        success = service.delete(request.key)

        if success:
            return {
                "success": True,
                "message": "Cache key deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to delete cache key"
            }
    except Exception as e:
        logger.error(f"Failed to delete cache: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to delete cache key",
            "error": str(e)
        }

@router.post("/exists")
async def cache_exists(request: CacheGetRequest):
    """检查键是否存在"""
    try:
        service = get_cache_tools_service()
        exists = service.exists(request.key)

        return {
            "success": True,
            "message": "Cache existence check completed",
            "data": {
                "key": request.key,
                "exists": exists
            }
        }
    except Exception as e:
        logger.error(f"Failed to check cache existence: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to check cache existence",
            "error": str(e)
        }

@router.post("/ttl")
async def cache_ttl(request: CacheGetRequest):
    """获取键的剩余生存时间"""
    try:
        service = get_cache_tools_service()
        ttl = service.ttl(request.key)

        return {
            "success": True,
            "message": "Cache TTL retrieved successfully",
            "data": {
                "key": request.key,
                "ttl": ttl,
                "description": {
                    -2: "Key does not exist",
                    -1: "Key exists but has no expiration",
                    ">=0": "Remaining seconds"
                }.get(ttl if ttl in [-2, -1] else ">=0", f"Remaining {ttl} seconds")
            }
        }
    except Exception as e:
        logger.error(f"Failed to get cache TTL: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get cache TTL",
            "error": str(e)
        }

@router.post("/keys")
async def cache_keys(request: CacheKeysRequest):
    """获取匹配模式的键列表"""
    try:
        service = get_cache_tools_service()
        keys = service.keys(request.pattern)

        return {
            "success": True,
            "message": "Cache keys retrieved successfully",
            "data": {
                "pattern": request.pattern,
                "keys": keys,
                "count": len(keys)
            }
        }
    except Exception as e:
        logger.error(f"Failed to get cache keys: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get cache keys",
            "error": str(e)
        }

@router.post("/mget")
async def cache_mget(request: Dict[str, List[str]]):
    """批量获取多个键的值"""
    try:
        keys = request.get("keys", [])
        service = get_cache_tools_service()
        values = service.mget(keys)

        return {
            "success": True,
            "message": "Cache values retrieved successfully",
            "data": {
                "values": values,
                "count": len(values)
            }
        }
    except Exception as e:
        logger.error(f"Failed to mget cache: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get multiple cache values",
            "error": str(e)
        }

@router.post("/mset")
async def cache_mset(request: CacheMSetRequest):
    """批量设置多个键值对"""
    try:
        service = get_cache_tools_service()
        success = service.mset(request.key_values, request.ttl)

        if success:
            return {
                "success": True,
                "message": "Cache values set successfully",
                "data": {
                    "count": len(request.key_values)
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to set cache values"
            }
    except Exception as e:
        logger.error(f"Failed to mset cache: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to set multiple cache values",
            "error": str(e)
        }

@router.post("/incr")
async def cache_incr(request: CacheIncrRequest):
    """原子性递增数值型缓存值"""
    try:
        service = get_cache_tools_service()
        new_value = service.incr(request.key, request.amount)

        return {
            "success": True,
            "message": "Cache value incremented successfully",
            "data": {
                "key": request.key,
                "new_value": new_value,
                "increment": request.amount
            }
        }
    except Exception as e:
        logger.error(f"Failed to increment cache: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to increment cache value",
            "error": str(e)
        }

@router.post("/flush")
async def cache_flush():
    """清空所有缓存数据"""
    try:
        service = get_cache_tools_service()
        success = service.flush_all()

        if success:
            return {
                "success": True,
                "message": "Cache flushed successfully"
            }
        else:
            return {
                "success": False,
                "message": "Failed to flush cache"
            }
    except Exception as e:
        logger.error(f"Failed to flush cache: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to flush cache",
            "error": str(e)
        }