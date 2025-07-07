from pydantic import Field

from core.croe import mcp
from tools.memory import Relation, manager


@mcp.tool()
async def memory_create_relations(
    namespace: str, relations: list[Relation] = Field(description="关系列表")
):
    """
    在知识图谱中创建多个新的关系
    """
    manager.add_relations(namespace, relations)


@mcp.tool()
async def memory_delete_relations(
    namespace: str, relations: list[Relation] = Field(description="关系列表")
):
    """
    在知识图谱中删除多个关系
    """
    manager.delete_relations(namespace, relations)