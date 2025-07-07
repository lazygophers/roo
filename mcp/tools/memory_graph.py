from pydantic import Field

from core.croe import mcp
from tools.memory import manager


@mcp.tool()
async def memory_read_graph(namespace: str = Field(description="命名空间")) -> dict:
    """
    读取整个知识图谱
    """
    return manager.get_graph(namespace)


@mcp.tool()
async def memory_search_nodes(
    namespace: str = Field(description="命名空间"),
    query: str = Field(description="查询条件"),
):
    """
    搜索知识图谱中的节点
    """
    graph = manager.get_graph(namespace)

    # 过滤 query 字段和 name 字段不相等或 不是 name 字段的子字符串
    graph["entities"] = [
        entity for entity in graph["entities"] if query in entity["name"]
    ]

    # 过滤 query 字段和 from_entity 或 to_entity 字段不相等或 不是 from_entity 或 to_entity 字段的子字符串
    graph["relations"] = [
        relation
        for relation in graph["relations"]
        if query in relation["from_entity"] or query in relation["to_entity"]
    ]

    return graph


@mcp.tool()
async def memory_open_nodes(
    namespace: str = Field(description="命名空间"),
    entity_names: list[str] = Field(description="实体名称"),
):
    """
    打开知识图谱中的节点
    """

    graph = manager.get_graph(namespace)

    # 过滤 name 字段未出现在 entity_names 中的实体
    graph["entities"] = [
        entity for entity in graph["entities"] if entity["name"] in entity_names
    ]

    # 过滤 from_entity 或 to_entity 字段均未出现在 entity_names 中的实体
    graph["relations"] = [
        relation
        for relation in graph["relations"]
        if relation["from_entity"] in entity_names
        or relation["to_entity"] in entity_names
    ]

    return graph