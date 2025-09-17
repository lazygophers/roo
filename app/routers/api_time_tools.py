"""
时间工具集配置管理 API
Time Tools Configuration Management API

提供时间工具的全局配置管理接口，包括时区设置、显示选项等。
类似于文件安全配置系统的API设计。
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from pydantic import BaseModel

from app.core.time_tools_service import get_time_tools_service
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging

logger = setup_logging()

router = APIRouter(prefix="/time-tools", tags=["time-tools"])

class TimeConfigRequest(BaseModel):
    """时间配置更新请求"""
    value: Any

class TimeConfigResponse(BaseModel):
    """时间配置响应"""
    status: str
    message: str = ""
    data: Dict[str, Any] = {}

@router.get("/status")
async def get_time_tools_status():
    """获取时间工具配置状态"""
    try:
        time_service = get_time_tools_service()
        status_info = time_service.get_status_info()
        
        return {
            "status": "success",
            "message": "Time tools status retrieved successfully",
            "data": status_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get time tools status: {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500, 
            detail="Failed to get time tools status"
        )

@router.get("/configs")
async def get_all_time_configs():
    """获取所有时间工具配置"""
    try:
        time_service = get_time_tools_service()
        configs = time_service.get_all_configs()
        
        return {
            "status": "success",
            "message": "Time configurations retrieved successfully",
            "data": {
                "configs": configs,
                "total": len(configs)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get time configs: {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get time configurations"
        )

@router.get("/configs/{config_type}")
async def get_time_config(config_type: str):
    """获取指定类型的时间工具配置"""
    try:
        # 验证配置类型
        valid_types = ["default_timezone", "display_timezone_info", "auto_detect_timezone"]
        if config_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid config type. Valid types: {', '.join(valid_types)}"
            )
        
        time_service = get_time_tools_service()
        config = time_service.get_config(config_type)
        
        if not config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration '{config_type}' not found"
            )
        
        return {
            "status": "success",
            "message": f"Configuration '{config_type}' retrieved successfully",
            "data": config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get time config '{config_type}': {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get time configuration"
        )

@router.put("/configs/{config_type}")
async def update_time_config(config_type: str, request: TimeConfigRequest):
    """更新指定类型的时间工具配置"""
    try:
        # 验证配置类型
        valid_types = ["default_timezone", "display_timezone_info", "auto_detect_timezone"]
        if config_type not in valid_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid config type. Valid types: {', '.join(valid_types)}"
            )
        
        time_service = get_time_tools_service()
        
        # 检查配置是否存在
        existing_config = time_service.get_config(config_type)
        if not existing_config:
            raise HTTPException(
                status_code=404,
                detail=f"Configuration '{config_type}' not found"
            )
        
        # 更新配置
        success = time_service.update_config(config_type, request.value)
        
        if not success:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to update configuration '{config_type}'. Invalid value or validation failed."
            )
        
        # 获取更新后的配置
        updated_config = time_service.get_config(config_type)
        
        logger.info(f"Updated time config: {config_type} = {sanitize_for_log(str(request.value))}")
        
        return {
            "status": "success",
            "message": f"Configuration '{config_type}' updated successfully",
            "data": updated_config
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update time config '{config_type}': {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update time configuration"
        )

@router.get("/timezones")
async def get_available_timezones():
    """获取可用时区列表"""
    try:
        time_service = get_time_tools_service()
        timezones = time_service.get_available_timezones()
        
        return {
            "status": "success",
            "message": "Available timezones retrieved successfully",
            "data": {
                "timezones": timezones,
                "total": len(timezones)
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get available timezones: {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get available timezones"
        )

@router.post("/reload")
async def reload_time_tools_config():
    """重新加载时间工具配置"""
    try:
        time_service = get_time_tools_service()
        
        # 重新初始化默认配置
        time_service._initialize_default_config()
        
        # 获取最新状态
        status_info = time_service.get_status_info()
        
        logger.info("Time tools configuration reloaded")
        
        return {
            "status": "success", 
            "message": "Time tools configuration reloaded successfully",
            "data": status_info
        }
        
    except Exception as e:
        logger.error(f"Failed to reload time tools config: {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500,
            detail="Failed to reload time tools configuration"
        )

@router.get("/current-time")
async def get_current_time_with_config():
    """根据当前配置获取时间信息"""
    try:
        time_service = get_time_tools_service()
        
        # 获取配置的时区
        tz_obj = time_service.get_timezone_object()
        show_tz_info = time_service.should_display_timezone_info()
        default_tz_str = time_service.get_default_timezone()
        
        # 生成时间信息
        if tz_obj:
            from datetime import datetime
            now = datetime.now(tz_obj)
            tz_name = str(tz_obj)
        else:
            from datetime import datetime
            now = datetime.now()
            tz_name = str(now.astimezone().tzinfo)
        
        unix_timestamp = int(now.timestamp())
        
        time_info = {
            "iso_format": now.isoformat(),
            "unix_timestamp": unix_timestamp,
            "formatted_time": now.strftime('%Y-%m-%d %H:%M:%S'),
            "timezone_configured": default_tz_str,
            "timezone_display": tz_name if show_tz_info else None,
            "show_timezone_info": show_tz_info
        }
        
        return {
            "status": "success",
            "message": "Current time retrieved with configuration",
            "data": time_info
        }
        
    except Exception as e:
        logger.error(f"Failed to get current time with config: {sanitize_for_log(str(e))}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get current time with configuration"
        )