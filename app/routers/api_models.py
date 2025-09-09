from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.models.schemas import ModelsResponse, ErrorResponse, ModelInfo, ModelsRequest, ModelBySlugRequest
from app.core.yaml_service import YAMLService
from app.core.database_service import get_database_service

router = APIRouter()

@router.post(
    "/models", 
    response_model=ModelsResponse,
    summary="获取所有模型信息",
    description="获取 resources/models 目录及其子目录下的所有 YAML 文件信息，排除 customInstructions 字段"
)
async def get_models(request: ModelsRequest = ModelsRequest()) -> ModelsResponse:
    """获取所有模型信息（使用数据库缓存）"""
    try:
        # 从数据库缓存获取数据
        db_service = get_database_service()
        cached_models = db_service.get_cached_data("models")
        
        # 转换为ModelInfo对象
        models = []
        for file_data in cached_models:
            content = file_data.get('content', {})
            if content and isinstance(content, dict):
                model_info = ModelInfo(
                    slug=content.get('slug', ''),
                    name=content.get('name', ''),
                    roleDefinition=content.get('roleDefinition', ''),
                    whenToUse=content.get('whenToUse', ''),
                    description=content.get('description', ''),
                    groups=content.get('groups', []),
                    file_path=file_data.get('file_path', '')
                )
                models.append(model_info)
        
        # 应用过滤器
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
        
        # 按关键词搜索
        if request.search:
            search_lower = request.search.lower()
            filtered_models = [
                m for m in filtered_models 
                if search_lower in m.name.lower() or search_lower in m.description.lower()
            ]
        
        # 按 slug 排序
        filtered_models.sort(key=lambda x: x.slug)
        
        return ModelsResponse(
            success=True,
            message="Models loaded successfully from cache",
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
    summary="获取单个模型信息",
    description="根据 slug 获取指定模型的详细信息"
)
async def get_model_by_slug(request: ModelBySlugRequest) -> ModelInfo:
    """根据 slug 获取单个模型信息（使用数据库缓存）"""
    try:
        # 从数据库缓存获取数据
        db_service = get_database_service()
        cached_models = db_service.get_cached_data("models")
        
        # 查找匹配的模型
        for file_data in cached_models:
            content = file_data.get('content', {})
            if content and isinstance(content, dict) and content.get('slug') == request.slug:
                return ModelInfo(
                    slug=content.get('slug', ''),
                    name=content.get('name', ''),
                    roleDefinition=content.get('roleDefinition', ''),
                    whenToUse=content.get('whenToUse', ''),
                    description=content.get('description', ''),
                    groups=content.get('groups', []),
                    file_path=file_data.get('file_path', '')
                )
        
        raise HTTPException(
            status_code=404,
            detail=f"Model with slug '{request.slug}' not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {str(e)}"
        )


@router.post(
    "/models/categories/list",
    summary="获取所有模型分类",
    description="获取可用的模型分类列表"
)
async def get_model_categories():
    """获取模型分类列表（使用数据库缓存）"""
    try:
        # 从数据库缓存获取数据
        db_service = get_database_service()
        cached_models = db_service.get_cached_data("models")
        
        categories = {
            "core": [],
            "coder": []
        }
        
        for file_data in cached_models:
            content = file_data.get('content', {})
            if content and isinstance(content, dict):
                file_path = file_data.get('file_path', '')
                model_data = {
                    "slug": content.get('slug', ''),
                    "name": content.get('name', ''),
                    "description": content.get('description', '')
                }
                
                if "/coder/" in file_path:
                    categories["coder"].append(model_data)
                else:
                    categories["core"].append(model_data)
        
        total_models = len(cached_models)
        
        return {
            "success": True,
            "message": "Categories loaded successfully from cache",
            "data": categories,
            "stats": {
                "total": total_models,
                "core": len(categories["core"]),
                "coder": len(categories["coder"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load categories: {str(e)}"
        )