from fastapi import APIRouter, HTTPException
from app.models.schemas import HookResponse, HookInfo
from app.core.hooks_service import HooksService

router = APIRouter()

@router.post(
    "/hooks/before",
    response_model=HookResponse,
    summary="获取 Before Hook",
    description="获取 before.md 文件的完整内容，包括 frontmatter 和 markdown 内容"
)
async def get_before_hook() -> HookResponse:
    """获取 before hook 信息"""
    try:
        hook_info = HooksService.get_before_hook()
        return HookResponse(
            success=True,
            message="Before hook loaded successfully",
            data=hook_info
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load before hook: {str(e)}"
        )


@router.post(
    "/hooks/after",
    response_model=HookResponse,
    summary="获取 After Hook",
    description="获取 after.md 文件的完整内容，包括 frontmatter 和 markdown 内容"
)
async def get_after_hook() -> HookResponse:
    """获取 after hook 信息"""
    try:
        hook_info = HooksService.get_after_hook()
        return HookResponse(
            success=True,
            message="After hook loaded successfully",
            data=hook_info
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load after hook: {str(e)}"
        )


@router.post(
    "/hooks",
    summary="获取所有 Hooks 信息",
    description="获取 before.md 和 after.md 两个文件的信息"
)
async def get_all_hooks():
    """获取所有 hooks 信息"""
    try:
        before_hook = HooksService.get_before_hook()
        after_hook = HooksService.get_after_hook()
        
        return {
            "success": True,
            "message": "All hooks loaded successfully",
            "data": {
                "before": before_hook,
                "after": after_hook
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load hooks: {str(e)}"
        )