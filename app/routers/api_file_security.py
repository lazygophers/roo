"""
文件安全配置 API 路由
提供文件工具集路径白名单的 CRUD 操作接口
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.file_security_service import get_file_security_service
from app.core.file_security import get_file_security_manager
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging

logger = setup_logging("INFO")
router = APIRouter(prefix="/file-security", tags=["File Security"])

# Pydantic 模型定义
class PathConfigRequest(BaseModel):
    """路径配置请求模型"""
    paths: List[str] = Field(default=[], description="路径列表（空列表表示允许所有路径）")
    
class PathConfigResponse(BaseModel):
    """路径配置响应模型"""
    id: str
    config_type: str
    name: str
    description: str
    paths: List[str]
    enabled: bool
    created_at: str
    updated_at: str
    metadata: Dict[str, Any] = {}

class LimitConfigRequest(BaseModel):
    """限制配置请求模型"""
    value: int = Field(..., ge=0, description="限制值，必须非负")

class LimitConfigResponse(BaseModel):
    """限制配置响应模型"""
    id: str
    limit_type: str
    name: str
    value: int
    description: str
    enabled: bool
    created_at: str
    updated_at: str

class SecuritySummaryResponse(BaseModel):
    """安全配置总览响应模型"""
    path_configs: Dict[str, Dict[str, Any]]
    limit_configs: Dict[str, Dict[str, Any]]
    total_paths: int
    enabled_path_configs: int
    last_updated: str

# API 端点实现
@router.get("/status", response_model=Dict[str, Any])
async def get_security_status():
    """获取文件安全配置状态"""
    try:
        file_security_manager = get_file_security_manager()
        security_info = file_security_manager.get_security_info()
        
        return {
            "status": "success",
            "data": security_info
        }
    except Exception as e:
        logger.error(f"Failed to get security status: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取安全状态失败: {str(e)}")

@router.get("/paths", response_model=List[PathConfigResponse])
async def get_path_configs(enabled_only: bool = True):
    """获取所有路径配置"""
    try:
        security_service = get_file_security_service()
        configs = security_service.get_all_path_configs(enabled_only=enabled_only)
        
        return [
            PathConfigResponse(
                id=config["id"],
                config_type=config["config_type"],
                name=config["name"],
                description=config.get("description", ""),
                paths=config["paths"],
                enabled=config["enabled"],
                created_at=config["created_at"],
                updated_at=config["updated_at"],
                metadata=config.get("metadata", {})
            )
            for config in configs
        ]
    except Exception as e:
        logger.error(f"Failed to get path configs: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取路径配置失败: {str(e)}")

@router.get("/paths/{config_type}", response_model=PathConfigResponse)
async def get_path_config(config_type: str):
    """获取指定类型的路径配置"""
    try:
        security_service = get_file_security_service()
        config = security_service.get_path_config(config_type)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"路径配置 {config_type} 不存在")
        
        return PathConfigResponse(
            id=config["id"],
            config_type=config["config_type"],
            name=config["name"],
            description=config.get("description", ""),
            paths=config["paths"],
            enabled=config["enabled"],
            created_at=config["created_at"],
            updated_at=config["updated_at"],
            metadata=config.get("metadata", {})
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get path config {config_type}: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取路径配置失败: {str(e)}")

@router.put("/paths/{config_type}", response_model=Dict[str, Any])
async def update_path_config(config_type: str, request: PathConfigRequest):
    """更新指定类型的路径配置"""
    try:
        # 验证配置类型
        valid_types = ["readable", "writable", "deletable", "forbidden"]
        if config_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的配置类型: {config_type}，允许的类型: {valid_types}"
            )
        
        # 空路径列表表示允许所有路径（除了 forbidden 类型）
        
        security_service = get_file_security_service()
        success = security_service.update_path_config(config_type, request.paths)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"路径配置 {config_type} 不存在")
        
        # 重新加载文件安全管理器配置
        file_security_manager = get_file_security_manager()
        file_security_manager.reload_config()
        
        logger.info(f"Updated path config {config_type} with {len(request.paths)} paths")
        
        return {
            "status": "success",
            "message": f"路径配置 {config_type} 更新成功",
            "updated_paths": len(request.paths),
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update path config {config_type}: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"更新路径配置失败: {str(e)}")

@router.post("/paths/{config_type}/enable", response_model=Dict[str, Any])
async def enable_path_config(config_type: str):
    """启用指定类型的路径配置"""
    try:
        security_service = get_file_security_service()
        success = security_service.enable_path_config(config_type)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"路径配置 {config_type} 不存在")
        
        # 重新加载文件安全管理器配置
        file_security_manager = get_file_security_manager()
        file_security_manager.reload_config()
        
        return {
            "status": "success",
            "message": f"路径配置 {config_type} 已启用",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable path config {config_type}: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"启用路径配置失败: {str(e)}")

@router.post("/paths/{config_type}/disable", response_model=Dict[str, Any])
async def disable_path_config(config_type: str):
    """禁用指定类型的路径配置"""
    try:
        security_service = get_file_security_service()
        success = security_service.disable_path_config(config_type)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"路径配置 {config_type} 不存在")
        
        # 重新加载文件安全管理器配置
        file_security_manager = get_file_security_manager()
        file_security_manager.reload_config()
        
        return {
            "status": "success",
            "message": f"路径配置 {config_type} 已禁用",
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable path config {config_type}: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"禁用路径配置失败: {str(e)}")

@router.get("/limits", response_model=List[LimitConfigResponse])
async def get_limit_configs(enabled_only: bool = True):
    """获取所有限制配置"""
    try:
        security_service = get_file_security_service()
        configs = security_service.get_all_limit_configs(enabled_only=enabled_only)
        
        return [
            LimitConfigResponse(
                id=config["id"],
                limit_type=config["limit_type"],
                name=config["name"],
                value=config["value"],
                description=config.get("description", ""),
                enabled=config["enabled"],
                created_at=config["created_at"],
                updated_at=config["updated_at"]
            )
            for config in configs
        ]
    except Exception as e:
        logger.error(f"Failed to get limit configs: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取限制配置失败: {str(e)}")

@router.get("/limits/{limit_type}", response_model=LimitConfigResponse)
async def get_limit_config(limit_type: str):
    """获取指定类型的限制配置"""
    try:
        security_service = get_file_security_service()
        config = security_service.get_limit_config(limit_type)
        
        if not config:
            raise HTTPException(status_code=404, detail=f"限制配置 {limit_type} 不存在")
        
        return LimitConfigResponse(
            id=config["id"],
            limit_type=config["limit_type"],
            name=config["name"],
            value=config["value"],
            description=config.get("description", ""),
            enabled=config["enabled"],
            created_at=config["created_at"],
            updated_at=config["updated_at"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get limit config {limit_type}: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取限制配置失败: {str(e)}")

@router.put("/limits/{limit_type}", response_model=Dict[str, Any])
async def update_limit_config(limit_type: str, request: LimitConfigRequest):
    """更新指定类型的限制配置"""
    try:
        # 验证限制类型
        valid_types = [
            "max_file_size", 
            "max_read_lines", 
            "strict_mode", 
            "recycle_bin_enabled",
            "recycle_bin_retention_days",
            "recycle_bin_auto_cleanup_hours"
        ]
        if limit_type not in valid_types:
            raise HTTPException(
                status_code=400, 
                detail=f"无效的限制类型: {limit_type}，允许的类型: {valid_types}"
            )
        
        security_service = get_file_security_service()
        success = security_service.update_limit_config(limit_type, request.value)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"限制配置 {limit_type} 不存在")
        
        # 重新加载文件安全管理器配置
        file_security_manager = get_file_security_manager()
        file_security_manager.reload_config()
        
        logger.info(f"Updated limit config {limit_type} to value {request.value}")
        
        return {
            "status": "success",
            "message": f"限制配置 {limit_type} 更新成功",
            "new_value": request.value,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update limit config {limit_type}: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"更新限制配置失败: {str(e)}")

@router.get("/summary", response_model=SecuritySummaryResponse)
async def get_security_summary():
    """获取安全配置总览"""
    try:
        security_service = get_file_security_service()
        summary = security_service.get_security_summary()
        
        return SecuritySummaryResponse(
            path_configs=summary["path_configs"],
            limit_configs=summary["limit_configs"],
            total_paths=summary["total_paths"],
            enabled_path_configs=summary["enabled_path_configs"],
            last_updated=summary["last_updated"]
        )
    except Exception as e:
        logger.error(f"Failed to get security summary: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取安全配置总览失败: {str(e)}")

class FileValidationRequest(BaseModel):
    """文件操作验证请求模型"""
    operation: str = Field(..., pattern=r"^(read|write|delete|list)$", description="操作类型")
    file_path: str = Field(..., min_length=1, max_length=1000, description="文件路径")
    check_size: bool = Field(default=True, description="是否检查文件大小")

@router.post("/validate", response_model=Dict[str, Any])
async def validate_file_operation(request: FileValidationRequest):
    """验证文件操作权限"""
    try:
        file_security_manager = get_file_security_manager()
        allowed, message = file_security_manager.validate_operation(request.operation, request.file_path)

        return {
            "allowed": allowed,
            "operation": request.operation,
            "file_path": sanitize_for_log(request.file_path),  # 在响应中也进行日志安全处理
            "message": message or "操作被允许",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to validate file operation: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"文件操作验证失败: {str(e)}")