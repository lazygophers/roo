"""
系统工具集
使用装饰器自动注册系统相关的MCP工具
"""
from app.core.mcp_tool_registry import system_tool


@system_tool(
    name="get_info",
    description="获取LazyAI Studio系统信息，包括CPU、内存、操作系统等",
    schema={
        "type": "object",
        "properties": {
            "detailed": {
                "type": "boolean",
                "description": "是否返回详细信息",
                "default": True
            },
            "include_performance": {
                "type": "boolean",
                "description": "是否包含性能指标",
                "default": False
            }
        },
        "required": []
    },
    metadata={
        "tags": ["系统", "监控", "性能", "LazyGophers"],
        "examples": [
            {"detailed": False},
            {"detailed": True, "include_performance": True}
        ]
    }
)
def get_info():
    """获取LazyAI Studio系统信息，包括CPU、内存、操作系统等"""
    pass