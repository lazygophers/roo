"""
网络抓取MCP工具集
支持HTTP请求、网页抓取、API调用等网络相关操作
遵循全局MCP配置，支持工具集级别配置优先级
"""

import asyncio
import json
import base64
import aiohttp
import aiofiles
from typing import Dict, Any, Optional, List, Union
from urllib.parse import urljoin, urlparse
from pathlib import Path
import mimetypes
from datetime import datetime

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.mcp_tools_service import get_mcp_config_service
from app.models.mcp_config import MCPGlobalConfig
from app.tools.registry import web_scraping_tool, mcp_category

logger = setup_logging()

# Force tool discovery trigger (version 1.1)


# 注册网络抓取工具分类
@mcp_category(
    category_id="web-scraping",
    name="网络抓取工具",
    description="网页抓取、HTTP请求、API调用等网络数据获取工具",
    icon="🌐",
    sort_order=6,
    config={
        "default_timeout": 30,
        "max_redirects": 5,
        "max_file_size_mb": 100,
        "enable_ssl_verification": True,
        "default_user_agent": "LazyAI-Studio-WebScraper/1.0",
        "rate_limit_enabled": True,
        "concurrent_requests_limit": 10,
        "enable_content_type_validation": True,
        "allowed_content_types": [
            "text/html",
            "text/plain",
            "application/json",
            "application/xml",
            "text/xml"
        ]
    }
)
def register_web_scraping_category():
    """注册网络抓取工具分类"""
    pass


class WebScrapingConfig:
    """网络抓取工具配置类"""

    def __init__(self):
        self.enabled = True
        self.user_agent = "LazyAI-Studio-WebScraper/1.0"
        self.timeout = 30
        self.max_retries = 3
        self.retry_delay = 1.0
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.allowed_content_types = [
            "text/html", "text/plain", "application/json",
            "application/xml", "text/xml", "text/css", "text/javascript"
        ]
        self.follow_redirects = True
        self.verify_ssl = True


