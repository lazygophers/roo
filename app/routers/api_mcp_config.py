"""
MCP全局配置API路由
提供MCP工具全局配置管理的REST API端点
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from datetime import datetime

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.mcp_tools_service import get_mcp_config_service
from app.models.mcp_config import MCPGlobalConfig
import functools

logger = setup_logging()

router = APIRouter(prefix="/mcp/config", tags=["MCP配置"])


def require_edit_permission(func):
    """装饰器：要求编辑权限"""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        config_service = get_mcp_config_service()
        if not config_service.is_tool_edit_allowed():
            return {
                "success": False,
                "message": "在远程环境中，MCP配置编辑被禁用。请在本地环境中使用此功能。"
            }
        return await func(*args, **kwargs)
    return wrapper

# Pydantic 模型定义
class ProxyConfigRequest(BaseModel):
    """代理配置请求模型"""
    enabled: bool = False
    proxy: str = Field("", description="统一代理地址，同时用于HTTP和HTTPS")
    no_proxy: str = Field("", description="不使用代理的地址列表，逗号分隔")
    username: str = Field("", description="代理认证用户名")
    password: str = Field("", description="代理认证密码")


class NetworkConfigRequest(BaseModel):
    """网络配置请求模型"""
    timeout: int = Field(30, gt=0, le=300, description="请求超时时间（秒）")
    retry_times: int = Field(3, ge=0, le=10, description="重试次数")
    retry_delay: float = Field(1.0, ge=0.1, le=10.0, description="重试延迟（秒）")
    user_agent: str = Field("LazyAI-Studio-MCP/1.0", description="用户代理")
    max_connections: int = Field(100, gt=0, le=1000, description="最大连接数")


class SecurityConfigRequest(BaseModel):
    """安全配置请求模型"""
    verify_ssl: bool = Field(True, description="验证SSL证书")
    allowed_hosts: List[str] = Field(default_factory=list, description="允许访问的主机列表")
    blocked_hosts: List[str] = Field(default_factory=list, description="禁止访问的主机列表")
    enable_rate_limit: bool = Field(True, description="启用速率限制")
    rate_limit_per_minute: int = Field(60, gt=0, le=1000, description="每分钟请求限制")


class ToolCategoryConfigRequest(BaseModel):
    """工具分类配置请求模型"""
    enabled: bool = Field(True, description="是否启用该分类")
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="自定义配置")


class GlobalConfigRequest(BaseModel):
    """全局配置请求模型"""
    enabled: bool = Field(True, description="启用MCP工具")
    debug_mode: bool = Field(False, description="调试模式")
    log_level: str = Field("INFO", description="日志级别")


class EnvironmentVariablesRequest(BaseModel):
    """环境变量配置请求模型"""
    variables: Dict[str, str] = Field(default_factory=dict, description="环境变量键值对")


# API端点实现
@router.get("/", response_model=Dict[str, Any])
async def get_config():
    """获取完整的MCP全局配置"""
    try:
        config_service = get_mcp_config_service()
        config = config_service.get_config()
        logger.info("Retrieved MCP global config")
        return {"success": True, "data": config.to_dict()}
    except Exception as e:
        logger.error(f"Failed to get MCP config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/", response_model=Dict[str, Any])
@require_edit_permission
async def update_global_config(request: GlobalConfigRequest):
    """更新全局配置"""
    try:
        config_service = get_mcp_config_service()
        updates = request.dict()
        config = config_service.update_config(updates)

        logger.info(f"Updated MCP global config: {sanitize_for_log(list(updates.keys()))}")
        return {"success": True, "data": config.to_dict()}
    except Exception as e:
        logger.error(f"Failed to update global config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/proxy", response_model=Dict[str, Any])
async def get_proxy_config():
    """获取代理配置"""
    try:
        config_service = get_mcp_config_service()
        proxy_config = config_service.get_proxy_config()
        return {"success": True, "data": proxy_config}
    except Exception as e:
        logger.error(f"Failed to get proxy config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/proxy", response_model=Dict[str, Any])
@require_edit_permission
async def update_proxy_config(request: ProxyConfigRequest):
    """更新代理配置"""
    try:
        config_service = get_mcp_config_service()
        proxy_config = request.dict()
        config = config_service.update_proxy_config(proxy_config)

        logger.info("Updated MCP proxy config")
        return {"success": True, "data": config.proxy.to_dict()}
    except Exception as e:
        logger.error(f"Failed to update proxy config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/network", response_model=Dict[str, Any])
async def get_network_config():
    """获取网络配置"""
    try:
        config_service = get_mcp_config_service()
        network_config = config_service.get_network_config()
        return {"success": True, "data": network_config}
    except Exception as e:
        logger.error(f"Failed to get network config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/network", response_model=Dict[str, Any])
@require_edit_permission
async def update_network_config(request: NetworkConfigRequest):
    """更新网络配置"""
    try:
        config_service = get_mcp_config_service()
        network_config = request.dict()
        config = config_service.update_network_config(network_config)

        logger.info("Updated MCP network config")
        return {"success": True, "data": config.network.to_dict()}
    except Exception as e:
        logger.error(f"Failed to update network config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/security", response_model=Dict[str, Any])
async def get_security_config():
    """获取安全配置"""
    try:
        config_service = get_mcp_config_service()
        security_config = config_service.get_security_config()
        return {"success": True, "data": security_config}
    except Exception as e:
        logger.error(f"Failed to get security config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/security", response_model=Dict[str, Any])
@require_edit_permission
async def update_security_config(request: SecurityConfigRequest):
    """更新安全配置"""
    try:
        config_service = get_mcp_config_service()
        security_config = request.dict()
        config = config_service.update_security_config(security_config)

        logger.info("Updated MCP security config")
        return {"success": True, "data": config.security.to_dict()}
    except Exception as e:
        logger.error(f"Failed to update security config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tool-categories", response_model=Dict[str, Any])
async def get_all_tool_categories():
    """获取所有工具分类配置"""
    try:
        config_service = get_mcp_config_service()
        config = config_service.get_config()

        categories_config = {
            cat: config.tool_categories[cat].to_dict() if cat in config.tool_categories
            else {"category": cat, "enabled": True, "custom_config": {}}
            for cat in config.tool_categories.keys()
        }

        return {"success": True, "data": categories_config}
    except Exception as e:
        logger.error(f"Failed to get tool categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tool-categories/{category}", response_model=Dict[str, Any])
async def get_tool_category_config(category: str):
    """获取特定工具分类配置"""
    try:
        config_service = get_mcp_config_service()
        category_config = config_service.get_tool_category_config(category)
        return {"success": True, "data": category_config}
    except Exception as e:
        logger.error(f"Failed to get tool category config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/tool-categories/{category}", response_model=Dict[str, Any])
@require_edit_permission
async def update_tool_category_config(category: str, request: ToolCategoryConfigRequest):
    """更新工具分类配置"""
    try:
        config_service = get_mcp_config_service()
        category_config = request.dict()
        config = config_service.update_tool_category_config(category, category_config)

        updated_config = config.tool_categories[category].to_dict()
        logger.info(f"Updated tool category config for {sanitize_for_log(category)}")
        return {"success": True, "data": updated_config}
    except Exception as e:
        logger.error(f"Failed to update tool category config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/environment-variables", response_model=Dict[str, Any])
async def get_environment_variables():
    """获取环境变量配置"""
    try:
        config_service = get_mcp_config_service()
        env_vars = config_service.get_environment_variables()
        return {"success": True, "data": env_vars}
    except Exception as e:
        logger.error(f"Failed to get environment variables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/environment-variables", response_model=Dict[str, Any])
@require_edit_permission
async def update_environment_variables(request: EnvironmentVariablesRequest):
    """更新环境变量配置"""
    try:
        config_service = get_mcp_config_service()
        env_vars = request.variables
        config = config_service.update_environment_variables(env_vars)

        logger.info(f"Updated environment variables: {sanitize_for_log(list(env_vars.keys()))}")
        return {"success": True, "data": config.environment_variables}
    except Exception as e:
        logger.error(f"Failed to update environment variables: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset", response_model=Dict[str, Any])
@require_edit_permission
async def reset_config():
    """重置配置为默认值"""
    try:
        config_service = get_mcp_config_service()
        config = config_service.reset_to_defaults()

        logger.info("Reset MCP config to defaults")
        return {"success": True, "data": config.to_dict()}
    except Exception as e:
        logger.error(f"Failed to reset config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export", response_model=Dict[str, Any])
async def export_config():
    """导出配置"""
    try:
        config_service = get_mcp_config_service()
        config_data = config_service.export_config()

        logger.info("Exported MCP config")
        return {"success": True, "data": config_data}
    except Exception as e:
        logger.error(f"Failed to export config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/import", response_model=Dict[str, Any])
@require_edit_permission
async def import_config(config_data: Dict[str, Any]):
    """导入配置"""
    try:
        config_service = get_mcp_config_service()
        config = config_service.import_config(config_data)

        logger.info("Imported MCP config")
        return {"success": True, "data": config.to_dict()}
    except Exception as e:
        logger.error(f"Failed to import config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=Dict[str, Any])
async def get_config_status():
    """获取配置状态信息"""
    try:
        config_service = get_mcp_config_service()
        config = config_service.get_config()

        status = {
            "enabled": config.enabled,
            "debug_mode": config.debug_mode,
            "proxy_enabled": config.proxy.enabled,
            "ssl_verification": config.security.verify_ssl,
            "tool_categories_count": len(config.tool_categories),
            "environment_variables_count": len(config.environment_variables),
            "last_updated": config.updated_at
        }

        return {"success": True, "data": status}
    except Exception as e:
        logger.error(f"Failed to get config status: {e}")
        raise HTTPException(status_code=500, detail=str(e))