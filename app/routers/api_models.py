from typing import List, Optional
from fastapi import APIRouter, HTTPException
from app.models.schemas import ModelsResponse, ErrorResponse, ModelInfo, ModelsRequest, ModelBySlugRequest
from app.core.yaml_service import YAMLService

router = APIRouter()

@router.post(
    "/models", 
    response_model=ModelsResponse,
    summary="获取所有模型信息",
    description="获取 resources/models 目录及其子目录下的所有 YAML 文件信息，排除 customInstructions 字段"
)
async def get_models(request: ModelsRequest = ModelsRequest()) -> ModelsResponse:
    """获取所有模型信息"""
    try:
        # 加载所有模型数据
        models = YAMLService.load_all_models()
        
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
        
        return ModelsResponse(
            success=True,
            message="Models loaded successfully",
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
    """根据 slug 获取单个模型信息"""
    try:
        models = YAMLService.load_all_models()
        
        # 查找匹配的模型
        for model in models:
            if model.slug == request.slug:
                return model
        
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
    """获取模型分类列表"""
    try:
        models = YAMLService.load_all_models()
        
        categories = {
            "core": [],
            "coder": []
        }
        
        for model in models:
            if "/coder/" in model.file_path:
                categories["coder"].append({
                    "slug": model.slug,
                    "name": model.name,
                    "description": model.description
                })
            else:
                categories["core"].append({
                    "slug": model.slug,
                    "name": model.name,
                    "description": model.description
                })
        
        return {
            "success": True,
            "message": "Categories loaded successfully",
            "data": categories,
            "stats": {
                "total": len(models),
                "core": len(categories["core"]),
                "coder": len(categories["coder"])
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load categories: {str(e)}"
        )