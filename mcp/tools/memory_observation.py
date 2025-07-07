from pydantic import Field

from core.croe import mcp
from tools.memory import Observation, manager


@mcp.tool()
async def memory_create_observations(
    namespace: str, observations: list[Observation] = Field(description="观察列表")
):
    """
    在知识图谱中创建多个新的观察
    """
    manager.add_observations(namespace, observations)


@mcp.tool()
async def memory_delete_observations(
    namespace: str, observations: list[Observation] = Field(description="观察列表")
):
    """
    在知识图谱中删除多个观察
    """
    manager.delete_observations(namespace, observations)