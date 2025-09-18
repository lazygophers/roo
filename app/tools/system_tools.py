"""
系统工具集
使用装饰器自动注册系统相关的MCP工具
"""
from app.core.mcp_tool_registry import system_tool


@system_tool(
    name="get_info",
    description="Get LazyAI Studio system information including CPU, memory, OS, etc.",
    schema={
        "type": "object",
        "properties": {
            "detailed": {
                "type": "boolean",
                "description": "Return detailed information",
                "default": True
            },
            "include_performance": {
                "type": "boolean",
                "description": "Include performance metrics",
                "default": False
            }
        },
        "required": []
    },
    metadata={
        "tags": ["system", "monitoring", "performance", "LazyGophers"],
        "examples": [
            {"detailed": False},
            {"detailed": True, "include_performance": True}
        ]
    }
)
def get_info():
    """Get LazyAI Studio system information including CPU, memory, OS, etc."""
    pass