"""
网络抓取工具API路由
提供网络抓取相关的REST API端点
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Union
import asyncio

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.tools.web_scraping_tools import (
    get_web_scraping_tools,
    http_request,
    fetch_webpage,
    download_file,
    api_call,
    batch_requests
)

logger = setup_logging()

router = APIRouter(prefix="/web-scraping", tags=["Web Scraping"])

# Pydantic 模型定义
class HttpRequestRequest(BaseModel):
    """HTTP请求模型"""
    url: str = Field(..., description="请求URL")
    method: str = Field("GET", description="HTTP方法")
    headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(None, description="URL参数")
    data: Optional[Union[str, Dict[str, Any]]] = Field(None, description="请求体数据")
    json_data: Optional[Dict[str, Any]] = Field(None, description="JSON请求体")
    auth: Optional[List[str]] = Field(None, description="HTTP基础认证 [username, password]")
    follow_redirects: Optional[bool] = Field(None, description="是否跟随重定向")


class FetchWebpageRequest(BaseModel):
    """网页抓取请求模型"""
    url: str = Field(..., description="网页URL")
    headers: Optional[Dict[str, str]] = Field(None, description="自定义请求头")
    extract_text: bool = Field(True, description="提取纯文本")
    extract_links: bool = Field(False, description="提取链接")
    extract_images: bool = Field(False, description="提取图片")


class DownloadFileRequest(BaseModel):
    """文件下载请求模型"""
    url: str = Field(..., description="文件URL")
    save_path: Optional[str] = Field(None, description="保存路径")
    headers: Optional[Dict[str, str]] = Field(None, description="自定义请求头")
    max_size: Optional[int] = Field(None, description="最大文件大小（字节）")


class ApiCallRequest(BaseModel):
    """API调用请求模型"""
    url: str = Field(..., description="API端点URL")
    method: str = Field("GET", description="HTTP方法")
    headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(None, description="URL参数")
    json_data: Optional[Dict[str, Any]] = Field(None, description="JSON请求体")
    auth_token: Optional[str] = Field(None, description="认证令牌")
    auth_type: str = Field("Bearer", description="认证类型")


class BatchRequestItem(BaseModel):
    """批量请求项模型"""
    url: str = Field(..., description="请求URL")
    method: str = Field("GET", description="HTTP方法")
    headers: Optional[Dict[str, str]] = Field(None, description="请求头")
    params: Optional[Dict[str, Any]] = Field(None, description="URL参数")
    data: Optional[Union[str, Dict[str, Any]]] = Field(None, description="请求体数据")
    json_data: Optional[Dict[str, Any]] = Field(None, description="JSON请求体")


class BatchRequestsRequest(BaseModel):
    """批量请求模型"""
    requests: List[BatchRequestItem] = Field(..., description="请求列表")
    max_concurrent: int = Field(5, ge=1, le=20, description="最大并发数")
    delay_between_requests: float = Field(0.1, ge=0, description="请求间延迟（秒）")


class WebScrapingConfigRequest(BaseModel):
    """网络抓取工具配置请求模型"""
    user_agent: Optional[str] = Field(None, description="用户代理")
    timeout: Optional[int] = Field(None, ge=1, le=300, description="请求超时（秒）")
    max_retries: Optional[int] = Field(None, ge=0, le=10, description="最大重试次数")
    retry_delay: Optional[float] = Field(None, ge=0.1, le=10.0, description="重试延迟（秒）")
    verify_ssl: Optional[bool] = Field(None, description="验证SSL证书")
    max_file_size: Optional[int] = Field(None, ge=1024, description="最大文件大小（字节）")
    follow_redirects: Optional[bool] = Field(None, description="跟随重定向")


# API端点实现
@router.post("/http-request", response_model=Dict[str, Any])
async def make_http_request(request: HttpRequestRequest):
    """执行HTTP请求"""
    try:
        logger.info(f"HTTP request: {request.method} {sanitize_for_log(request.url)}")

        auth_tuple = tuple(request.auth) if request.auth and len(request.auth) == 2 else None

        result = await http_request(
            url=request.url,
            method=request.method,
            headers=request.headers,
            params=request.params,
            data=request.data,
            json_data=request.json_data,
            auth=auth_tuple,
            follow_redirects=request.follow_redirects
        )

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"HTTP request failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fetch-webpage", response_model=Dict[str, Any])
async def fetch_webpage_endpoint(request: FetchWebpageRequest):
    """抓取网页内容"""
    try:
        logger.info(f"Fetching webpage: {sanitize_for_log(request.url)}")

        result = await fetch_webpage(
            url=request.url,
            headers=request.headers,
            extract_text=request.extract_text,
            extract_links=request.extract_links,
            extract_images=request.extract_images
        )

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Webpage fetch failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/download-file", response_model=Dict[str, Any])
async def download_file_endpoint(request: DownloadFileRequest):
    """下载文件"""
    try:
        logger.info(f"Downloading file: {sanitize_for_log(request.url)}")

        result = await download_file(
            url=request.url,
            save_path=request.save_path,
            headers=request.headers,
            max_size=request.max_size
        )

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"File download failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api-call", response_model=Dict[str, Any])
async def make_api_call(request: ApiCallRequest):
    """执行API调用"""
    try:
        logger.info(f"API call: {request.method} {sanitize_for_log(request.url)}")

        result = await api_call(
            url=request.url,
            method=request.method,
            headers=request.headers,
            params=request.params,
            json_data=request.json_data,
            auth_token=request.auth_token,
            auth_type=request.auth_type
        )

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"API call failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-requests", response_model=Dict[str, Any])
async def make_batch_requests(request: BatchRequestsRequest):
    """执行批量HTTP请求"""
    try:
        logger.info(f"Batch requests: {len(request.requests)} requests")

        # 转换请求格式
        requests_data = []
        for req in request.requests:
            req_data = req.dict(exclude_none=True)
            requests_data.append(req_data)

        result = await batch_requests(
            requests=requests_data,
            max_concurrent=request.max_concurrent,
            delay_between_requests=request.delay_between_requests
        )

        return {"success": True, "data": result}

    except Exception as e:
        logger.error(f"Batch requests failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=Dict[str, Any])
async def get_web_scraping_config():
    """获取网络抓取工具配置"""
    try:
        tools = get_web_scraping_tools()
        config = {
            "enabled": tools.config.enabled,
            "user_agent": tools.config.user_agent,
            "timeout": tools.config.timeout,
            "max_retries": tools.config.max_retries,
            "retry_delay": tools.config.retry_delay,
            "max_file_size": tools.config.max_file_size,
            "allowed_content_types": tools.config.allowed_content_types,
            "follow_redirects": tools.config.follow_redirects,
            "verify_ssl": tools.config.verify_ssl
        }

        # 获取MCP全局配置信息
        mcp_config_info = None
        if tools.mcp_config:
            mcp_config_info = {
                "proxy_enabled": tools.mcp_config.proxy.enabled,
                "global_timeout": tools.mcp_config.network.timeout,
                "global_user_agent": tools.mcp_config.network.user_agent,
                "ssl_verification": tools.mcp_config.security.verify_ssl
            }

        return {
            "success": True,
            "data": {
                "config": config,
                "mcp_global_config": mcp_config_info
            }
        }

    except Exception as e:
        logger.error(f"Failed to get config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config", response_model=Dict[str, Any])
async def update_web_scraping_config(request: WebScrapingConfigRequest):
    """更新网络抓取工具配置"""
    try:
        from app.core.mcp_tools_service import get_mcp_config_service

        # 准备工具集自定义配置
        custom_config = {}
        config_updates = request.dict(exclude_none=True)

        if config_updates:
            custom_config.update(config_updates)

        # 更新MCP工具分类配置
        config_service = get_mcp_config_service()
        config_service.update_tool_category_config(
            "web-scraping",
            {"enabled": True, "custom_config": custom_config}
        )

        logger.info(f"Updated web scraping config: {sanitize_for_log(list(custom_config.keys()))}")

        # 重新加载配置
        tools = get_web_scraping_tools()
        tools._load_config()

        return {"success": True, "message": "Configuration updated successfully"}

    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-connection", response_model=Dict[str, Any])
async def test_connection():
    """测试网络连接（包括代理配置）"""
    try:
        # 测试基本HTTP连接
        test_urls = [
            "https://httpbin.org/get",
            "https://www.google.com",
            "https://github.com"
        ]

        results = []
        for url in test_urls:
            try:
                result = await http_request(url, method="GET")
                results.append({
                    "url": url,
                    "status": "success" if result["success"] else "failed",
                    "status_code": result.get("status_code"),
                    "response_time": result.get("response_time", "N/A")
                })
            except Exception as e:
                results.append({
                    "url": url,
                    "status": "error",
                    "error": str(e)
                })

        # 获取当前配置信息
        tools = get_web_scraping_tools()
        config_info = {
            "user_agent": tools.config.user_agent,
            "timeout": tools.config.timeout,
            "proxy_enabled": tools.mcp_config.proxy.enabled if tools.mcp_config else False,
            "proxy_url": tools._get_proxy_url() if tools.mcp_config else None
        }

        return {
            "success": True,
            "data": {
                "config": config_info,
                "test_results": results
            }
        }

    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=Dict[str, Any])
async def get_web_scraping_status():
    """获取网络抓取工具状态"""
    try:
        tools = get_web_scraping_tools()

        # 检查会话状态
        session_status = "closed"
        if tools.session and not tools.session.closed:
            session_status = "active"

        status_info = {
            "enabled": tools.config.enabled,
            "session_status": session_status,
            "proxy_configured": tools.mcp_config.proxy.enabled if tools.mcp_config else False,
            "ssl_verification": tools.config.verify_ssl,
            "max_file_size_mb": tools.config.max_file_size // (1024 * 1024),
            "timeout_seconds": tools.config.timeout,
            "max_retries": tools.config.max_retries
        }

        return {"success": True, "data": status_info}

    except Exception as e:
        logger.error(f"Failed to get status: {e}")
        raise HTTPException(status_code=500, detail=str(e))