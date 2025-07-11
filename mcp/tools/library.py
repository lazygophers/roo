import os
from pydantic import Field

from core.cache import Cache
from core.croe import mcp
from tools.feath import fetch
from tools.file import read_file

document_prefix = "library/document/"

cache = Cache(
    os.path.join("cache", "library", "cache")
)  # 初始化缓存实例，用于存储仓库更新时间等信息

library_map = {
    # golang
    "golang/风格指南": "file://library/document/golang/guide.md",
    ## google
    "golang/google/best-practices": "https://cdn.jsdelivr.net/gh/google/styleguide@master/go/best-practices.md",
    "golang/google/decisions": "https://cdn.jsdelivr.net/gh/google/styleguide@master/go/decisions.md",
    "golang/google/guide": "https://cdn.jsdelivr.net/gh/google/styleguide@master/go/guide.md",
    "golang/google/index": "https://cdn.jsdelivr.net/gh/google/styleguide@master/go/index.md",
    ## uber
    "golang/uber/guide": "https://cdn.jsdelivr.net/gh/uber-go/guide@master/style.md",
    # python
    "python/风格指南": "file://library/document/python/guide.md",
    ## google
    "python/google/guide": "https://cdn.jsdelivr.net/gh/google/styleguide@master/pyguide.md",
    "python/google/lintrc": "https://cdn.jsdelivr.net/gh/google/styleguide@gh-pages/pylintrc",
    # markdown
    "markdown/风格指南": "file://library/document/markdown/guide.md",
}


async def fetch_with_cache(url: str = Field(description="URL")) -> str:
    value = cache.get(url)
    if value is not None:
        return value

    if url.startswith("https://"):
        value = await fetch(url, timeout=60)
        cache.set(url, value, ttl=86400)
    elif url.startswith("file://"):
        value = await read_file(url[7:])

    raise value


@mcp.tool()
async def library_list() -> list[str]:
    """
    根据 library 类型获取 library_id 列表
    Returns:
        list: 包含所有支持的 library_id
    """

    return list(library_map.keys())


@mcp.tool()
async def library_get(
    library_id: str = Field(
        description="库标识，可通过 library_list 获取",
        examples=list(library_map.keys()),
    ),
) -> str:
    """
    获取库的最新文档、源码
    Returns:
        library 内容
    """

    if library_id not in library_map:
        raise ValueError(f"Invalid library_id: {library_id}")

    return await fetch_with_cache(library_map[library_id])