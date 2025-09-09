from fastapi import APIRouter, HTTPException, Path
from app.models.schemas import RulesResponse
from app.core.rules_service import RulesService

router = APIRouter()

@router.get(
    "/rules/{slug}",
    response_model=RulesResponse,
    summary="根据 slug 获取 Rules 文件信息",
    description="根据 slug 查找对应的 rules 目录下的所有文件 metadata。例如 slug=code-go 会依次查找 rules-code-go, rules-code, rules 目录"
)
async def get_rules_by_slug(
    slug: str = Path(..., description="模式标识符，用于确定查找的 rules 目录", example="code-go")
) -> RulesResponse:
    """根据 slug 获取 rules 文件的 metadata"""
    try:
        # 获取搜索结果
        searched_dirs, found_dirs, metadata_list = RulesService.get_rules_by_slug(slug)
        
        return RulesResponse(
            success=True,
            message=f"Rules loaded successfully for slug '{slug}'",
            slug=slug,
            searched_directories=searched_dirs,
            found_directories=found_dirs,
            data=metadata_list,
            total=len(metadata_list)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load rules for slug '{slug}': {str(e)}"
        )


@router.get(
    "/rules",
    summary="获取所有可用的 Rules 目录",
    description="列出 resources 目录下所有的 rules-* 目录"
)
async def list_available_rules():
    """获取所有可用的 rules 目录"""
    try:
        from pathlib import Path
        from app.core.config import PROJECT_ROOT
        
        resources_dir = PROJECT_ROOT / "resources"
        rules_dirs = []
        
        # 查找所有 rules-* 目录
        for item in resources_dir.iterdir():
            if item.is_dir() and item.name.startswith('rules'):
                rules_dirs.append({
                    "name": item.name,
                    "full_path": str(item),
                    "exists": True
                })
        
        # 按名称排序
        rules_dirs.sort(key=lambda x: x["name"])
        
        return {
            "success": True,
            "message": "Available rules directories loaded successfully",
            "data": rules_dirs,
            "total": len(rules_dirs)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load available rules directories: {str(e)}"
        )