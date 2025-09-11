from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.models.schemas import ModelsResponse, ErrorResponse, ModelInfo, ModelsRequest, ModelBySlugRequest
from app.core.database_service_lite import get_lite_database_service

router = APIRouter()

@router.post(
    "/models", 
    response_model=ModelsResponse,
    summary="获取所有模型信息（优化版本）",
    description="高性能获取 resources/models 目录下的所有模型信息，使用智能缓存和懒加载技术"
)
async def get_models_optimized(request: ModelsRequest = ModelsRequest()) -> ModelsResponse:
    """获取所有模型信息（性能优化版本）"""
    try:
        # 使用轻量级数据库服务
        db_service = get_lite_database_service()
        
        # 获取所有模型数据（带缓存）
        models_data = db_service.get_models_data()
        
        # 转换为ModelInfo对象（优化内存使用）
        models = []
        for data in models_data:
            model_info = ModelInfo(
                slug=data.get('slug', ''),
                name=data.get('name', ''),
                roleDefinition=data.get('roleDefinition', ''),
                whenToUse=data.get('whenToUse', ''),
                description=data.get('description', ''),
                groups=data.get('groups', []),
                file_path=data.get('file_path', ''),
                file_size=data.get('file_size'),
                last_modified=data.get('last_modified')
            )
            models.append(model_info)
        
        # 高性能过滤
        filtered_models = models
        
        # 按 slug 过滤
        if request.slug:
            filtered_models = [m for m in filtered_models if m.slug == request.slug]
        
        # 按分类过滤 (基于文件路径)
        if request.category:
            if request.category == "coder":
                filtered_models = [m for m in filtered_models if "/coder/" in m.file_path]
            elif request.category == "core":
                filtered_models = [m for m in filtered_models if "/coder/" not in m.file_path]
        
        # 按关键词搜索（优化搜索算法）
        if request.search:
            search_lower = request.search.lower()
            filtered_models = [
                m for m in filtered_models 
                if (search_lower in m.name.lower() or 
                    search_lower in m.description.lower() or
                    search_lower in m.slug.lower())
            ]
        
        # 按 slug 排序（已在数据库层预排序）
        filtered_models.sort(key=lambda x: x.slug)
        
        return ModelsResponse(
            success=True,
            message="Models loaded successfully with optimized caching",
            data=filtered_models,
            total=len(filtered_models)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load models: {str(e)}"
        )


@router.post(
    "/models/by-slug",
    response_model=ModelInfo,
    summary="获取单个模型信息（优化版本）",
    description="高性能根据 slug 获取指定模型的详细信息，使用专门的单模型缓存"
)
async def get_model_by_slug_optimized(request: ModelBySlugRequest) -> ModelInfo:
    """根据 slug 获取单个模型信息（性能优化版本）"""
    try:
        # 使用轻量级数据库服务的优化查找
        db_service = get_lite_database_service()
        model_data = db_service.get_model_by_slug(request.slug)
        
        if not model_data:
            raise HTTPException(
                status_code=404,
                detail=f"Model with slug '{request.slug}' not found"
            )
        
        return ModelInfo(
            slug=model_data.get('slug', ''),
            name=model_data.get('name', ''),
            roleDefinition=model_data.get('roleDefinition', ''),
            whenToUse=model_data.get('whenToUse', ''),
            description=model_data.get('description', ''),
            groups=model_data.get('groups', []),
            file_path=model_data.get('file_path', ''),
            file_size=model_data.get('file_size'),
            last_modified=model_data.get('last_modified')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {str(e)}"
        )


@router.post(
    "/models/by-group",
    response_model=ModelsResponse,
    summary="按组获取模型（优化版本）",
    description="高性能按组获取模型信息，使用分组缓存"
)
async def get_models_by_group(group: str) -> ModelsResponse:
    """按组获取模型信息（性能优化版本）"""
    try:
        # 使用轻量级数据库服务的分组查询
        db_service = get_lite_database_service()
        models_data = db_service.get_models_by_group(group)
        
        # 转换为ModelInfo对象
        models = []
        for data in models_data:
            model_info = ModelInfo(
                slug=data.get('slug', ''),
                name=data.get('name', ''),
                roleDefinition=data.get('roleDefinition', ''),
                whenToUse=data.get('whenToUse', ''),
                description=data.get('description', ''),
                groups=data.get('groups', []),
                file_path=data.get('file_path', ''),
                file_size=data.get('file_size'),
                last_modified=data.get('last_modified')
            )
            models.append(model_info)
        
        return ModelsResponse(
            success=True,
            message=f"Models loaded successfully for group '{group}'",
            data=models,
            total=len(models)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load models for group '{group}': {str(e)}"
        )


@router.post(
    "/models/categories/list",
    summary="获取所有模型分类（优化版本）",
    description="高性能获取可用的模型分类列表，使用分类缓存"
)
async def get_model_categories_optimized():
    """获取模型分类列表（性能优化版本）"""
    try:
        # 使用轻量级数据库服务
        db_service = get_lite_database_service()
        models_data = db_service.get_models_data()
        
        categories = {
            "core": [],
            "coder": []
        }
        
        # 高效分类处理
        for data in models_data:
            model_info = {
                "slug": data.get('slug', ''),
                "name": data.get('name', ''),
                "description": data.get('description', '')[:50]  # 截断描述以节省内存
            }
            
            file_path = data.get('file_path', '')
            if "/coder/" in file_path:
                categories["coder"].append(model_info)
            else:
                categories["core"].append(model_info)
        
        total_models = len(models_data)
        
        return {
            "success": True,
            "message": "Categories loaded successfully with optimized caching",
            "data": categories,
            "stats": {
                "total": total_models,
                "core": len(categories["core"]),
                "coder": len(categories["coder"])
            },
            "performance": {
                "cached": True,
                "optimization_level": "high"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load categories: {str(e)}"
        )


@router.post(
    "/models/refresh-cache",
    summary="刷新模型缓存（优化版本）",
    description="手动刷新模型缓存，清除所有缓存并重新加载"
)
async def refresh_models_cache():
    """刷新模型缓存"""
    try:
        db_service = get_lite_database_service()
        result = db_service.refresh_models_cache()
        
        return {
            "success": True,
            "message": "Models cache refreshed successfully",
            "data": result,
            "performance": {
                "cache_cleared": True,
                "optimization_level": "high"
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh cache: {str(e)}"
        )


@router.get(
    "/models/cache-stats",
    summary="获取缓存统计信息",
    description="获取模型缓存的性能统计信息"
)
async def get_cache_stats():
    """获取缓存统计信息"""
    try:
        db_service = get_lite_database_service()
        status = db_service.get_status()
        
        return {
            "success": True,
            "message": "Cache statistics retrieved successfully",
            "data": {
                "service_type": status.get("service_type"),
                "memory_cache_size": status.get("memory_cache_size", 0),
                "lru_cache_hits": status.get("lru_cache_hits", 0),
                "lru_cache_misses": status.get("lru_cache_misses", 0),
                "lru_cache_size": status.get("lru_cache_size", 0),
                "cache_hit_ratio": (
                    status.get("lru_cache_hits", 0) / 
                    max(1, status.get("lru_cache_hits", 0) + status.get("lru_cache_misses", 0))
                )
            },
            "performance": {
                "optimized": True,
                "features": ["lazy_loading", "lru_cache", "memory_cache"]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get cache stats: {str(e)}"
        )