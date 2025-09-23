"""
缓存工具 API 路由
MCP 工具的缓存配置接口
"""

from fastapi import APIRouter
from typing import Dict, Any

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.json_file_service import get_json_file_service

logger = setup_logging()

router = APIRouter(prefix="/cache-tools", tags=["cache-tools"])

@router.get("/status")
async def get_cache_tools_status():
    """获取缓存工具状态"""
    try:
        json_service = get_json_file_service()

        return {
            "success": True,
            "message": "Cache tools status retrieved successfully",
            "data": {
                "status": "active",
                "backend_type": "json_files",
                "json_export_enabled": True,
                "json_cache_dir": str(json_service.json_cache_dir),
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

@router.post("/export-json")
async def export_all_caches_to_json():
    """导出所有缓存数据到JSON文件"""
    try:
        json_service = get_json_file_service()

        # 使用新的同步方法来重新扫描和导出
        results = json_service.sync_all_configs()

        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        return {
            "success": True,
            "message": f"JSON export completed: {success_count}/{total_count} configs exported successfully",
            "data": {
                "export_results": results,
                "success_count": success_count,
                "total_count": total_count,
                "export_directory": str(json_service.json_cache_dir)
            }
        }
    except Exception as e:
        logger.error(f"Failed to export caches to JSON: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to export caches to JSON",
            "error": str(e)
        }

@router.get("/json-summary")
async def get_json_cache_summary():
    """获取JSON缓存汇总信息"""
    try:
        json_service = get_json_file_service()

        summary = json_service.get_all_stats()

        return {
            "success": True,
            "message": "JSON cache summary retrieved successfully",
            "data": summary
        }
    except Exception as e:
        logger.error(f"Failed to get JSON cache summary: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get JSON cache summary",
            "error": str(e)
        }

@router.get("/json/{config_name}")
async def get_json_cache_data(config_name: str):
    """获取指定配置的JSON缓存数据"""
    try:
        json_service = get_json_file_service()

        cache_data = json_service._read_json_cache(config_name)

        if cache_data is None:
            return {
                "success": False,
                "message": f"JSON cache not found for config: {config_name}",
                "error": "Cache file not found"
            }

        return {
            "success": True,
            "message": f"JSON cache data retrieved for config: {config_name}",
            "data": cache_data
        }
    except Exception as e:
        logger.error(f"Failed to get JSON cache data for {sanitize_for_log(config_name)}: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": f"Failed to get JSON cache data for config: {config_name}",
            "error": str(e)
        }

@router.post("/refresh")
async def refresh_all_caches():
    """刷新所有缓存（重新扫描资源文件）"""
    try:
        json_service = get_json_file_service()

        # 重新同步所有配置
        results = json_service.sync_all_configs()

        success_count = sum(1 for success in results.values() if success)
        total_count = len(results)

        return {
            "success": True,
            "message": f"Cache refresh completed: {success_count}/{total_count} configs refreshed successfully",
            "data": {
                "refresh_results": results,
                "success_count": success_count,
                "total_count": total_count,
                "cache_directory": str(json_service.json_cache_dir)
            }
        }
    except Exception as e:
        logger.error(f"Failed to refresh caches: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to refresh caches",
            "error": str(e)
        }

@router.post("/refresh/{config_name}")
async def refresh_specific_cache(config_name: str):
    """刷新指定配置的缓存"""
    try:
        json_service = get_json_file_service()

        # 刷新指定配置
        success = json_service.sync_config(config_name)

        if success:
            stats = json_service.get_config_stats(config_name)
            return {
                "success": True,
                "message": f"Cache refreshed successfully for config: {config_name}",
                "data": {
                    "config_name": config_name,
                    "stats": stats
                }
            }
        else:
            return {
                "success": False,
                "message": f"Failed to refresh cache for config: {config_name}",
                "error": "Sync operation failed"
            }
    except Exception as e:
        logger.error(f"Failed to refresh cache for {sanitize_for_log(config_name)}: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": f"Failed to refresh cache for config: {config_name}",
            "error": str(e)
        }