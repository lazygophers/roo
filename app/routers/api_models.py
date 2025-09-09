from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ModelsResponse, ErrorResponse, ModelInfo
from app.core.yaml_service import YAMLService

router = APIRouter()

@router.get(
    "/models", 
    response_model=ModelsResponse,
    summary="获取所有模型信息",
    description="获取 resources/models 目录及其子目录下的所有 YAML 文件信息，排除 customInstructions 字段"
)
async def get_models(
    slug: Optional[str] = Query(None, description="按 slug 过滤模型"),
    category: Optional[str] = Query(None, description="按分类过滤模型 (coder/core)"),
    search: Optional[str] = Query(None, description="在 name 和 description 中搜索关键词")
) -> ModelsResponse:
    """获取所有模型信息"""
    try:
        # 加载所有模型数据
        models = YAMLService.load_all_models()
        
        # 应用过滤器
        filtered_models = models
        
        # 按 slug 过滤
        if slug:
            filtered_models = [m for m in filtered_models if m.slug == slug]
        
        # 按分类过滤 (基于文件路径)
        if category:
            if category == "coder":
                filtered_models = [m for m in filtered_models if "/coder/" in m.file_path]
            elif category == "core":
                filtered_models = [m for m in filtered_models if "/coder/" not in m.file_path]
        
        # 按关键词搜索
        if search:
            search_lower = search.lower()
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


@router.get(
    "/models/{slug}",
    response_model=ModelInfo,
    summary="获取单个模型信息",
    description="根据 slug 获取指定模型的详细信息"
)
async def get_model_by_slug(slug: str) -> ModelInfo:
    """根据 slug 获取单个模型信息"""
    try:
        models = YAMLService.load_all_models()
        
        # 查找匹配的模型
        for model in models:
            if model.slug == slug:
                return model
        
        raise HTTPException(
            status_code=404,
            detail=f"Model with slug '{slug}' not found"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load model: {str(e)}"
        )


@router.get(
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