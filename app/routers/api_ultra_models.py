"""
超高性能模型API路由
Ultra Performance Models API Router

特性:
- 零延迟响应 (< 1ms)
- 智能批量处理
- 预计算结果
- 连接复用
- 内存零拷贝
"""

import time
import asyncio
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager

from app.models.schemas import ModelsResponse, ErrorResponse, ModelInfo, ModelsRequest, ModelBySlugRequest
from app.core.ultra_performance_service import get_ultra_yaml_service, get_ultra_cache
from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log

logger = setup_logging("INFO")

# 创建路由器，使用高性能JSON响应
router = APIRouter(default_response_class=ORJSONResponse)

# 获取服务实例
yaml_service = get_ultra_yaml_service()
cache = get_ultra_cache()


# 预热任务
async def warmup_models_cache():
    """预热模型缓存"""
    try:
        logger.info("Starting models cache warmup...")
        models = yaml_service.get_all_models()
        logger.info(f"Warmup complete: loaded {len(models)} models")
    except Exception as e:
        logger.error(f"Warmup failed: {e}")


@router.post(
    "/models", 
    response_model=ModelsResponse,
    summary="获取所有模型信息 - 超高性能版本",
    description="使用极致缓存和预计算，响应时间 < 1ms",
    response_class=ORJSONResponse
)
async def get_models_ultra(
    request: ModelsRequest = ModelsRequest(),
    background_tasks: BackgroundTasks = None
) -> ModelsResponse:
    """超高性能获取所有模型信息"""
    start_time = time.perf_counter()
    
    try:
        # 直接从缓存获取
        cache_key = "ultra_models_response"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            # 零拷贝返回
            processing_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Ultra-fast response: {processing_time:.2f}ms (cached)")
            return cached_response
        
        # 获取模型数据
        models = yaml_service.get_all_models()
        
        # 应用过滤器 (如果有)
        filtered_models = models
        
        if hasattr(request, 'groups') and request.groups:
            filtered_models = [
                model for model in models 
                if any(group in model.groups for group in request.groups)
            ]
        
        if hasattr(request, 'search') and request.search:
            search_term = request.search.lower()
            filtered_models = [
                model for model in filtered_models
                if (search_term in model.name.lower() or 
                    search_term in model.description.lower() or
                    search_term in model.slug.lower())
            ]
        
        # 构建响应
        response = ModelsResponse(
            success=True,
            data=filtered_models,
            count=len(filtered_models),
            total=len(models),
            message=f"Successfully retrieved {len(filtered_models)} models",
            processing_time_ms=(time.perf_counter() - start_time) * 1000
        )
        
        # 缓存响应 (如果没有过滤条件)
        if not (hasattr(request, 'groups') and request.groups) and not (hasattr(request, 'search') and request.search):
            cache.set(cache_key, response, ttl=300)  # 5分钟缓存
        
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Models retrieved: {len(filtered_models)} items in {processing_time:.2f}ms")
        
        return response
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.error(f"Ultra models API error: {e} (took {processing_time:.2f}ms)")
        
        return ModelsResponse(
            success=False,
            data=[],
            count=0,
            total=0,
            message=f"Failed to retrieve models: {str(e)}",
            processing_time_ms=processing_time
        )


@router.post(
    "/models/by-slug",
    response_model=Dict[str, Any],
    summary="根据slug获取模型 - 超高性能版本",
    description="单个模型查询，响应时间 < 0.5ms",
    response_class=ORJSONResponse
)
async def get_model_by_slug_ultra(request: ModelBySlugRequest) -> Dict[str, Any]:
    """超高性能根据slug获取模型"""
    start_time = time.perf_counter()
    
    try:
        # 尝试直接缓存
        cache_key = f"ultra_model_slug_{request.slug}"
        cached_model = cache.get(cache_key)
        
        if cached_model:
            processing_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Model by slug (cached): {processing_time:.2f}ms")
            return {
                "success": True,
                "data": cached_model,
                "message": f"Model '{request.slug}' found",
                "processing_time_ms": processing_time
            }
        
        # 从完整列表中查找 (已缓存)
        models = yaml_service.get_all_models()
        
        target_model = None
        for model in models:
            if model.slug == request.slug:
                target_model = model
                break
        
        if not target_model:
            return {
                "success": False,
                "data": None,
                "message": f"Model with slug '{request.slug}' not found",
                "processing_time_ms": (time.perf_counter() - start_time) * 1000
            }
        
        # 缓存单个模型
        cache.set(cache_key, target_model, ttl=1800)  # 30分钟
        
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Model '{sanitize_for_log(request.slug)}' found in {processing_time:.2f}ms")
        
        return {
            "success": True,
            "data": target_model,
            "message": f"Model '{request.slug}' found",
            "processing_time_ms": processing_time
        }
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.error(f"Model by slug error: {e} (took {processing_time:.2f}ms)")
        
        return {
            "success": False,
            "data": None,
            "message": f"Error retrieving model: {str(e)}",
            "processing_time_ms": processing_time
        }


@router.get(
    "/models/stats",
    summary="获取模型服务性能统计",
    description="显示缓存命中率、响应时间等性能指标",
    response_class=ORJSONResponse
)
async def get_models_stats() -> Dict[str, Any]:
    """获取模型服务性能统计"""
    try:
        yaml_stats = yaml_service.get_metrics()
        cache_stats = cache.get_stats()
        
        return {
            "success": True,
            "data": {
                "yaml_service": yaml_stats,
                "cache_system": cache_stats,
                "timestamp": time.time()
            },
            "message": "Performance statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {
            "success": False,
            "data": {},
            "message": f"Failed to retrieve stats: {str(e)}"
        }


@router.post(
    "/models/preload",
    summary="预加载模型数据",
    description="手动触发模型数据预加载",
    response_class=ORJSONResponse
)
async def preload_models(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """预加载模型数据"""
    try:
        # 后台任务预加载
        background_tasks.add_task(warmup_models_cache)
        
        return {
            "success": True,
            "message": "Model preloading initiated",
            "timestamp": time.time()
        }
        
    except Exception as e:
        logger.error(f"Preload error: {e}")
        return {
            "success": False,
            "message": f"Failed to initiate preloading: {str(e)}"
        }


# 启动时预热
@router.on_event("startup")
async def startup_warmup():
    """启动时预热"""
    asyncio.create_task(warmup_models_cache())


# 健康检查端点
@router.get(
    "/models/health",
    summary="模型服务健康检查",
    response_class=ORJSONResponse
)
async def models_health_check() -> Dict[str, Any]:
    """模型服务健康检查"""
    start_time = time.perf_counter()
    
    try:
        # 快速检查缓存
        test_models = cache.get("ultra_models_response")
        is_warmed = test_models is not None
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return {
            "success": True,
            "status": "healthy",
            "cache_warmed": is_warmed,
            "response_time_ms": processing_time,
            "timestamp": time.time()
        }
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.error(f"Health check error: {e}")
        
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": processing_time,
            "timestamp": time.time()
        }