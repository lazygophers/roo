"""
缓存工具集 API 路由
Cache Tools API Routes

提供基于Redis协议的缓存操作接口，支持字符串、过期时间、批量操作等功能。
"""

from fastapi import APIRouter, HTTPException, Query as FastAPIQuery
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.cache_tools_service import (
    get_cache_tools_service,
    CacheDataType,
    CacheItem
)
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging

logger = setup_logging("INFO")
router = APIRouter(prefix="/cache", tags=["Cache Tools"])

# Pydantic 模型定义
class SetCacheRequest(BaseModel):
    """设置缓存请求模型"""
    key: str = Field(..., description="缓存键")
    value: Any = Field(..., description="缓存值")
    ttl: Optional[int] = Field(default=None, ge=1, description="生存时间（秒）")
    tags: Optional[List[str]] = Field(default=None, description="标签列表")

class GetCacheResponse(BaseModel):
    """获取缓存响应模型"""
    key: str
    value: Any
    exists: bool
    ttl: int = Field(description="剩余生存时间，-1表示永不过期，-2表示不存在")
    data_type: str
    last_accessed: str
    access_count: int

class BatchSetRequest(BaseModel):
    """批量设置请求模型"""
    key_values: Dict[str, Any] = Field(..., description="键值对字典")
    ttl: Optional[int] = Field(default=None, ge=1, description="统一生存时间（秒）")

class BatchGetRequest(BaseModel):
    """批量获取请求模型"""
    keys: List[str] = Field(..., description="键列表")

class DeleteKeysRequest(BaseModel):
    """删除键请求模型"""
    keys: List[str] = Field(..., description="要删除的键列表")

class ExpireRequest(BaseModel):
    """设置过期时间请求模型"""
    key: str = Field(..., description="缓存键")
    ttl: int = Field(..., ge=1, description="生存时间（秒）")

class IncrementRequest(BaseModel):
    """递增请求模型"""
    key: str = Field(..., description="缓存键")
    amount: int = Field(default=1, description="递增量")

class CacheInfoResponse(BaseModel):
    """缓存信息响应模型"""
    status: str
    memory_items: int
    persistent_items: int
    total_items: int
    total_access_count: int
    type_statistics: Dict[str, int]
    configuration: Dict[str, Any]
    last_updated: str

class CacheStatsResponse(BaseModel):
    """缓存统计响应模型"""
    hit_rate: float
    miss_rate: float
    memory_usage: Dict[str, int]
    top_keys: List[Dict[str, Any]]
    expired_items_today: int

# API 端点实现
@router.post("/set", response_model=Dict[str, Any])
async def set_cache_value(request: SetCacheRequest):
    """SET命令：设置缓存值"""
    try:
        cache_service = get_cache_tools_service()
        success = cache_service.set(
            key=request.key,
            value=request.value,
            ttl=request.ttl,
            tags=request.tags
        )

        if not success:
            raise HTTPException(status_code=500, detail="缓存设置失败")

        logger.info(f"Cache SET: {sanitize_for_log(request.key)}")

        return {
            "status": "success",
            "message": "缓存值已成功设置",
            "key": request.key,
            "ttl": request.ttl,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set cache value: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"设置缓存失败: {str(e)}")

@router.get("/get/{key}", response_model=GetCacheResponse)
async def get_cache_value(key: str):
    """GET命令：获取缓存值"""
    try:
        cache_service = get_cache_tools_service()
        value = cache_service.get(key)

        if value is None:
            # 键不存在
            return GetCacheResponse(
                key=key,
                value=None,
                exists=False,
                ttl=-2,
                data_type="none",
                last_accessed="",
                access_count=0
            )

        # 获取额外信息
        ttl = cache_service.ttl(key)

        # 从内存缓存获取访问信息
        with cache_service._cache_lock:
            if key in cache_service._memory_cache:
                cache_item = cache_service._memory_cache[key]
                return GetCacheResponse(
                    key=key,
                    value=value,
                    exists=True,
                    ttl=ttl,
                    data_type=cache_item.data_type.value,
                    last_accessed=datetime.fromtimestamp(cache_item.last_accessed).isoformat(),
                    access_count=cache_item.access_count
                )

        return GetCacheResponse(
            key=key,
            value=value,
            exists=True,
            ttl=ttl,
            data_type="string",
            last_accessed=datetime.now().isoformat(),
            access_count=0
        )

    except Exception as e:
        logger.error(f"Failed to get cache value: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取缓存失败: {str(e)}")

