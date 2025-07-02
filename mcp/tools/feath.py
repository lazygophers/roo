from core import log
from core.croe import mcp
import requests
from pydantic import Field


@mcp.tool()
async def fetch_markdown(
    url: str = Field(description="请求的目标URL"),
    params: dict = Field(description="可选的请求参数字典", default=None),
    method: str = Field(description="可选的请求方法", default="get"),
    headers: dict = Field(description="可选的请求头字典", default=None),
    cookies: dict = Field(description="可选的Cookie字典", default=None),
    data: object = Field(description="可选的请求数据对象", default=None),
    json: dict = Field(description="可选的JSON数据字典", default=None),
    timeout: int = Field(description="可选的请求超时时间（秒）", default=30),
    allow_redirects: bool = Field(description="可选的请求是否允许重定向", default=True),
) -> str:
    """获取指定URL的Markdown文本内容.
    Returns:
        str: 响应的Markdown文本内容
    """
    log.info(f"正在请求URL: {url}")
    response = requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        cookies=cookies,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    if response.status_code == 200:
        return response.text
    else:
        log.error(f"请求失败，状态码: {response.status_code}")
        raise Exception("请求失败，状态码:{}".format(response.status_code))


@mcp.tool()
async def fetch_rss(
    url: str = Field(description="请求的目标URL"),
    params: dict = Field(description="可选的请求参数字典", default=None),
    method: str = Field(description="可选的请求方法", default="get"),
    headers: dict = Field(description="可选的请求头字典", default=None),
    cookies: dict = Field(description="可选的Cookie字典", default=None),
    data: object = Field(description="可选的请求数据对象", default=None),
    json: dict = Field(description="可选的JSON数据字典", default=None),
    timeout: int = Field(description="可选的请求超时时间（秒）", default=30),
    allow_redirects: bool = Field(description="可选的请求是否允许重定向", default=True),
) -> str:
    """获取指定URL的RSS订阅内容.
    Returns:
        str: RSS订阅内容的原始字符串
    """
    log.info(f"正在请求URL: {url}")
    response = requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        cookies=cookies,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    if response.status_code == 200:
        return response.text
    else:
        log.error(f"请求失败，状态码: {response.status_code}")
        raise Exception("请求失败，状态码:{}".format(response.status_code))


@mcp.tool()
async def fetch_html(
    url: str = Field(description="请求的目标URL"),
    params: dict = Field(description="可选的请求参数字典", default=None),
    method: str = Field(description="可选的请求方法", default="get"),
    headers: dict = Field(description="可选的请求头字典", default=None),
    cookies: dict = Field(description="可选的Cookie字典", default=None),
    data: object = Field(description="可选的请求数据对象", default=None),
    json: dict = Field(description="可选的JSON数据字典", default=None),
    timeout: int = Field(description="可选的请求超时时间（秒）", default=30),
    allow_redirects: bool = Field(description="可选的请求是否允许重定向", default=True),
) -> str:
    """获取指定URL的HTML页面内容.
    Returns:
        str: HTML页面的原始文本内容
    """
    log.info(f"正在请求URL: {url}")
    response = requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        cookies=cookies,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    if response.status_code == 200:
        return response.text
    else:
        log.error(f"请求失败，状态码: {response.status_code}")
        raise Exception("请求失败，状态码:{}".format(response.status_code))


@mcp.tool()
async def fetch_json(
    url: str = Field(description="请求的目标URL"),
    params: dict = Field(description="可选的请求参数字典", default=None),
    method: str = Field(description="可选的请求方法", default="get"),
    headers: dict = Field(description="可选的请求头字典", default=None),
    cookies: dict = Field(description="可选的Cookie字典", default=None),
    data: object = Field(description="可选的请求数据对象", default=None),
    json: dict = Field(description="可选的JSON数据字典", default=None),
    timeout: int = Field(description="可选的请求超时时间（秒）", default=30),
    allow_redirects: bool = Field(description="可选的请求是否允许重定向", default=True),
) -> dict:
    """获取并解析指定URL的JSON响应.
    Returns:
        dict: 解析后的JSON数据对象
    """
    log.info(f"正在请求URL: {url}")
    response = requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        cookies=cookies,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    if response.status_code == 200:
        return response.json()
    else:
        log.error(f"请求失败，状态码: {response.status_code}")
        raise Exception("请求失败，状态码:{}".format(response.status_code))


@mcp.tool()
async def fetch(
    url: str = Field(description="请求的目标URL"),
    params: dict = Field(description="可选的请求参数字典", default=None),
    method: str = Field(description="可选的请求方法", default="get"),
    headers: dict = Field(description="可选的请求头字典", default=None),
    cookies: dict = Field(description="可选的Cookie字典", default=None),
    data: object = Field(description="可选的请求数据对象", default=None),
    json: dict = Field(description="可选的JSON数据字典", default=None),
    timeout: int = Field(description="可选的请求超时时间（秒）", default=30),
    allow_redirects: bool = Field(description="可选的请求是否允许重定向", default=True),
) -> dict:
    """获取指定URL的响应内容详情.
    Returns:
        dict: 包含以下字段的响应数据字典
            - url (str): 最终响应URL（可能经过重定向）
            - headers (CaseInsensitiveDict): 响应头信息
            - status_code (int): HTTP状态码
            - text (str): 响应文本内容
            - cookies (dict): 响应cookies（字典格式）
            - content_type (str): 内容类型（取自Content-Type头部）
    """
    log.info(f"正在请求URL: {url}")
    response = requests.request(
        method=method,
        url=url,
        params=params,
        headers=headers,
        cookies=cookies,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    )
    log.info(f"响应状态码: {response.status_code}")
    return {
        "url": response.url,
        "headers": dict(response.headers),
        "status_code": response.status_code,
        "text": response.text,
        "cookies": dict(response.cookies),
        "content_type": response.headers.get("Content-Type"),
    }
