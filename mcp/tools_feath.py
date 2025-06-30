from config import proxies
from croe import mcp
import requests


@mcp.tool()
async def fetch_markdown(
    url: str,
    params=None,
    method: str = "GET",
    headers: dict = None,
    cookies: dict = None,
    data=None,
    json=None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> str:
    """获取指定URL的Markdown文本内容.

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
        str: 响应的Markdown文本内容

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
    url: str,
    params=None,
    method: str = "GET",
    headers: dict = None,
    cookies: dict = None,
    data: str | bytes | list | tuple | dict | object = None,
    json: dict = None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> str:
    """获取指定URL的RSS订阅内容.

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
        str: RSS订阅内容的原始字符串

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
    url: str,
    params=None,
    method: str = "GET",
    headers: dict = None,
    cookies: dict = None,
    data: str | bytes | list | tuple | dict | object = None,
    json: dict = None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> str:
    """获取指定URL的HTML页面内容.

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
        str: HTML页面的原始文本内容

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
    url: str,
    params=None,
    method: str = "GET",
    headers: dict = None,
    cookies: dict = None,
    data: str | bytes | list | tuple | dict | object = None,
    json: dict = None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> dict:
    """获取并解析指定URL的JSON响应.

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
        dict: 解析后的JSON数据对象

    Raises:
        RequestException: 网络请求相关异常
        ValueError: JSON解析失败时抛出
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
    ).json()


@mcp.tool()
async def fetch(
    url: str,
    params=None,
    method: str = "GET",
    headers: dict = None,
    cookies: dict = None,
    data: str | bytes | list | tuple | dict | object = None,
    json: dict = None,
    timeout: int = 30,
    allow_redirects: bool = True,
) -> dict:
    """获取指定URL的响应内容详情.

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
        dict: 包含以下字段的响应数据字典
            - url (str): 最终响应URL（可能经过重定向）
            - headers (CaseInsensitiveDict): 响应头信息
            - status_code (int): HTTP状态码
            - text (str): 响应文本内容
            - cookies (dict): 响应cookies（字典格式）
            - content_type (str): 内容类型（取自Content-Type头部）

    Raises:
        RequestException: 网络请求相关异常
    """
    response = requests.request(
        params=params,
        method=method,
        headers=headers,
        cookies=cookies,
        url=url,
        data=data,
        json=json,
        timeout=timeout,
        proxies=proxies,
        allow_redirects=allow_redirects,
    )
    return {
        "url": response.url,
        "headers": dict(response.headers),
        "status_code": response.status_code,
        "text": response.text,
        "cookies": dict(response.cookies),
        "content_type": response.headers.get("Content-Type"),
    }
