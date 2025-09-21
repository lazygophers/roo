"""
缓存工具 API 路由
MCP 工具的缓存配置接口
"""

from fastapi import APIRouter
from typing import Dict, Any

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log

logger = setup_logging()

router = APIRouter(prefix="/cache-tools", tags=["cache-tools"])

@router.get("/status")
async def get_cache_tools_status():
    """获取缓存工具状态（占位接口）"""
    try:
        return {
            "success": True,
            "message": "Cache tools status retrieved successfully",
            "data": {
                "status": "active",
                "backend_type": "diskcache",
                "tools_available": True
            }
        }
    except Exception as e:
        logger.error(f"Failed to get cache tools status: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get cache tools status",
            "error": str(e)
        }