from fastapi import APIRouter, HTTPException
from app.models.schemas import CommandsResponse
from app.core.commands_service import CommandsService

router = APIRouter()

@router.post(
    "/commands",
    response_model=CommandsResponse,
    summary="获取 Commands 目录文件信息",
    description="获取 resources/commands 目录下所有文件的 metadata 信息"
)
async def get_commands() -> CommandsResponse:
    """获取 commands 目录下所有文件的 metadata 信息"""
    try:
        metadata_list = CommandsService.get_commands_metadata()
        
        # Convert FileMetadata objects to dictionaries
        data_dicts = [item.model_dump() for item in metadata_list]
        
        return CommandsResponse(
            success=True,
            message="Commands loaded successfully",
            data=data_dicts,
            count=len(data_dicts),
            total=len(data_dicts)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load commands: {str(e)}"
        )