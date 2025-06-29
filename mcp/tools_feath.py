from croe import mcp
import requests
from requests.exceptions import RequestException


@mcp.tool()
async def fetch_markdown(
    url: str, params=None,
    method: str = "GET",
    headers: dict = None, cookies: dict = None,
    data=None, json=None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> str:
    """获取指定URL的Markdown内容.

    Args:
        url (str): 请求的目标URL
        params (dict, optional): 请求查询参数字典
        method (str, optional): HTTP方法（GET/POST等），默认GET
        headers (dict, optional): 请求头字典
        cookies (dict, optional): cookies字典
        data (any, optional): 请求体数据（表单数据）
        json (any, optional): JSON请求体数据
        timeout (int, optional): 请求超时时间（秒），默认30秒
        allow_redirects (bool, optional): 是否允许重定向，默认True

    Returns:
        str: 响应内容字符串

    Raises:
        RequestException: 网络请求相关异常
    """
    return requests.request(
        params=params,
        method=method,
        headers=headers,
        cookies=cookies,
        url=url,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    ).text


@mcp.tool()
async def fetch_rss(
    url: str, params=None,
    method: str = "GET",
    headers: dict = None, cookies: dict = None,
    data=None, json=None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> str:
    """获取指定URL的RSS内容.

    Args:
        url (str): 请求的目标URL
        params (dict, optional): 请求查询参数字典
        method (str, optional): HTTP方法（GET/POST等），默认GET
        headers (dict, optional): 请求头字典
        cookies (dict, optional): cookies字典
        data (any, optional): 请求体数据（表单数据）
        json (any, optional): JSON请求体数据
        timeout (int, optional): 请求超时时间（秒），默认30秒
        allow_redirects (bool, optional): 是否允许重定向，默认True

    Returns:
        str: 响应内容字符串

    Raises:
        RequestException: 网络请求相关异常
    """
    return requests.request(
        params=params,
        method=method,
        headers=headers,
        cookies=cookies,
        url=url,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    ).text


@mcp.tool()
async def fetch_html(
    url: str, params=None,
    method: str = "GET",
    headers: dict = None, cookies: dict = None,
    data=None, json=None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> str:
    """获取指定URL的HTML内容.

    Args:
        url (str): 请求的目标URL
        params (dict, optional): 请求查询参数字典
        method (str, optional): HTTP方法（GET/POST等），默认GET
        headers (dict, optional): 请求头字典
        cookies (dict, optional): cookies字典
        data (any, optional): 请求体数据（表单数据）
        json (any, optional): JSON请求体数据
        timeout (int, optional): 请求超时时间（秒），默认30秒
        allow_redirects (bool, optional): 是否允许重定向，默认True

    Returns:
        str: 响应内容字符串

    Raises:
        RequestException: 网络请求相关异常
    """
    return requests.request(
        params=params,
        method=method,
        headers=headers,
        cookies=cookies,
        url=url,
        data=data,
        json=json,
        timeout=timeout,
        allow_redirects=allow_redirects,
    ).text


@mcp.tool()
async def fetch_json(
    url: str, params=None,
    method: str = "GET",
    headers: dict = None, cookies: dict = None,
    data=None, json=None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> dict:
    """获取指定URL的JSON内容.

    Args:
        url (str): 请求的目标URL
        params (dict, optional): 请求查询参数字典
        method (str, optional): HTTP方法（GET/POST等），默认GET
        headers (dict, optional): 请求头字典
        cookies (dict, optional): cookies字典
        data (any, optional): 请求体数据（表单数据）
        json (any, optional): JSON请求体数据
        timeout (int, optional): 请求超时时间（秒），默认30秒
        allow_redirects (bool, optional): 是否允许重定向，默认True

    Returns:
        dict: 解析后的JSON响应数据

    Raises:
        RequestException: 网络请求相关异常
        ValueError: JSON解析失败时触发
    """
    return requests.request(
        params=params,
        method=method,
        headers=headers,
        cookies=cookies,
        url=url,
        data=data,
        json=json,
    ).json()