class WebScrapingTools:
    """网络抓取工具集"""

    def __init__(self):
        self.config = WebScrapingConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.mcp_config: Optional[MCPGlobalConfig] = None
        self._load_config()

    def _load_config(self):
        """加载配置（全局MCP配置 + 工具集配置）"""
        try:
            config_service = get_mcp_config_service()
            self.mcp_config = config_service.get_config()

            # 获取工具集专用配置
            web_scraping_config = config_service.get_tool_category_config("web-scraping")
            custom_config = web_scraping_config.get("custom_config", {})

            # 工具集配置优先级 > 全局配置
            if "user_agent" in custom_config:
                self.config.user_agent = custom_config["user_agent"]
            elif self.mcp_config:
                self.config.user_agent = self.mcp_config.network.user_agent

            if "timeout" in custom_config:
                self.config.timeout = custom_config["timeout"]
            elif self.mcp_config:
                self.config.timeout = self.mcp_config.network.timeout

            if "max_retries" in custom_config:
                self.config.max_retries = custom_config["max_retries"]
            elif self.mcp_config:
                self.config.max_retries = self.mcp_config.network.retry_times

            if "retry_delay" in custom_config:
                self.config.retry_delay = custom_config["retry_delay"]
            elif self.mcp_config:
                self.config.retry_delay = self.mcp_config.network.retry_delay

            if "verify_ssl" in custom_config:
                self.config.verify_ssl = custom_config["verify_ssl"]
            elif self.mcp_config:
                self.config.verify_ssl = self.mcp_config.security.verify_ssl

            logger.info(f"Loaded web scraping tools config: UA={sanitize_for_log(self.config.user_agent)}")

        except Exception as e:
            logger.warning(f"Failed to load MCP config, using defaults: {e}")

    async def _get_session(self) -> aiohttp.ClientSession:
        """获取HTTP会话，配置代理和其他参数"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                ssl=self.config.verify_ssl,
                limit=self.mcp_config.network.max_connections if self.mcp_config else 100
            )

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)

            # 设置代理（使用全局MCP代理配置）
            proxy_config = None
            if self.mcp_config:
                proxy_config = self.mcp_config.get_proxy_dict()

            headers = {
                "User-Agent": self.config.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1"
            }

            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers=headers
            )

            # 配置代理（如果有）
            if proxy_config:
                # aiohttp需要为每个请求单独设置proxy
                pass

        return self.session

    def _get_proxy_url(self) -> Optional[str]:
        """获取代理URL"""
        if self.mcp_config:
            proxy_dict = self.mcp_config.get_proxy_dict()
            if proxy_dict:
                return proxy_dict.get("http") or proxy_dict.get("https")
        return None

    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """带重试的HTTP请求"""
        session = await self._get_session()
        proxy_url = self._get_proxy_url()

        for attempt in range(self.config.max_retries + 1):
            try:
                if proxy_url:
                    kwargs["proxy"] = proxy_url

                async with session.request(method, url, **kwargs) as response:
                    # 检查响应状态
                    if response.status < 400:
                        return response
                    elif attempt < self.config.max_retries:
                        logger.warning(f"Request failed with status {response.status}, retrying ({attempt + 1}/{self.config.max_retries})")
                        await asyncio.sleep(self.config.retry_delay)
                        continue
                    else:
                        response.raise_for_status()

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                if attempt < self.config.max_retries:
                    logger.warning(f"Request failed: {e}, retrying ({attempt + 1}/{self.config.max_retries})")
                    await asyncio.sleep(self.config.retry_delay)
                else:
                    raise e

    async def close(self):
        """关闭会话"""
        if self.session and not self.session.closed:
            await self.session.close()


# 全局实例
_web_scraping_tools: Optional[WebScrapingTools] = None


def get_web_scraping_tools() -> WebScrapingTools:
    """获取网络抓取工具实例"""
    global _web_scraping_tools
    if _web_scraping_tools is None:
        _web_scraping_tools = WebScrapingTools()
    return _web_scraping_tools


def reload_web_scraping_config():
    """重新加载配置（供MCP配置服务调用）"""
    global _web_scraping_tools
    if _web_scraping_tools is not None:
        _web_scraping_tools._load_config()


# MCP工具定义
@web_scraping_tool(
    name="http_request",
    description="执行HTTP请求（GET, POST, PUT, DELETE等）",
    schema={
        "type": "object",
        "properties": {
            "url": {
                "type": "string",
                "description": "请求URL"
            },
            "method": {
                "type": "string",
                "enum": ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"],
                "default": "GET",
                "description": "HTTP方法"
            },
            "headers": {
                "type": "object",
                "additionalProperties": {"type": "string"},
                "description": "请求头"
            },
            "params": {
                "type": "object",
                "description": "URL参数"
            },
            "data": {
                "oneOf": [
                    {"type": "string"},
                    {"type": "object"}
                ],
                "description": "请求体数据（form data或字符串）"
            },
            "json_data": {
                "type": "object",
                "description": "JSON请求体"
            },
            "auth": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 2,
                "maxItems": 2,
                "description": "HTTP基础认证 [username, password]"
            },
            "follow_redirects": {
                "type": "boolean",
                "description": "是否跟随重定向"
            }
        },
        "required": ["url"]
    },
    returns={
        "type": "object",
        "properties": {
            "status_code": {"type": "integer", "description": "HTTP状态码"},
            "headers": {"type": "object", "description": "响应头"},
            "content": {"type": "string", "description": "响应内容"},
            "url": {"type": "string", "description": "最终请求URL"},
            "encoding": {"type": "string", "description": "内容编码"},
            "content_type": {"type": "string", "description": "内容类型"}
        }
    },
    metadata={
        "tags": ["http", "network", "request"],
        "version": "1.0.0"
    }
)
async def http_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    data: Optional[Union[str, Dict[str, Any]]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    auth: Optional[tuple] = None,
    follow_redirects: Optional[bool] = None
) -> Dict[str, Any]:
    """
    执行HTTP请求

    Args:
        url: 请求URL
        method: HTTP方法（GET, POST, PUT, DELETE等）
        headers: 请求头
        params: URL参数
        data: 请求体数据（form data或字符串）
        json_data: JSON请求体
        auth: HTTP基础认证 (username, password)
        follow_redirects: 是否跟随重定向

    Returns:
        包含响应信息的字典
    """
    tools = get_web_scraping_tools()

    try:
        logger.info(f"Making HTTP {method} request to {sanitize_for_log(url)}")

        # 准备请求参数
        kwargs = {}

        if headers:
            kwargs["headers"] = headers

        if params:
            kwargs["params"] = params

        if json_data:
            kwargs["json"] = json_data
        elif data:
            if isinstance(data, dict):
                kwargs["data"] = data
            else:
                kwargs["data"] = data

        if auth:
            kwargs["auth"] = aiohttp.BasicAuth(auth[0], auth[1])

        if follow_redirects is not None:
            kwargs["allow_redirects"] = follow_redirects
        else:
            kwargs["allow_redirects"] = tools.config.follow_redirects

        # 执行请求
        async with await tools._make_request_with_retry(method.upper(), url, **kwargs) as response:
            content_type = response.headers.get("Content-Type", "").lower()

            # 读取响应内容
            if "application/json" in content_type:
                content = await response.json()
                content_text = json.dumps(content, ensure_ascii=False, indent=2)
            else:
                content = await response.text()
                content_text = content

            result = {
                "success": True,
                "status_code": response.status,
                "headers": dict(response.headers),
                "content": content,
                "content_text": content_text,
                "content_type": content_type,
                "url": str(response.url),
                "method": method.upper(),
                "encoding": response.get_encoding()
            }

            logger.info(f"HTTP request successful: {response.status}")
            return result

    except Exception as e:
        logger.error(f"HTTP request failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "method": method.upper()
        }


@web_scraping_tool(
    name="fetch_webpage",
    description="抓取网页内容，支持提取文本、链接和图片，使用BeautifulSoup解析HTML",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "网页URL"},
            "headers": {"type": "object", "additionalProperties": {"type": "string"}, "description": "自定义请求头"},
            "extract_text": {"type": "boolean", "description": "是否提取纯文本内容", "default": True},
            "extract_links": {"type": "boolean", "description": "是否提取链接", "default": False},
            "extract_images": {"type": "boolean", "description": "是否提取图片URL", "default": False}
        },
        "required": ["url"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "title": {"type": "string", "description": "网页标题"},
            "text": {"type": "string", "description": "提取的文本内容"},
            "links": {"type": "array", "items": {"type": "object"}, "description": "提取的链接列表"},
            "images": {"type": "array", "items": {"type": "string"}, "description": "提取的图片URL列表"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["webpage", "scraping", "html"]}
)
async def fetch_webpage(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    extract_text: bool = True,
    extract_links: bool = False,
    extract_images: bool = False
) -> Dict[str, Any]:
    """
    抓取网页内容并解析

    Args:
        url: 网页URL
        headers: 自定义请求头
        extract_text: 是否提取纯文本
        extract_links: 是否提取链接
        extract_images: 是否提取图片URL

    Returns:
        包含网页内容和解析结果的字典
    """
    tools = get_web_scraping_tools()

    try:
        logger.info(f"Fetching webpage: {sanitize_for_log(url)}")

        # 执行HTTP请求
        result = await http_request(url, headers=headers)

        if not result["success"]:
            return result

        # 检查内容类型
        content_type = result.get("content_type", "")
        if "text/html" not in content_type.lower():
            logger.warning(f"URL is not HTML content: {content_type}")
            return result

        html_content = result["content_text"]
        parsed_result = {
            "success": True,
            "url": result["url"],
            "status_code": result["status_code"],
            "headers": result["headers"],
            "html": html_content,
            "title": "",
            "text": "",
            "links": [],
            "images": []
        }

        # 简单的HTML解析（可以考虑使用BeautifulSoup）
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')

            # 提取标题
            title_tag = soup.find('title')
            if title_tag:
                parsed_result["title"] = title_tag.get_text().strip()

            # 提取纯文本
            if extract_text:
                # 移除script和style标签
                for script in soup(["script", "style"]):
                    script.decompose()
                parsed_result["text"] = soup.get_text()

            # 提取链接
            if extract_links:
                links = []
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    # 处理相对链接
                    if href.startswith('/'):
                        href = urljoin(url, href)
                    elif not href.startswith(('http://', 'https://', 'mailto:', 'tel:')):
                        href = urljoin(url, href)

                    links.append({
                        "url": href,
                        "text": link.get_text().strip(),
                        "title": link.get('title', '')
                    })
                parsed_result["links"] = links

            # 提取图片
            if extract_images:
                images = []
                for img in soup.find_all('img', src=True):
                    src = img['src']
                    # 处理相对链接
                    if src.startswith('/'):
                        src = urljoin(url, src)
                    elif not src.startswith(('http://', 'https://', 'data:')):
                        src = urljoin(url, src)

                    images.append({
                        "url": src,
                        "alt": img.get('alt', ''),
                        "title": img.get('title', '')
                    })
                parsed_result["images"] = images

        except ImportError:
            logger.warning("BeautifulSoup not available, skipping HTML parsing")
            # 基础文本提取
            if extract_text:
                import re
                # 移除HTML标签的简单方法
                text = re.sub(r'<[^>]+>', '', html_content)
                parsed_result["text"] = ' '.join(text.split())

        logger.info(f"Webpage fetched successfully: {len(html_content)} characters")
        return parsed_result

    except Exception as e:
        logger.error(f"Failed to fetch webpage: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


@web_scraping_tool(
    name="download_file",
    description="下载文件到指定路径，支持大文件下载和进度监控，可设置文件大小限制",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "文件下载URL"},
            "save_path": {"type": "string", "description": "文件保存路径"},
            "headers": {"type": "object", "additionalProperties": {"type": "string"}, "description": "自定义请求头"},
            "max_size": {"type": "integer", "description": "最大文件大小（字节）"}
        },
        "required": ["url"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功下载"},
            "file_path": {"type": "string", "description": "下载文件的完整路径"},
            "file_size": {"type": "integer", "description": "文件大小（字节）"},
            "content_type": {"type": "string", "description": "文件内容类型"},
            "download_time": {"type": "number", "description": "下载耗时（秒）"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["download", "file", "binary"]}
)
async def download_file(
    url: str,
    save_path: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    max_size: Optional[int] = None
) -> Dict[str, Any]:
    """
    下载文件

    Args:
        url: 文件URL
        save_path: 保存路径（如果为空则返回二进制内容）
        headers: 自定义请求头
        max_size: 最大文件大小限制（字节）

    Returns:
        包含下载结果的字典
    """
    tools = get_web_scraping_tools()

    try:
        logger.info(f"Downloading file from: {sanitize_for_log(url)}")

        session = await tools._get_session()
        proxy_url = tools._get_proxy_url()

        kwargs = {}
        if headers:
            kwargs["headers"] = headers
        if proxy_url:
            kwargs["proxy"] = proxy_url

        async with session.get(url, **kwargs) as response:
            response.raise_for_status()

            # 检查文件大小
            content_length = response.headers.get('Content-Length')
            file_size = int(content_length) if content_length else None
            max_allowed_size = max_size or tools.config.max_file_size

            if file_size and file_size > max_allowed_size:
                return {
                    "success": False,
                    "error": f"File too large: {file_size} bytes (max: {max_allowed_size})",
                    "url": url
                }

            # 读取内容
            content = await response.read()
            actual_size = len(content)

            if actual_size > max_allowed_size:
                return {
                    "success": False,
                    "error": f"File too large: {actual_size} bytes (max: {max_allowed_size})",
                    "url": url
                }

            result = {
                "success": True,
                "url": str(response.url),
                "status_code": response.status,
                "headers": dict(response.headers),
                "size": actual_size,
                "content_type": response.headers.get("Content-Type", ""),
                "filename": None
            }

            # 确定文件名
            filename = None
            content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename=' in content_disposition:
                filename = content_disposition.split('filename=')[1].strip('"')

            if not filename:
                # 从URL推断文件名
                parsed_url = urlparse(url)
                filename = Path(parsed_url.path).name or "download"

            result["filename"] = filename

            if save_path:
                # 保存到文件
                save_file_path = Path(save_path)
                save_file_path.parent.mkdir(parents=True, exist_ok=True)

                async with aiofiles.open(save_file_path, 'wb') as f:
                    await f.write(content)

                result["saved_path"] = str(save_file_path)
                logger.info(f"File saved to: {save_file_path}")
            else:
                # 返回base64编码的内容
                result["content_base64"] = base64.b64encode(content).decode('utf-8')

            logger.info(f"File downloaded successfully: {actual_size} bytes")
            return result

    except Exception as e:
        logger.error(f"Failed to download file: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


@web_scraping_tool(
    name="api_call",
    description="执行API调用，自动处理认证头，支持JSON响应解析和错误处理",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "API端点URL"},
            "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"], "description": "HTTP方法", "default": "GET"},
            "headers": {"type": "object", "additionalProperties": {"type": "string"}, "description": "请求头字典"},
            "params": {"type": "object", "description": "URL参数字典"},
            "json_data": {"type": "object", "description": "JSON请求体数据"},
            "auth_token": {"type": "string", "description": "认证令牌"},
            "auth_type": {"type": "string", "enum": ["Bearer", "Token", "Basic"], "description": "认证类型", "default": "Bearer"}
        },
        "required": ["url"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "API调用是否成功"},
            "status_code": {"type": "integer", "description": "HTTP状态码"},
            "content": {"type": ["object", "array"], "description": "API响应内容（JSON格式）"},
            "headers": {"type": "object", "description": "响应头"},
            "response_time": {"type": "number", "description": "响应时间（秒）"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["api", "json", "rest"]}
)
async def api_call(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    auth_token: Optional[str] = None,
    auth_type: str = "Bearer"
) -> Dict[str, Any]:
    """
    执行API调用（专门用于RESTful API）

    Args:
        url: API端点URL
        method: HTTP方法
        headers: 请求头
        params: URL参数
        json_data: JSON请求体
        auth_token: 认证令牌
        auth_type: 认证类型（Bearer, Token等）

    Returns:
        API响应结果
    """
    try:
        logger.info(f"Making API call: {method} {sanitize_for_log(url)}")

        # 准备请求头
        api_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        if auth_token:
            api_headers["Authorization"] = f"{auth_type} {auth_token}"

        if headers:
            api_headers.update(headers)

        # 执行请求
        result = await http_request(
            url=url,
            method=method,
            headers=api_headers,
            params=params,
            json_data=json_data
        )

        if result["success"]:
            logger.info(f"API call successful: {result['status_code']}")
        else:
            logger.error(f"API call failed: {result.get('error', 'Unknown error')}")

        return result

    except Exception as e:
        logger.error(f"API call failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url,
            "method": method
        }


@web_scraping_tool(
    name="batch_requests",
    description="批量执行HTTP请求，支持并发控制和请求间延迟，适合大量数据抓取",
    schema={
        "type": "object",
        "properties": {
            "requests": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "url": {"type": "string", "description": "请求URL"},
                        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"], "default": "GET"},
                        "headers": {"type": "object", "additionalProperties": {"type": "string"}},
                        "params": {"type": "object"},
                        "data": {"type": ["string", "object"]},
                        "json_data": {"type": "object"}
                    },
                    "required": ["url"]
                },
                "description": "请求列表"
            },
            "max_concurrent": {"type": "integer", "minimum": 1, "maximum": 20, "description": "最大并发数", "default": 5},
            "delay_between_requests": {"type": "number", "minimum": 0, "description": "请求间延迟（秒）", "default": 0.1}
        },
        "required": ["requests"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "批量请求是否全部成功"},
            "results": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "status_code": {"type": "integer"},
                        "content": {"type": ["string", "object"]},
                        "error": {"type": "string"}
                    }
                },
                "description": "每个请求的结果列表"
            },
            "summary": {
                "type": "object",
                "properties": {
                    "total": {"type": "integer", "description": "总请求数"},
                    "successful": {"type": "integer", "description": "成功请求数"},
                    "failed": {"type": "integer", "description": "失败请求数"},
                    "total_time": {"type": "number", "description": "总耗时（秒）"}
                }
            }
        }
    },
    metadata={"tags": ["batch", "concurrent", "bulk"]}
)
async def batch_requests(
    requests: List[Dict[str, Any]],
    max_concurrent: int = 5,
    delay_between_requests: float = 0.1
) -> Dict[str, Any]:
    """
    批量HTTP请求

    Args:
        requests: 请求列表，每个请求包含url、method等参数
        max_concurrent: 最大并发数
        delay_between_requests: 请求间延迟

    Returns:
        批量请求结果
    """
    try:
        logger.info(f"Starting batch requests: {len(requests)} requests")

        async def process_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
            """处理单个请求"""
            try:
                if delay_between_requests > 0:
                    await asyncio.sleep(delay_between_requests)

                return await http_request(**request_data)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e),
                    "request": request_data
                }

        # 使用信号量限制并发数
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_request(request_data):
            async with semaphore:
                return await process_request(request_data)

        # 执行批量请求
        tasks = [limited_request(req) for req in requests]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        successful = 0
        failed = 0
        processed_results = []

        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "success": False,
                    "error": str(result),
                    "request_index": i,
                    "request": requests[i]
                })
                failed += 1
            else:
                processed_results.append({
                    **result,
                    "request_index": i
                })
                if result.get("success", False):
                    successful += 1
                else:
                    failed += 1

        batch_result = {
            "success": True,
            "total_requests": len(requests),
            "successful": successful,
            "failed": failed,
            "results": processed_results
        }

        logger.info(f"Batch requests completed: {successful} successful, {failed} failed")
        return batch_result

    except Exception as e:
        logger.error(f"Batch requests failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_requests": len(requests)
        }


@web_scraping_tool(
    name="parse_html",
    description="解析HTML内容，提取标题、段落、表格、链接等结构化数据",
    schema={
        "type": "object",
        "properties": {
            "html_content": {"type": "string", "description": "HTML内容字符串"},
            "url": {"type": "string", "description": "HTML来源URL（可选，用于处理相对链接）"},
            "extract_tables": {"type": "boolean", "description": "是否提取表格数据", "default": False},
            "extract_forms": {"type": "boolean", "description": "是否提取表单信息", "default": False},
            "extract_meta": {"type": "boolean", "description": "是否提取meta标签", "default": True},
            "css_selectors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要提取的CSS选择器列表"
            },
            "remove_scripts": {"type": "boolean", "description": "是否移除script标签", "default": True},
            "remove_styles": {"type": "boolean", "description": "是否移除style标签", "default": True}
        },
        "required": ["html_content"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "title": {"type": "string", "description": "页面标题"},
            "headings": {"type": "array", "items": {"type": "object"}, "description": "标题列表(h1-h6)"},
            "paragraphs": {"type": "array", "items": {"type": "string"}, "description": "段落文本"},
            "links": {"type": "array", "items": {"type": "object"}, "description": "链接列表"},
            "images": {"type": "array", "items": {"type": "object"}, "description": "图片列表"},
            "tables": {"type": "array", "items": {"type": "array"}, "description": "表格数据"},
            "forms": {"type": "array", "items": {"type": "object"}, "description": "表单信息"},
            "meta_tags": {"type": "object", "description": "meta标签信息"},
            "css_extracts": {"type": "object", "description": "CSS选择器提取结果"},
            "text_content": {"type": "string", "description": "纯文本内容"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["html", "parsing", "extraction", "structured-data"]}
)
async def parse_html(
    html_content: str,
    url: Optional[str] = None,
    extract_tables: bool = False,
    extract_forms: bool = False,
    extract_meta: bool = True,
    css_selectors: Optional[List[str]] = None,
    remove_scripts: bool = True,
    remove_styles: bool = True
) -> Dict[str, Any]:
    """解析HTML内容，提取结构化数据"""
    try:
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin, urlparse
        import re

        # 解析HTML
        soup = BeautifulSoup(html_content, 'html.parser')

        # 移除不需要的元素
        if remove_scripts:
            for script in soup.find_all('script'):
                script.decompose()
        if remove_styles:
            for style in soup.find_all('style'):
                style.decompose()

        result = {
            "success": True,
            "title": "",
            "headings": [],
            "paragraphs": [],
            "links": [],
            "images": [],
            "tables": [],
            "forms": [],
            "meta_tags": {},
            "css_extracts": {},
            "text_content": ""
        }

        # 提取标题
        title_tag = soup.find('title')
        if title_tag:
            result["title"] = title_tag.get_text().strip()

        # 提取各级标题
        for i in range(1, 7):
            headings = soup.find_all(f'h{i}')
            for heading in headings:
                result["headings"].append({
                    "level": i,
                    "text": heading.get_text().strip(),
                    "id": heading.get('id'),
                    "class": heading.get('class')
                })

        # 提取段落
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text:
                result["paragraphs"].append(text)

        # 提取链接
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            if url:
                href = urljoin(url, href)
            result["links"].append({
                "text": link.get_text().strip(),
                "href": href,
                "title": link.get('title'),
                "class": link.get('class')
            })

        # 提取图片
        images = soup.find_all('img')
        for img in images:
            src = img.get('src')
            if src and url:
                src = urljoin(url, src)
            result["images"].append({
                "src": src,
                "alt": img.get('alt'),
                "title": img.get('title'),
                "width": img.get('width'),
                "height": img.get('height'),
                "class": img.get('class')
            })

        # 提取表格
        if extract_tables:
            tables = soup.find_all('table')
            for table in tables:
                table_data = []
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text().strip() for cell in cells]
                    table_data.append(row_data)
                result["tables"].append(table_data)

        # 提取表单
        if extract_forms:
            forms = soup.find_all('form')
            for form in forms:
                inputs = form.find_all(['input', 'textarea', 'select'])
                form_data = {
                    "action": form.get('action'),
                    "method": form.get('method', 'get'),
                    "fields": []
                }
                for input_elem in inputs:
                    field = {
                        "name": input_elem.get('name'),
                        "type": input_elem.get('type'),
                        "value": input_elem.get('value'),
                        "required": input_elem.has_attr('required')
                    }
                    form_data["fields"].append(field)
                result["forms"].append(form_data)

        # 提取meta标签
        if extract_meta:
            meta_tags = soup.find_all('meta')
            for meta in meta_tags:
                name = meta.get('name') or meta.get('property') or meta.get('http-equiv')
                content = meta.get('content')
                if name and content:
                    result["meta_tags"][name] = content

        # CSS选择器提取
        if css_selectors:
            for selector in css_selectors:
                try:
                    elements = soup.select(selector)
                    result["css_extracts"][selector] = [
                        {
                            "text": elem.get_text().strip(),
                            "html": str(elem),
                            "attributes": elem.attrs
                        } for elem in elements
                    ]
                except Exception as e:
                    result["css_extracts"][selector] = {"error": str(e)}

        # 提取纯文本
        result["text_content"] = soup.get_text().strip()

        logger.info(f"HTML parsing successful: extracted {len(result['paragraphs'])} paragraphs, {len(result['links'])} links")
        return result

    except Exception as e:
        logger.error(f"HTML parsing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@web_scraping_tool(
    name="parse_markdown",
    description="解析Markdown内容，提取标题、代码块、表格等结构化数据",
    schema={
        "type": "object",
        "properties": {
            "markdown_content": {"type": "string", "description": "Markdown内容字符串"},
            "extract_code_blocks": {"type": "boolean", "description": "是否提取代码块", "default": True},
            "extract_tables": {"type": "boolean", "description": "是否提取表格", "default": True},
            "extract_links": {"type": "boolean", "description": "是否提取链接", "default": True},
            "convert_to_html": {"type": "boolean", "description": "是否转换为HTML", "default": False}
        },
        "required": ["markdown_content"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "headings": {"type": "array", "items": {"type": "object"}, "description": "标题列表"},
            "paragraphs": {"type": "array", "items": {"type": "string"}, "description": "段落文本"},
            "code_blocks": {"type": "array", "items": {"type": "object"}, "description": "代码块"},
            "tables": {"type": "array", "items": {"type": "array"}, "description": "表格数据"},
            "links": {"type": "array", "items": {"type": "object"}, "description": "链接列表"},
            "images": {"type": "array", "items": {"type": "object"}, "description": "图片列表"},
            "html_content": {"type": "string", "description": "转换后的HTML（如果请求）"},
            "text_content": {"type": "string", "description": "纯文本内容"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["markdown", "parsing", "documentation", "text"]}
)
async def parse_markdown(
    markdown_content: str,
    extract_code_blocks: bool = True,
    extract_tables: bool = True,
    extract_links: bool = True,
    convert_to_html: bool = False
) -> Dict[str, Any]:
    """解析Markdown内容，提取结构化数据"""
    try:
        import re

        result = {
            "success": True,
            "headings": [],
            "paragraphs": [],
            "code_blocks": [],
            "tables": [],
            "links": [],
            "images": [],
            "html_content": "",
            "text_content": ""
        }

        lines = markdown_content.split('\n')
        current_paragraph = ""
        in_code_block = False
        current_code_block = {"language": "", "code": ""}

        for line in lines:
            # 提取标题
            if line.startswith('#'):
                level = len(line) - len(line.lstrip('#'))
                if level <= 6:
                    title_text = line.lstrip('#').strip()
                    result["headings"].append({
                        "level": level,
                        "text": title_text
                    })
                    continue

            # 处理代码块
            if extract_code_blocks:
                if line.startswith('```'):
                    if in_code_block:
                        # 结束代码块
                        result["code_blocks"].append(current_code_block.copy())
                        current_code_block = {"language": "", "code": ""}
                        in_code_block = False
                    else:
                        # 开始代码块
                        language = line[3:].strip()
                        current_code_block["language"] = language
                        in_code_block = True
                    continue

                if in_code_block:
                    current_code_block["code"] += line + "\n"
                    continue

            # 提取表格
            if extract_tables and '|' in line and line.strip():
                # 简单表格检测
                if not hasattr(parse_markdown, '_current_table'):
                    parse_markdown._current_table = []

                cells = [cell.strip() for cell in line.split('|') if cell.strip()]
                if cells and not all(cell in ['-', ':---:', ':---', '---:'] for cell in cells):
                    parse_markdown._current_table.append(cells)
            else:
                # 完成当前表格
                if hasattr(parse_markdown, '_current_table') and parse_markdown._current_table:
                    result["tables"].append(parse_markdown._current_table)
                    delattr(parse_markdown, '_current_table')

            # 提取链接和图片
            if extract_links:
                # 链接 [text](url)
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                links = re.findall(link_pattern, line)
                for text, url in links:
                    result["links"].append({"text": text, "href": url})

                # 图片 ![alt](src)
                image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
                images = re.findall(image_pattern, line)
                for alt, src in images:
                    result["images"].append({"alt": alt, "src": src})

            # 收集段落
            if line.strip() and not line.startswith('#') and not in_code_block:
                current_paragraph += line + " "
            else:
                if current_paragraph.strip():
                    result["paragraphs"].append(current_paragraph.strip())
                    current_paragraph = ""

        # 处理最后的段落
        if current_paragraph.strip():
            result["paragraphs"].append(current_paragraph.strip())

        # 完成最后的表格
        if hasattr(parse_markdown, '_current_table') and parse_markdown._current_table:
            result["tables"].append(parse_markdown._current_table)
            delattr(parse_markdown, '_current_table')

        # 转换为HTML（如果需要）
        if convert_to_html:
            try:
                import markdown
                result["html_content"] = markdown.markdown(markdown_content)
            except ImportError:
                # 简单的Markdown到HTML转换
                html_lines = []
                for line in markdown_content.split('\n'):
                    if line.startswith('#'):
                        level = len(line) - len(line.lstrip('#'))
                        text = line.lstrip('#').strip()
                        html_lines.append(f'<h{level}>{text}</h{level}>')
                    else:
                        html_lines.append(f'<p>{line}</p>')
                result["html_content"] = '\n'.join(html_lines)

        # 纯文本内容
        result["text_content"] = re.sub(r'[#*`_\[\]()!]', '', markdown_content)

        logger.info(f"Markdown parsing successful: {len(result['headings'])} headings, {len(result['paragraphs'])} paragraphs")
        return result

    except Exception as e:
        logger.error(f"Markdown parsing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@web_scraping_tool(
    name="parse_xml",
    description="解析XML内容，提取元素、属性、文本等结构化数据",
    schema={
        "type": "object",
        "properties": {
            "xml_content": {"type": "string", "description": "XML内容字符串"},
            "xpath_queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要执行的XPath查询列表"
            },
            "extract_attributes": {"type": "boolean", "description": "是否提取元素属性", "default": True},
            "namespace_map": {"type": "object", "description": "XML命名空间映射"},
            "parse_as_dict": {"type": "boolean", "description": "是否转换为字典格式", "default": True}
        },
        "required": ["xml_content"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "root_tag": {"type": "string", "description": "根元素标签"},
            "structure": {"type": "object", "description": "XML结构树"},
            "xpath_results": {"type": "object", "description": "XPath查询结果"},
            "elements": {"type": "array", "items": {"type": "object"}, "description": "元素列表"},
            "text_content": {"type": "string", "description": "纯文本内容"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["xml", "parsing", "xpath", "structured-data"]}
)
async def parse_xml(
    xml_content: str,
    xpath_queries: Optional[List[str]] = None,
    extract_attributes: bool = True,
    namespace_map: Optional[Dict[str, str]] = None,
    parse_as_dict: bool = True
) -> Dict[str, Any]:
    """解析XML内容，提取结构化数据"""
    try:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom
        import re

        result = {
            "success": True,
            "root_tag": "",
            "structure": {},
            "xpath_results": {},
            "elements": [],
            "text_content": ""
        }

        # 解析XML
        root = ET.fromstring(xml_content)
        result["root_tag"] = root.tag

        # 递归转换XML为字典
        def element_to_dict(element):
            result_dict = {}

            # 添加属性
            if extract_attributes and element.attrib:
                result_dict["@attributes"] = element.attrib

            # 添加文本内容
            if element.text and element.text.strip():
                result_dict["@text"] = element.text.strip()

            # 处理子元素
            children = {}
            for child in element:
                child_dict = element_to_dict(child)
                if child.tag in children:
                    if not isinstance(children[child.tag], list):
                        children[child.tag] = [children[child.tag]]
                    children[child.tag].append(child_dict)
                else:
                    children[child.tag] = child_dict

            if children:
                result_dict.update(children)

            return result_dict

        # 转换为字典格式
        if parse_as_dict:
            result["structure"] = {root.tag: element_to_dict(root)}

        # 提取所有元素信息
        for elem in root.iter():
            elem_info = {
                "tag": elem.tag,
                "text": elem.text.strip() if elem.text else "",
                "attributes": dict(elem.attrib) if extract_attributes else {},
                "tail": elem.tail.strip() if elem.tail else ""
            }
            result["elements"].append(elem_info)

        # 执行XPath查询
        if xpath_queries:
            for query in xpath_queries:
                try:
                    elements = root.findall(query, namespace_map or {})
                    result["xpath_results"][query] = [
                        {
                            "tag": elem.tag,
                            "text": elem.text.strip() if elem.text else "",
                            "attributes": dict(elem.attrib) if extract_attributes else {}
                        } for elem in elements
                    ]
                except Exception as e:
                    result["xpath_results"][query] = {"error": str(e)}

        # 提取纯文本
        result["text_content"] = ET.tostring(root, method='text', encoding='unicode').strip()

        logger.info(f"XML parsing successful: {len(result['elements'])} elements extracted")
        return result

    except Exception as e:
        logger.error(f"XML parsing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@web_scraping_tool(
    name="parse_json",
    description="解析和处理JSON数据，支持JSONPath查询和数据转换",
    schema={
        "type": "object",
        "properties": {
            "json_content": {"type": "string", "description": "JSON内容字符串"},
            "jsonpath_queries": {
                "type": "array",
                "items": {"type": "string"},
                "description": "JSONPath查询表达式列表"
            },
            "flatten_arrays": {"type": "boolean", "description": "是否展平数组", "default": False},
            "extract_keys": {"type": "array", "items": {"type": "string"}, "description": "要提取的特定键"},
            "max_depth": {"type": "integer", "description": "最大解析深度", "default": 10}
        },
        "required": ["json_content"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "data": {"type": "object", "description": "解析后的JSON数据"},
            "jsonpath_results": {"type": "object", "description": "JSONPath查询结果"},
            "extracted_keys": {"type": "object", "description": "提取的键值对"},
            "statistics": {"type": "object", "description": "数据统计信息"},
            "flattened": {"type": "object", "description": "展平后的数据"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["json", "parsing", "jsonpath", "data-processing"]}
)
async def parse_json(
    json_content: str,
    jsonpath_queries: Optional[List[str]] = None,
    flatten_arrays: bool = False,
    extract_keys: Optional[List[str]] = None,
    max_depth: int = 10
) -> Dict[str, Any]:
    """解析JSON数据，支持复杂查询和转换"""
    try:
        import json
        import re
        from collections import defaultdict

        # 解析JSON
        data = json.loads(json_content)

        result = {
            "success": True,
            "data": data,
            "jsonpath_results": {},
            "extracted_keys": {},
            "statistics": {},
            "flattened": {}
        }

        # 统计信息
        def collect_stats(obj, depth=0):
            stats = {"total_keys": 0, "total_values": 0, "max_depth": depth, "data_types": defaultdict(int)}

            if isinstance(obj, dict):
                stats["total_keys"] += len(obj)
                for key, value in obj.items():
                    stats["data_types"][type(value).__name__] += 1
                    if isinstance(value, (dict, list)) and depth < max_depth:
                        sub_stats = collect_stats(value, depth + 1)
                        stats["total_keys"] += sub_stats["total_keys"]
                        stats["total_values"] += sub_stats["total_values"]
                        stats["max_depth"] = max(stats["max_depth"], sub_stats["max_depth"])
                        for k, v in sub_stats["data_types"].items():
                            stats["data_types"][k] += v
            elif isinstance(obj, list):
                stats["total_values"] += len(obj)
                for item in obj:
                    if isinstance(item, (dict, list)) and depth < max_depth:
                        sub_stats = collect_stats(item, depth + 1)
                        stats["total_keys"] += sub_stats["total_keys"]
                        stats["total_values"] += sub_stats["total_values"]
                        stats["max_depth"] = max(stats["max_depth"], sub_stats["max_depth"])
                        for k, v in sub_stats["data_types"].items():
                            stats["data_types"][k] += v
            else:
                stats["total_values"] += 1
                stats["data_types"][type(obj).__name__] += 1

            return stats

        result["statistics"] = collect_stats(data)
        result["statistics"]["data_types"] = dict(result["statistics"]["data_types"])

        # 简单的JSONPath查询实现
        def simple_jsonpath(obj, path):
            """简化的JSONPath实现"""
            if not path:
                return [obj]

            if path.startswith('$.'):
                path = path[2:]

            parts = path.split('.')
            current = [obj]

            for part in parts:
                next_level = []
                for item in current:
                    if part == '*':
                        if isinstance(item, dict):
                            next_level.extend(item.values())
                        elif isinstance(item, list):
                            next_level.extend(item)
                    elif '[' in part and ']' in part:
                        # 数组索引处理
                        key = part.split('[')[0]
                        index_str = part.split('[')[1].split(']')[0]
                        if isinstance(item, dict) and key in item:
                            if index_str == '*':
                                if isinstance(item[key], list):
                                    next_level.extend(item[key])
                            else:
                                try:
                                    index = int(index_str)
                                    if isinstance(item[key], list) and 0 <= index < len(item[key]):
                                        next_level.append(item[key][index])
                                except ValueError:
                                    pass
                    elif isinstance(item, dict) and part in item:
                        next_level.append(item[part])
                current = next_level

            return current

        # 执行JSONPath查询
        if jsonpath_queries:
            for query in jsonpath_queries:
                try:
                    result["jsonpath_results"][query] = simple_jsonpath(data, query)
                except Exception as e:
                    result["jsonpath_results"][query] = {"error": str(e)}

        # 提取特定键
        if extract_keys:
            def extract_recursive(obj, keys, prefix=""):
                extracted = {}
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        full_key = f"{prefix}.{key}" if prefix else key
                        if key in keys:
                            extracted[full_key] = value
                        if isinstance(value, (dict, list)):
                            sub_extracted = extract_recursive(value, keys, full_key)
                            extracted.update(sub_extracted)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            sub_extracted = extract_recursive(item, keys, f"{prefix}[{i}]")
                            extracted.update(sub_extracted)
                return extracted

            result["extracted_keys"] = extract_recursive(data, extract_keys)

        # 展平数据
        if flatten_arrays:
            def flatten_recursive(obj, parent_key="", sep="."):
                items = []
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_key = f"{parent_key}{sep}{key}" if parent_key else key
                        if isinstance(value, (dict, list)):
                            items.extend(flatten_recursive(value, new_key, sep).items())
                        else:
                            items.append((new_key, value))
                elif isinstance(obj, list):
                    for i, value in enumerate(obj):
                        new_key = f"{parent_key}[{i}]"
                        if isinstance(value, (dict, list)):
                            items.extend(flatten_recursive(value, new_key, sep).items())
                        else:
                            items.append((new_key, value))
                return dict(items)

            result["flattened"] = flatten_recursive(data)

        logger.info(f"JSON parsing successful: {result['statistics']['total_keys']} keys, {result['statistics']['total_values']} values")
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing failed - invalid JSON: {e}")
        return {
            "success": False,
            "error": f"Invalid JSON format: {str(e)}"
        }
    except Exception as e:
        logger.error(f"JSON processing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@web_scraping_tool(
    name="parse_rss",
    description="解析RSS/Atom订阅源，提取文章、标题、链接等信息",
    schema={
        "type": "object",
        "properties": {
            "rss_content": {"type": "string", "description": "RSS/Atom内容字符串"},
            "max_items": {"type": "integer", "description": "最大提取项目数", "default": 50},
            "extract_content": {"type": "boolean", "description": "是否提取完整内容", "default": True},
            "parse_dates": {"type": "boolean", "description": "是否解析日期", "default": True},
            "include_raw": {"type": "boolean", "description": "是否包含原始XML", "default": False}
        },
        "required": ["rss_content"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "feed_type": {"type": "string", "description": "订阅源类型(RSS/Atom)"},
            "feed_info": {"type": "object", "description": "订阅源信息"},
            "items": {"type": "array", "items": {"type": "object"}, "description": "条目列表"},
            "statistics": {"type": "object", "description": "统计信息"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["rss", "atom", "feed", "news", "syndication"]}
)
async def parse_rss(
    rss_content: str,
    max_items: int = 50,
    extract_content: bool = True,
    parse_dates: bool = True,
    include_raw: bool = False
) -> Dict[str, Any]:
    """解析RSS/Atom订阅源"""
    try:
        import xml.etree.ElementTree as ET
        from datetime import datetime
        import re

        # 解析XML
        root = ET.fromstring(rss_content)

        result = {
            "success": True,
            "feed_type": "",
            "feed_info": {},
            "items": [],
            "statistics": {}
        }

        # 检测订阅源类型
        if root.tag == 'rss' or 'rss' in root.tag.lower():
            result["feed_type"] = "RSS"
            channel = root.find('.//channel')

            # RSS订阅源信息
            if channel is not None:
                result["feed_info"] = {
                    "title": getattr(channel.find('title'), 'text', ''),
                    "description": getattr(channel.find('description'), 'text', ''),
                    "link": getattr(channel.find('link'), 'text', ''),
                    "language": getattr(channel.find('language'), 'text', ''),
                    "lastBuildDate": getattr(channel.find('lastBuildDate'), 'text', ''),
                    "generator": getattr(channel.find('generator'), 'text', '')
                }

                # 提取RSS条目
                items = channel.findall('item')[:max_items]
                for item in items:
                    item_data = {
                        "title": getattr(item.find('title'), 'text', ''),
                        "description": getattr(item.find('description'), 'text', ''),
                        "link": getattr(item.find('link'), 'text', ''),
                        "pubDate": getattr(item.find('pubDate'), 'text', ''),
                        "guid": getattr(item.find('guid'), 'text', ''),
                        "author": getattr(item.find('author'), 'text', ''),
                        "categories": []
                    }

                    # 提取分类
                    for category in item.findall('category'):
                        if category.text:
                            item_data["categories"].append(category.text)

                    # 提取内容
                    if extract_content:
                        content = item.find('content:encoded', {'content': 'http://purl.org/rss/1.0/modules/content/'})
                        if content is not None:
                            item_data["content"] = content.text

                    if include_raw:
                        item_data["raw_xml"] = ET.tostring(item, encoding='unicode')

                    result["items"].append(item_data)

        elif 'atom' in root.tag.lower() or root.tag.endswith('feed'):
            result["feed_type"] = "Atom"

            # Atom订阅源信息
            result["feed_info"] = {
                "title": getattr(root.find('.//{http://www.w3.org/2005/Atom}title'), 'text', ''),
                "subtitle": getattr(root.find('.//{http://www.w3.org/2005/Atom}subtitle'), 'text', ''),
                "id": getattr(root.find('.//{http://www.w3.org/2005/Atom}id'), 'text', ''),
                "updated": getattr(root.find('.//{http://www.w3.org/2005/Atom}updated'), 'text', ''),
                "generator": getattr(root.find('.//{http://www.w3.org/2005/Atom}generator'), 'text', '')
            }

            # 查找链接
            link_elem = root.find('.//{http://www.w3.org/2005/Atom}link')
            if link_elem is not None:
                result["feed_info"]["link"] = link_elem.get('href', '')

            # 提取Atom条目
            entries = root.findall('.//{http://www.w3.org/2005/Atom}entry')[:max_items]
            for entry in entries:
                item_data = {
                    "title": getattr(entry.find('.//{http://www.w3.org/2005/Atom}title'), 'text', ''),
                    "summary": getattr(entry.find('.//{http://www.w3.org/2005/Atom}summary'), 'text', ''),
                    "id": getattr(entry.find('.//{http://www.w3.org/2005/Atom}id'), 'text', ''),
                    "published": getattr(entry.find('.//{http://www.w3.org/2005/Atom}published'), 'text', ''),
                    "updated": getattr(entry.find('.//{http://www.w3.org/2005/Atom}updated'), 'text', ''),
                    "categories": []
                }

                # 查找链接
                link_elem = entry.find('.//{http://www.w3.org/2005/Atom}link')
                if link_elem is not None:
                    item_data["link"] = link_elem.get('href', '')

                # 查找作者
                author_elem = entry.find('.//{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name')
                if author_elem is not None:
                    item_data["author"] = author_elem.text

                # 提取分类
                for category in entry.findall('.//{http://www.w3.org/2005/Atom}category'):
                    term = category.get('term')
                    if term:
                        item_data["categories"].append(term)

                # 提取内容
                if extract_content:
                    content = entry.find('.//{http://www.w3.org/2005/Atom}content')
                    if content is not None:
                        item_data["content"] = content.text

                if include_raw:
                    item_data["raw_xml"] = ET.tostring(entry, encoding='unicode')

                result["items"].append(item_data)

        # 日期解析
        if parse_dates:
            for item in result["items"]:
                for date_field in ['pubDate', 'published', 'updated']:
                    if date_field in item and item[date_field]:
                        try:
                            # 简单日期解析
                            date_str = item[date_field]
                            # 移除时区信息进行简单解析
                            clean_date = re.sub(r'\s*[+-]\d{4}$', '', date_str)
                            clean_date = re.sub(r'\s*[A-Z]{3}$', '', clean_date)
                            item[f"{date_field}_parsed"] = clean_date
                        except:
                            pass

        # 统计信息
        result["statistics"] = {
            "total_items": len(result["items"]),
            "feed_type": result["feed_type"],
            "has_content": sum(1 for item in result["items"] if item.get("content")),
            "categories_count": len(set(cat for item in result["items"] for cat in item.get("categories", [])))
        }

        logger.info(f"RSS parsing successful: {result['feed_type']}, {len(result['items'])} items")
        return result

    except Exception as e:
        logger.error(f"RSS parsing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@web_scraping_tool(
    name="extract_css_selector",
    description="使用CSS选择器从网页中提取特定内容，支持复杂选择器和批量提取",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "目标网页URL"},
            "html_content": {"type": "string", "description": "HTML内容字符串（可选，优先使用）"},
            "css_selectors": {
                "type": "array",
                "items": {"type": "object"},
                "description": "CSS选择器配置列表",
                "properties": {
                    "name": {"type": "string", "description": "提取数据的名称"},
                    "selector": {"type": "string", "description": "CSS选择器"},
                    "attribute": {"type": "string", "description": "要提取的属性（默认为text）"},
                    "multiple": {"type": "boolean", "description": "是否提取多个元素", "default": False}
                }
            },
            "wait_for_element": {"type": "string", "description": "等待特定元素出现的选择器"},
            "headers": {"type": "object", "description": "HTTP请求头"}
        },
        "required": ["css_selectors"],
        "oneOf": [
            {"required": ["url"]},
            {"required": ["html_content"]}
        ]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "extracted_data": {"type": "object", "description": "提取的数据"},
            "selectors_used": {"type": "array", "description": "使用的选择器列表"},
            "url": {"type": "string", "description": "源URL"},
            "statistics": {"type": "object", "description": "提取统计信息"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["css", "selector", "extraction", "scraping"]}
)
async def extract_css_selector(
    css_selectors: List[Dict[str, Any]],
    url: Optional[str] = None,
    html_content: Optional[str] = None,
    wait_for_element: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """使用CSS选择器提取网页内容"""
    try:
        from bs4 import BeautifulSoup
        import time

        # 获取HTML内容
        if html_content:
            html = html_content
            source_url = url or "provided_html"
        elif url:
            # 使用现有的http_request功能
            request_result = await http_request(url, headers=headers or {})
            if not request_result.get("success"):
                return {
                    "success": False,
                    "error": f"Failed to fetch URL: {request_result.get('error')}"
                }
            html = request_result.get("content_text", "")
            source_url = url
        else:
            return {
                "success": False,
                "error": "Either 'url' or 'html_content' must be provided"
            }

        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        result = {
            "success": True,
            "extracted_data": {},
            "selectors_used": [],
            "url": source_url,
            "statistics": {
                "total_selectors": len(css_selectors),
                "successful_extractions": 0,
                "failed_extractions": 0,
                "total_elements_found": 0
            }
        }

        # 处理每个CSS选择器
        for selector_config in css_selectors:
            name = selector_config.get("name", f"selector_{len(result['selectors_used'])}")
            selector = selector_config.get("selector")
            attribute = selector_config.get("attribute", "text")
            multiple = selector_config.get("multiple", False)

            if not selector:
                result["statistics"]["failed_extractions"] += 1
                result["extracted_data"][name] = {"error": "No selector provided"}
                continue

            try:
                # 查找元素
                elements = soup.select(selector)

                if not elements:
                    result["extracted_data"][name] = None if not multiple else []
                    result["selectors_used"].append({
                        "name": name,
                        "selector": selector,
                        "found": 0
                    })
                    continue

                result["statistics"]["total_elements_found"] += len(elements)

                # 提取数据
                if multiple:
                    extracted_values = []
                    for element in elements:
                        if attribute == "text":
                            value = element.get_text().strip()
                        elif attribute == "html":
                            value = str(element)
                        else:
                            value = element.get(attribute, "")

                        # 如果需要，添加额外的属性
                        if isinstance(value, str):
                            extracted_values.append(value)
                        else:
                            # 提供更完整的元素信息
                            element_data = {
                                "text": element.get_text().strip(),
                                "html": str(element),
                                "attributes": dict(element.attrs),
                                "tag": element.name
                            }
                            if attribute in element_data:
                                element_data["requested_value"] = element_data[attribute]
                            extracted_values.append(element_data)

                    result["extracted_data"][name] = extracted_values
                else:
                    element = elements[0]
                    if attribute == "text":
                        result["extracted_data"][name] = element.get_text().strip()
                    elif attribute == "html":
                        result["extracted_data"][name] = str(element)
                    else:
                        result["extracted_data"][name] = element.get(attribute, "")

                result["selectors_used"].append({
                    "name": name,
                    "selector": selector,
                    "found": len(elements),
                    "multiple": multiple,
                    "attribute": attribute
                })
                result["statistics"]["successful_extractions"] += 1

            except Exception as e:
                result["statistics"]["failed_extractions"] += 1
                result["extracted_data"][name] = {"error": str(e)}
                result["selectors_used"].append({
                    "name": name,
                    "selector": selector,
                    "error": str(e)
                })

        logger.info(f"CSS extraction successful: {result['statistics']['successful_extractions']}/{result['statistics']['total_selectors']} selectors")
        return result

    except Exception as e:
        logger.error(f"CSS selector extraction failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@web_scraping_tool(
    name="smart_extract_and_parse",
    description="智能抓取并解析网页内容，根据内容类型自动选择最适合的解析方式（HTML/JSON/XML/RSS）",
    schema={
        "type": "object",
        "properties": {
            "url": {"type": "string", "description": "目标网页URL"},
            "auto_detect_format": {"type": "boolean", "description": "是否自动检测内容格式", "default": True},
            "force_format": {"type": "string", "enum": ["html", "json", "xml", "rss", "markdown"], "description": "强制指定解析格式"},
            "extract_options": {
                "type": "object",
                "description": "解析选项",
                "properties": {
                    "extract_tables": {"type": "boolean", "default": True},
                    "extract_forms": {"type": "boolean", "default": False},
                    "extract_meta": {"type": "boolean", "default": True},
                    "css_selectors": {"type": "array", "items": {"type": "string"}},
                    "max_items": {"type": "integer", "default": 50}
                }
            },
            "headers": {"type": "object", "description": "HTTP请求头"},
            "follow_redirects": {"type": "boolean", "description": "是否跟随重定向", "default": True}
        },
        "required": ["url"]
    },
    returns={
        "type": "object",
        "properties": {
            "success": {"type": "boolean", "description": "是否成功"},
            "detected_format": {"type": "string", "description": "检测到的内容格式"},
            "url": {"type": "string", "description": "最终URL（处理重定向后）"},
            "raw_content": {"type": "string", "description": "原始内容"},
            "parsed_content": {"type": "object", "description": "解析后的结构化内容"},
            "metadata": {"type": "object", "description": "元数据信息"},
            "statistics": {"type": "object", "description": "统计信息"},
            "error": {"type": "string", "description": "错误信息（如果失败）"}
        }
    },
    metadata={"tags": ["smart-parsing", "auto-detect", "multi-format", "extraction"]}
)
async def smart_extract_and_parse(
    url: str,
    auto_detect_format: bool = True,
    force_format: Optional[str] = None,
    extract_options: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, str]] = None,
    follow_redirects: bool = True
) -> Dict[str, Any]:
    """智能抓取并解析网页内容"""
    try:
        import re
        from urllib.parse import urlparse

        extract_options = extract_options or {}

        # 1. 抓取网页内容
        fetch_result = await http_request(url, headers=headers or {})
        if not fetch_result.get("success"):
            return {
                "success": False,
                "error": f"Failed to fetch URL: {fetch_result.get('error')}"
            }

        raw_content = fetch_result.get("content_text", "")
        final_url = fetch_result.get("url", url)
        content_type = fetch_result.get("content_type", "").lower()

        result = {
            "success": True,
            "detected_format": "",
            "url": final_url,
            "raw_content": raw_content,
            "parsed_content": {},
            "metadata": {
                "content_type": content_type,
                "content_length": len(raw_content),
                "url_domain": urlparse(final_url).netloc,
                "response_info": {
                    "status_code": fetch_result.get("status_code"),
                    "encoding": fetch_result.get("encoding")
                }
            },
            "statistics": {}
        }

        # 2. 格式检测
        detected_format = force_format

        if auto_detect_format and not force_format:
            # 基于内容类型检测
            if "application/json" in content_type:
                detected_format = "json"
            elif "application/xml" in content_type or "text/xml" in content_type:
                detected_format = "xml"
            elif "application/rss+xml" in content_type or "application/atom+xml" in content_type:
                detected_format = "rss"
            elif "text/html" in content_type:
                detected_format = "html"
            else:
                # 基于内容特征检测
                content_lower = raw_content.strip().lower()
                if content_lower.startswith('{') or content_lower.startswith('['):
                    detected_format = "json"
                elif content_lower.startswith('<?xml') or '<rss' in content_lower or '<feed' in content_lower:
                    if 'rss' in content_lower or 'atom' in content_lower:
                        detected_format = "rss"
                    else:
                        detected_format = "xml"
                elif content_lower.startswith('<!doctype html') or '<html' in content_lower:
                    detected_format = "html"
                elif re.match(r'^#+\s', raw_content.strip(), re.MULTILINE):
                    detected_format = "markdown"
                else:
                    detected_format = "html"  # 默认作为HTML处理

        result["detected_format"] = detected_format or "html"

        # 3. 根据格式解析内容
        if result["detected_format"] == "json":
            parse_result = await parse_json(
                raw_content,
                jsonpath_queries=extract_options.get("jsonpath_queries"),
                flatten_arrays=extract_options.get("flatten_arrays", False),
                extract_keys=extract_options.get("extract_keys"),
                max_depth=extract_options.get("max_depth", 10)
            )

        elif result["detected_format"] == "xml":
            parse_result = await parse_xml(
                raw_content,
                xpath_queries=extract_options.get("xpath_queries"),
                extract_attributes=extract_options.get("extract_attributes", True),
                namespace_map=extract_options.get("namespace_map"),
                parse_as_dict=extract_options.get("parse_as_dict", True)
            )

        elif result["detected_format"] == "rss":
            parse_result = await parse_rss(
                raw_content,
                max_items=extract_options.get("max_items", 50),
                extract_content=extract_options.get("extract_content", True),
                parse_dates=extract_options.get("parse_dates", True),
                include_raw=extract_options.get("include_raw", False)
            )

        elif result["detected_format"] == "markdown":
            parse_result = await parse_markdown(
                raw_content,
                extract_code_blocks=extract_options.get("extract_code_blocks", True),
                extract_tables=extract_options.get("extract_tables", True),
                extract_links=extract_options.get("extract_links", True),
                convert_to_html=extract_options.get("convert_to_html", False)
            )

        else:  # HTML
            parse_result = await parse_html(
                raw_content,
                url=final_url,
                extract_tables=extract_options.get("extract_tables", True),
                extract_forms=extract_options.get("extract_forms", False),
                extract_meta=extract_options.get("extract_meta", True),
                css_selectors=extract_options.get("css_selectors"),
                remove_scripts=extract_options.get("remove_scripts", True),
                remove_styles=extract_options.get("remove_styles", True)
            )

        # 4. 合并解析结果
        if parse_result.get("success"):
            result["parsed_content"] = parse_result

            # 提取统计信息
            if "statistics" in parse_result:
                result["statistics"].update(parse_result["statistics"])

            # 根据解析类型添加特定统计信息
            if result["detected_format"] == "html":
                result["statistics"]["parsing_stats"] = {
                    "paragraphs": len(parse_result.get("paragraphs", [])),
                    "links": len(parse_result.get("links", [])),
                    "images": len(parse_result.get("images", [])),
                    "headings": len(parse_result.get("headings", []))
                }
            elif result["detected_format"] == "json":
                result["statistics"]["parsing_stats"] = parse_result.get("statistics", {})
            elif result["detected_format"] in ["xml", "rss"]:
                result["statistics"]["parsing_stats"] = {
                    "elements": len(parse_result.get("elements", [])),
                    "items": len(parse_result.get("items", []))
                }

        else:
            result["parsed_content"] = {"error": parse_result.get("error", "Unknown parsing error")}
            result["statistics"]["parsing_error"] = parse_result.get("error")

        # 5. 添加智能分析
        result["metadata"]["analysis"] = {
            "content_type_detected": result["detected_format"],
            "parsing_successful": parse_result.get("success", False),
            "content_features": {
                "has_structured_data": result["detected_format"] in ["json", "xml", "rss"],
                "has_html_content": result["detected_format"] == "html",
                "estimated_word_count": len(raw_content.split()),
                "has_code_blocks": "```" in raw_content,
                "has_tables": "|" in raw_content or "<table" in raw_content.lower()
            }
        }

        logger.info(f"Smart extraction successful: {final_url}, format: {result['detected_format']}")
        return result

    except Exception as e:
        logger.error(f"Smart extraction failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "url": url
        }


# MCP工具注册信息
MCP_TOOLS = [
    {
        "name": "http_request",
        "description": "Make HTTP requests with support for various methods and configurations",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Request URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"],
                    "default": "GET",
                    "description": "HTTP method"
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers"
                },
                "params": {
                    "type": "object",
                    "description": "URL parameters"
                },
                "data": {
                    "oneOf": [
                        {"type": "string"},
                        {"type": "object"}
                    ],
                    "description": "Request body data"
                },
                "json_data": {
                    "type": "object",
                    "description": "JSON request body"
                },
                "auth": {
                    "type": "array",
                    "items": {"type": "string"},
                    "minItems": 2,
                    "maxItems": 2,
                    "description": "HTTP basic authentication [username, password]"
                },
                "follow_redirects": {
                    "type": "boolean",
                    "description": "Whether to follow redirects"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "fetch_webpage",
        "description": "Fetch and parse webpage content with optional text, links, and images extraction",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Webpage URL"
                },
                "headers": {
                    "type": "object",
                    "description": "Custom request headers"
                },
                "extract_text": {
                    "type": "boolean",
                    "default": True,
                    "description": "Extract plain text from HTML"
                },
                "extract_links": {
                    "type": "boolean",
                    "default": False,
                    "description": "Extract all links from the page"
                },
                "extract_images": {
                    "type": "boolean",
                    "default": False,
                    "description": "Extract all image URLs from the page"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "download_file",
        "description": "Download files from URLs with size limits and optional saving to disk",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "File URL"
                },
                "save_path": {
                    "type": "string",
                    "description": "Local save path (optional, if not provided returns base64 content)"
                },
                "headers": {
                    "type": "object",
                    "description": "Custom request headers"
                },
                "max_size": {
                    "type": "integer",
                    "description": "Maximum file size in bytes"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "api_call",
        "description": "Make RESTful API calls with authentication and JSON handling",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "API endpoint URL"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "default": "GET",
                    "description": "HTTP method"
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers"
                },
                "params": {
                    "type": "object",
                    "description": "URL parameters"
                },
                "json_data": {
                    "type": "object",
                    "description": "JSON request body"
                },
                "auth_token": {
                    "type": "string",
                    "description": "Authentication token"
                },
                "auth_type": {
                    "type": "string",
                    "default": "Bearer",
                    "description": "Authentication type (Bearer, Token, etc.)"
                }
            },
            "required": ["url"]
        }
    },
    {
        "name": "batch_requests",
        "description": "Execute multiple HTTP requests concurrently with rate limiting",
        "inputSchema": {
            "type": "object",
            "properties": {
                "requests": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "url": {"type": "string"},
                            "method": {"type": "string"},
                            "headers": {"type": "object"},
                            "params": {"type": "object"},
                            "data": {"oneOf": [{"type": "string"}, {"type": "object"}]},
                            "json_data": {"type": "object"}
                        },
                        "required": ["url"]
                    },
                    "description": "List of requests to execute"
                },
                "max_concurrent": {
                    "type": "integer",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Maximum concurrent requests"
                },
                "delay_between_requests": {
                    "type": "number",
                    "default": 0.1,
                    "minimum": 0,
                    "description": "Delay between requests in seconds"
                }
            },
            "required": ["requests"]
        }
    }
]