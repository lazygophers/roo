from pydantic import Field

from core.croe import mcp


@mcp.tool()
async def memory_read_graph(namespace: str = Field(description="命名空间")):
    """
    读取整个知识图谱
    """

@mcp.tool()
async def memory_search_nodes(
        namespace: str = Field(description="命名空间"),
        query: str = Field(description="查询条件"),
):
    """
    搜索知识图谱中的节点
    """

@mcp.tool()
async def memory_open_nodes(
        namespace: str = Field(description="命名空间"),
        entity_names: list[str] = Field(description="实体名称"),
):
    """
    打开知识图谱中的节点
    """