@router.delete("/delete/{key}", response_model=Dict[str, Any])
async def delete_cache_key(key: str):
    """DEL命令：删除缓存键"""
    try:
        cache_service = get_cache_tools_service()
        success = cache_service.delete(key)

        if not success:
            raise HTTPException(status_code=404, detail=f"缓存键未找到: {key}")

        logger.info(f"Cache DEL: {sanitize_for_log(key)}")

        return {
            "status": "success",
            "message": "缓存键已成功删除",
            "key": key,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete cache key: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"删除缓存失败: {str(e)}")

@router.get("/exists/{key}", response_model=Dict[str, bool])
async def check_key_exists(key: str):
    """EXISTS命令：检查键是否存在"""
    try:
        cache_service = get_cache_tools_service()
        exists = cache_service.exists(key)

        return {
            "key": key,
            "exists": exists
        }
    except Exception as e:
        logger.error(f"Failed to check key existence: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"检查键存在性失败: {str(e)}")

@router.put("/expire", response_model=Dict[str, Any])
async def set_key_expiry(request: ExpireRequest):
    """EXPIRE命令：设置键的过期时间"""
    try:
        cache_service = get_cache_tools_service()
        success = cache_service.expire(request.key, request.ttl)

        if not success:
            raise HTTPException(status_code=404, detail=f"缓存键未找到: {request.key}")

        logger.info(f"Cache EXPIRE: {sanitize_for_log(request.key)} TTL={request.ttl}")

        return {
            "status": "success",
            "message": "过期时间已成功设置",
            "key": request.key,
            "ttl": request.ttl,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to set expiry: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"设置过期时间失败: {str(e)}")

@router.get("/ttl/{key}", response_model=Dict[str, int])
async def get_key_ttl(key: str):
    """TTL命令：获取键的剩余生存时间"""
    try:
        cache_service = get_cache_tools_service()
        ttl = cache_service.ttl(key)

        return {
            "key": key,
            "ttl": ttl
        }
    except Exception as e:
        logger.error(f"Failed to get TTL: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取TTL失败: {str(e)}")

@router.get("/keys", response_model=List[str])
async def get_matching_keys(
    pattern: str = FastAPIQuery(default="*", description="匹配模式，支持*通配符")
):
    """KEYS命令：获取匹配模式的键"""
    try:
        cache_service = get_cache_tools_service()
        keys = cache_service.keys(pattern)

        return keys
    except Exception as e:
        logger.error(f"Failed to get keys: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取键列表失败: {str(e)}")

@router.post("/mset", response_model=Dict[str, Any])
async def batch_set_values(request: BatchSetRequest):
    """MSET命令：批量设置键值对"""
    try:
        cache_service = get_cache_tools_service()
        success = cache_service.mset(request.key_values, request.ttl)

        logger.info(f"Cache MSET: {len(request.key_values)} keys")

        return {
            "status": "success" if success else "partial",
            "message": f"批量设置完成：{len(request.key_values)} 个键值对",
            "key_count": len(request.key_values),
            "ttl": request.ttl,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to batch set values: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"批量设置失败: {str(e)}")

@router.post("/mget", response_model=List[Any])
async def batch_get_values(request: BatchGetRequest):
    """MGET命令：批量获取多个键的值"""
    try:
        cache_service = get_cache_tools_service()
        values = cache_service.mget(request.keys)

        return values
    except Exception as e:
        logger.error(f"Failed to batch get values: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"批量获取失败: {str(e)}")

@router.post("/delete-batch", response_model=Dict[str, Any])
async def batch_delete_keys(request: DeleteKeysRequest):
    """批量删除多个键"""
    try:
        cache_service = get_cache_tools_service()

        success_count = 0
        failed_keys = []

        for key in request.keys:
            if cache_service.delete(key):
                success_count += 1
            else:
                failed_keys.append(key)

        logger.info(f"Cache batch delete: {success_count}/{len(request.keys)} keys deleted")

        return {
            "status": "completed",
            "message": f"批量删除完成：成功 {success_count} 个，失败 {len(failed_keys)} 个",
            "success_count": success_count,
            "failed_count": len(failed_keys),
            "failed_keys": failed_keys,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to batch delete keys: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")

@router.put("/incr", response_model=Dict[str, Any])
async def increment_value(request: IncrementRequest):
    """INCR命令：原子性递增"""
    try:
        cache_service = get_cache_tools_service()
        new_value = cache_service.incr(request.key, request.amount)

        if new_value is None:
            raise HTTPException(status_code=400, detail="无法递增非数值类型的值")

        logger.info(f"Cache INCR: {sanitize_for_log(request.key)} += {request.amount} = {new_value}")

        return {
            "status": "success",
            "message": "递增操作成功",
            "key": request.key,
            "amount": request.amount,
            "new_value": new_value,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to increment value: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"递增操作失败: {str(e)}")

@router.post("/flushall", response_model=Dict[str, Any])
async def flush_all_cache():
    """FLUSHALL命令：清空所有缓存"""
    try:
        cache_service = get_cache_tools_service()
        success = cache_service.flushall()

        if not success:
            raise HTTPException(status_code=500, detail="清空缓存失败")

        logger.info("Cache FLUSHALL: All cache cleared")

        return {
            "status": "success",
            "message": "所有缓存已清空",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to flush cache: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"清空缓存失败: {str(e)}")

@router.get("/info", response_model=CacheInfoResponse)
async def get_cache_info():
    """INFO命令：获取缓存系统信息"""
    try:
        cache_service = get_cache_tools_service()
        info = cache_service.info()

        return CacheInfoResponse(
            status=info["status"],
            memory_items=info["memory_items"],
            persistent_items=info["persistent_items"],
            total_items=info["total_items"],
            total_access_count=info["total_access_count"],
            type_statistics=info["type_statistics"],
            configuration=info["configuration"],
            last_updated=info["last_updated"]
        )
    except Exception as e:
        logger.error(f"Failed to get cache info: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取缓存信息失败: {str(e)}")

@router.get("/stats", response_model=Dict[str, Any])
async def get_cache_statistics():
    """获取缓存统计信息"""
    try:
        cache_service = get_cache_tools_service()

        with cache_service._cache_lock:
            memory_items = cache_service._memory_cache

            # 计算命中率等统计信息
            total_access = sum(item.access_count for item in memory_items.values())

            # 获取访问次数最多的键
            top_keys = sorted(
                [{"key": k, "access_count": v.access_count, "last_accessed": datetime.fromtimestamp(v.last_accessed).isoformat()}
                 for k, v in memory_items.items()],
                key=lambda x: x["access_count"],
                reverse=True
            )[:10]

            # 统计今日过期项（简化版本）
            expired_today = sum(1 for item in memory_items.values() if item.is_expired())

        return {
            "status": "success",
            "statistics": {
                "total_access_count": total_access,
                "memory_items": len(memory_items),
                "top_accessed_keys": top_keys,
                "expired_items": expired_today,
                "average_access_per_key": total_access / max(len(memory_items), 1)
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache statistics: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取缓存统计失败: {str(e)}")

@router.get("/status", response_model=Dict[str, Any])
async def get_cache_status():
    """获取缓存服务状态"""
    try:
        cache_service = get_cache_tools_service()
        info = cache_service.info()

        return {
            "status": "active",
            "service_name": "Cache Tools",
            "version": "1.0.0",
            "info": info,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cache status: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取缓存状态失败: {str(e)}")

# 配置管理API
@router.get("/configs", response_model=List[Dict[str, Any]])
async def get_cache_configs():
    """获取所有缓存配置"""
    try:
        cache_service = get_cache_tools_service()
        Query_obj = Query()
        configs = cache_service.config_table.all()

        return configs
    except Exception as e:
        logger.error(f"Failed to get cache configs: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取缓存配置失败: {str(e)}")

@router.put("/configs/{config_type}", response_model=Dict[str, Any])
async def update_cache_config(config_type: str, value: Any):
    """更新缓存配置"""
    try:
        cache_service = get_cache_tools_service()

        Query_obj = Query()
        existing = cache_service.config_table.get(Query_obj.config_type == config_type)

        if not existing:
            raise HTTPException(status_code=404, detail=f"配置项未找到: {config_type}")

        update_data = {
            "value": value,
            "updated_at": datetime.now().isoformat()
        }

        cache_service.config_table.update(update_data, Query_obj.config_type == config_type)

        logger.info(f"Updated cache config: {config_type} = {sanitize_for_log(str(value))}")

        return {
            "status": "success",
            "message": "缓存配置已更新",
            "config_type": config_type,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update cache config: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")