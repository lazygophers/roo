import os

from croe import mcp
from tools_file import list_files, read_file


document_prefix = "library/document/"


@mcp.tool()
async def library_list() -> list[str]:
    """
    根据 library 类型获取 library_id 列表

    Args:

    Returns:
        list: 包含所有支持的 library_id
    """

    return [
        (
            file_name[len(document_prefix) :]
            if file_name.startswith(document_prefix)
            else file_name
        )
        for file_name in await list_files(document_prefix, True)
    ]


@mcp.tool()
async def library_get(library_id: str) -> str:
    """
    获取库的最新文档、源码

    Args:
        library_id: libray标识

    Returns:
        library 内容
    """

    return await read_file(os.path.join(document_prefix, library_id))
