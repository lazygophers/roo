from pydantic import Field

from core.croe import mcp
from tools.memory import Entity, manager


@mcp.tool()
async def memory_create_entities(
    namespace: str, entities: list[Entity] = Field(description="实体列表")
):
    """
    在知识图谱中创建多个新的实体
    """
    manager.add_entities(namespace, entities)


@mcp.tool()
async def memory_delete_entities(
    namespace: str, entities_names: list[str] = Field(description="实体名称列表")
):
    """
    在知识图谱中删除多个实体
    """
    manager.delete_entities(namespace, entities_names)