import os
from pydantic import Field
from cache import Cache
from croe import mcp

cache = Cache(os.path.join("cache", "cache"))


@mcp.tool()
async def cache_get(
    key: str = Field(
        description="缓存键，注意需要带上项目标识",
        examples=[
            "codegen:cache1",
            "codegen:cache2",
            "codegen:cache3",
            "codegen:cache4",
            "github.com/lazygophers/utils:cache1",
            "github.com/lazygophers/utils:cache2",
        ],
    )
) -> object:
    """
    获取指定键的缓存值
    Returns:
        object: 缓存值对象，若不存在则返回None
    """
    return cache.get(key)


@mcp.tool()
async def cache_set(
    key: str = Field(
        description="缓存键，注意需要带上项目标识",
        examples=[
            "codegen:cache1",
            "codegen:cache2",
            "codegen:cache3",
            "codegen:cache4",
            "github.com/lazygophers/utils:cache1",
            "github.com/lazygophers/utils:cache2",
        ],
    ),
    value: object = Field(description="缓存值"),
    ttl: int = Field(
        description="缓存有效期（秒），0表示永久有效",
        examples=[0, 60, 3600, 86400, 604800, 2592000],
        default=0,
    ),
) -> bool:
    """
    设置指定键的缓存值
    Returns:
        bool: 缓存设置是否成功
    """
    cache.set(key, value, ttl)
    return True


@mcp.tool()
async def cache_delete(
    key: str = Field(
        description="缓存键",
        examples=[
            "codegen:cache1",
            "codegen:cache2",
            "codegen:cache3",
            "codegen:cache4",
            "github.com/lazygophers/utils:cache1",
            "github.com/lazygophers/utils:cache2",
        ],
    )
) -> bool:
    """
    删除指定键的缓存
    Returns:
        bool: 缓存删除是否成功
    """
    cache.delete(key)
    return True


@mcp.tool()
async def cache_exists(
    key: str = Field(
        description="缓存键，注意需要带上项目标识",
        examples=[
            "codegen:cache1",
            "codegen:cache2",
            "codegen:cache3",
            "codegen:cache4",
            "github.com/lazygophers/utils:cache1",
            "github.com/lazygophers/utils:cache2",
        ],
    ),
) -> bool:
    """
    检查指定键是否存在缓存
    Returns:
        bool: 缓存是否存在
    """
    return cache.exists(key)