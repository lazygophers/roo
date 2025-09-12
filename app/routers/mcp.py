"""
MCP (Model Context Protocol) API 路由
提供 SSE 和 Streamable HTTP 端点
"""

from fastapi import APIRouter, Request, Response
from fastapi.responses import StreamingResponse
import json
from datetime import datetime
from typing import Any, Dict

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.mcp_tools_service import get_mcp_tools_service
from app.core.mcp_server import get_mcp_server

logger = setup_logging()

router = APIRouter(prefix="/mcp", tags=["MCP"])

@router.get("/tools")
async def list_mcp_tools():
    """列出可用的 MCP 工具"""
    try:
        # 从MCP工具服务获取真实的工具数据
        tools_service = get_mcp_tools_service()
        tools = tools_service.get_tools(enabled_only=False)  # 获取所有工具，包括禁用的
        
        return {
            "success": True,
            "message": "MCP tools retrieved successfully",
            "data": {
                "tools": tools,
                "server": "LazyAI Studio MCP Server",
                "organization": "LazyGophers"
            }
        }
    except Exception as e:
        logger.error(f"Failed to list MCP tools: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to list tools: Internal server error"
        }

@router.post("/call-tool")
async def call_mcp_tool(request: Dict[str, Any]):
    """调用 MCP 工具"""
    try:
        tool_name = request.get("name")
        arguments = request.get("arguments", {})
        
        if not tool_name:
            return {
                "success": False,
                "message": "Tool name is required"
            }
        
        # 检查工具是否存在
        available_tools = ["get_current_timestamp", "get_system_info", "list_available_modes"]
        if tool_name not in available_tools:
            return {
                "success": False,
                "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
            }
        
        # 直接实现工具函数
        if tool_name == "get_current_timestamp":
            import time
            from datetime import datetime
            now = datetime.now()
            unix_timestamp = int(time.time())
            result = f"""当前时间信息:
- ISO 格式: {now.isoformat()}
- Unix 时间戳: {unix_timestamp}
- 格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
- 时区: {now.astimezone().tzname()}"""
        elif tool_name == "get_system_info":
            import platform
            import psutil
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            result = f"""LazyAI Studio 系统信息:
- Python 版本: {platform.python_version()}
- 操作系统: {platform.system()} {platform.release()}
- CPU 使用率: {cpu_percent}%
- 内存使用: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
- 可用内存: {memory.available // 1024 // 1024}MB
- LazyGophers 出品 - 让 AI 替你思考！"""
        elif tool_name == "list_available_modes":
            result = """LazyAI Studio 可用模式:

🧠 orchestrator - Brain (智能中枢)
🏗️ architect - 顶尖架构师
📚 ask - 学术顾问
🪄 code - 代码魔法师
🐍 code-python - Python 代码魔法师
🔬 debug - 异常分析师
✍️ doc-writer - 文档工程师
⚙️ giter - 版本控制专家
🧠 memory - 记忆中枢
🔍 project-research - 项目研究员

🎯 快速选择建议:
- 需要架构设计 → architect
- 编写代码功能 → code 或 code-python
- 调试问题 → debug
- 分析项目 → project-research
- 任务规划 → orchestrator

LazyGophers - 让你做个聪明的懒人！ 🛋️"""
        else:
            result = f"Tool {tool_name} executed with arguments {arguments}"
        
        return {
            "success": True,
            "message": "Tool executed successfully",
            "data": {
                "tool": tool_name,
                "result": result,
                "arguments": arguments
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to call MCP tool: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Tool execution failed: Internal server error"
        }

@router.get("/status")
async def mcp_status():
    """MCP 服务器状态检查"""
    try:
        tools_service = get_mcp_tools_service()
        mcp_server = get_mcp_server()
        
        # 获取统计信息
        stats = tools_service.get_statistics()
        tools_by_category = tools_service.get_tools_by_category()
        
        return {
            "success": True,
            "message": "MCP server is running",
            "data": {
                "status": "healthy",
                "server_name": "LazyAI Studio MCP Server",
                "tools_count": stats['enabled_tools'],
                "total_tools": stats['total_tools'],
                "categories_count": stats['total_categories'],
                "tools_by_category": {cat_id: info['count'] for cat_id, info in stats['by_category'].items()},
                "endpoints": {
                    "sse": "/api/mcp/sse",
                    "streamable": "/api/mcp/streamable",
                    "tools": "/api/mcp/tools",
                    "call_tool": "/api/mcp/call-tool",
                    "categories": "/api/mcp/categories"
                },
                "organization": "LazyGophers",
                "motto": "让 AI 替你思考，让工具替你工作！",
                "last_updated": stats['last_updated']
            }
        }
    except Exception as e:
        logger.error(f"MCP status check failed: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Status check failed: Internal server error"
        }

@router.get("/categories")
async def list_mcp_categories():
    """列出 MCP 工具分类"""
    try:
        tools_service = get_mcp_tools_service()
        categories = tools_service.get_categories(enabled_only=False)  # 获取所有分类，包括禁用的
        tools_by_category = tools_service.get_tools_by_category()
        
        # 为每个分类添加工具数量
        for category in categories:
            cat_id = category['id']
            category['tools_count'] = tools_by_category.get(cat_id, {}).get('count', 0)
        
        return {
            "success": True,
            "message": "MCP categories retrieved successfully",
            "data": {
                "categories": categories,
                "total_categories": len(categories)
            }
        }
    except Exception as e:
        logger.error(f"Failed to list MCP categories: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to list categories: Internal server error"
        }

@router.get("/tools/{category}")
async def list_tools_by_category(category: str):
    """按分类列出 MCP 工具"""
    try:
        tools_service = get_mcp_tools_service()
        
        # 验证分类是否存在
        category_info = tools_service.get_category(category)
        if not category_info:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category)}' not found"
            }
        
        tools = tools_service.get_tools(category=category, enabled_only=True)
        
        return {
            "success": True,
            "message": f"Tools in category '{category}' retrieved successfully",
            "data": {
                "category": category_info,
                "tools": tools,
                "tools_count": len(tools)
            }
        }
    except Exception as e:
        logger.error(f"Failed to list tools for category '{sanitize_for_log(category)}': {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to list tools: Internal server error"
        }

@router.get("/tools/info/{tool_name}")
async def get_tool_info(tool_name: str):
    """获取特定工具的详细信息"""
    try:
        tools_service = get_mcp_tools_service()
        tool = tools_service.get_tool(tool_name)
        
        if not tool:
            return {
                "success": False,
                "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
            }
        
        return {
            "success": True,
            "message": "Tool information retrieved successfully",
            "data": {
                "tool": tool
            }
        }
    except Exception as e:
        logger.error(f"Failed to get tool info for '{sanitize_for_log(tool_name)}': {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get tool information: Internal server error"
        }

@router.post("/tools/refresh")
async def refresh_mcp_tools():
    """刷新 MCP 工具配置"""
    try:
        tools_service = get_mcp_tools_service()
        mcp_server = get_mcp_server()
        
        # 重新注册内置工具
        result = tools_service.register_builtin_tools()
        
        # 刷新MCP服务器工具
        mcp_result = mcp_server.refresh_tools()
        
        return {
            "success": True,
            "message": "MCP tools refreshed successfully",
            "data": {
                "tools_service_result": result,
                "mcp_server_result": mcp_result,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Failed to refresh MCP tools: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to refresh tools: Internal server error"
        }

# SSE 端点 - 集成到主应用中
# 注意: 这里我们不直接挂载 FastMCP 的 SSE，而是创建代理端点
@router.get("/sse")
async def mcp_sse_endpoint(request: Request):
    """MCP SSE 传输端点"""
    try:
        # 创建 SSE 响应头
        headers = {
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*"
        }
        
        async def sse_generator():
            """SSE 数据生成器"""
            try:
                # 发送初始连接事件
                yield f"event: connection\ndata: {json.dumps({'status': 'connected', 'server': 'LazyAI Studio MCP'})}\n\n"
                
                # 发送工具列表
                tools_data = [
                    {"name": "get_current_timestamp", "description": "获取当前时间戳"},
                    {"name": "get_system_info", "description": "获取 LazyAI Studio 系统信息"},
                    {"name": "list_available_modes", "description": "列出可用的 AI 模式"}
                ]
                
                yield f"event: tools\ndata: {json.dumps({'tools': tools_data})}\n\n"
                
                # 保持连接活跃
                while True:
                    import asyncio
                    await asyncio.sleep(30)  # 30秒心跳
                    yield f"event: heartbeat\ndata: {json.dumps({'timestamp': int(__import__('time').time())})}\n\n"
                    
            except Exception as e:
                logger.error(f"SSE generator error: {sanitize_for_log(str(e))}")
                yield f"event: error\ndata: {json.dumps({'error': 'Internal server error'})}\n\n"
        
        return StreamingResponse(sse_generator(), headers=headers)
        
    except Exception as e:
        logger.error(f"SSE endpoint error: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "SSE endpoint failed: Internal server error"
        }

@router.post("/streamable")  
async def mcp_streamable_endpoint(request: Dict[str, Any]):
    """MCP Streamable HTTP 传输端点"""
    try:
        # 处理 Streamable HTTP 请求
        method = request.get("method", "")
        params = request.get("params", {})
        
        logger.info(f"MCP Streamable HTTP request: method={sanitize_for_log(method)}")
        
        if method == "tools/list":
            # 返回工具列表
            tools = [
                {
                    "name": "get_current_timestamp",
                    "description": "获取当前时间戳",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "get_system_info", 
                    "description": "获取 LazyAI Studio 系统信息",
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                },
                {
                    "name": "list_available_modes",
                    "description": "列出可用的 AI 模式", 
                    "inputSchema": {"type": "object", "properties": {}, "required": []}
                }
            ]
            
            return {
                "jsonrpc": "2.0", 
                "id": request.get("id"),
                "result": {
                    "tools": tools
                }
            }
            
        elif method == "tools/call":
            # 调用工具
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            available_tools = ["get_current_timestamp", "get_system_info", "list_available_modes"]
            if tool_name not in available_tools:
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"), 
                    "error": {
                        "code": -1,
                        "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
                    }
                }
            
            # 直接调用工具函数
            if tool_name == "get_current_timestamp":
                import time
                from datetime import datetime
                now = datetime.now()
                unix_timestamp = int(time.time())
                result = f"""当前时间信息:
- ISO 格式: {now.isoformat()}
- Unix 时间戳: {unix_timestamp}
- 格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
- 时区: {now.astimezone().tzname()}"""
            else:
                result = f"Tool {tool_name} executed with arguments {arguments}"
            
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "content": [
                        {
                            "type": "text",
                            "text": str(result)
                        }
                    ]
                }
            }
            
        elif method == "initialize":
            # 初始化响应
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "serverInfo": {
                        "name": "LazyAI Studio MCP Server",
                        "version": "1.0.0"
                    }
                }
            }
            
        elif method == "ping":
            # Ping 响应
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {}
            }
            
        elif method == "notifications/initialized":
            # 初始化通知响应
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "result": {}
            }
            
        else:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -1,
                    "message": f"Method '{sanitize_for_log(method)}' not supported"
                }
            }
            
    except Exception as e:
        logger.error(f"Streamable HTTP endpoint error: {sanitize_for_log(str(e))}")
        return {
            "jsonrpc": "2.0",
            "id": request.get("id", None),
            "error": {
                "code": -1,
                "message": "Internal server error"
            }
        }

@router.post("/tools/enable")
async def enable_mcp_tool(request: Dict[str, Any]):
    """启用MCP工具"""
    try:
        tool_name = request.get("name")
        if not tool_name:
            return {
                "success": False,
                "message": "Tool name is required"
            }

        tools_service = get_mcp_tools_service()
        result = tools_service.enable_tool(tool_name)
        
        if result:
            return {
                "success": True,
                "message": f"Tool '{sanitize_for_log(tool_name)}' enabled successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
            }
    except Exception as e:
        logger.error(f"Failed to enable tool: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to enable tool: Internal server error"
        }

@router.post("/tools/disable")
async def disable_mcp_tool(request: Dict[str, Any]):
    """禁用MCP工具"""
    try:
        tool_name = request.get("name")
        if not tool_name:
            return {
                "success": False,
                "message": "Tool name is required"
            }

        tools_service = get_mcp_tools_service()
        result = tools_service.disable_tool(tool_name)
        
        if result:
            return {
                "success": True,
                "message": f"Tool '{sanitize_for_log(tool_name)}' disabled successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
            }
    except Exception as e:
        logger.error(f"Failed to disable tool: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to disable tool: Internal server error"
        }

@router.post("/tools/remove")
async def remove_mcp_tool(request: Dict[str, Any]):
    """从数据库中删除MCP工具"""
    try:
        tool_name = request.get("name")
        if not tool_name:
            return {
                "success": False,
                "message": "Tool name is required"
            }

        tools_service = get_mcp_tools_service()
        result = tools_service.remove_tool(tool_name)
        
        if result:
            return {
                "success": True,
                "message": f"Tool '{sanitize_for_log(tool_name)}' removed successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
            }
    except Exception as e:
        logger.error(f"Failed to remove tool: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to remove tool: Internal server error"
        }

@router.post("/categories/enable")
async def enable_mcp_category(request: Dict[str, Any]):
    """启用MCP工具分类"""
    try:
        category_id = request.get("id")
        if not category_id:
            return {
                "success": False,
                "message": "Category ID is required"
            }

        tools_service = get_mcp_tools_service()
        result = tools_service.enable_category(category_id)
        
        if result:
            return {
                "success": True,
                "message": f"Category '{sanitize_for_log(category_id)}' enabled successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_id)}' not found"
            }
    except Exception as e:
        logger.error(f"Failed to enable category: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to enable category: Internal server error"
        }

@router.post("/categories/disable")
async def disable_mcp_category(request: Dict[str, Any]):
    """禁用MCP工具分类"""
    try:
        category_id = request.get("id")
        if not category_id:
            return {
                "success": False,
                "message": "Category ID is required"
            }

        tools_service = get_mcp_tools_service()
        result = tools_service.disable_category(category_id)
        
        if result:
            return {
                "success": True,
                "message": f"Category '{sanitize_for_log(category_id)}' disabled successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_id)}' not found"
            }
    except Exception as e:
        logger.error(f"Failed to disable category: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to disable category: Internal server error"
        }

@router.post("/categories/create")
async def create_mcp_category(request: Dict[str, Any]):
    """创建新的MCP工具分类"""
    try:
        category_data = request
        if not category_data.get("id") or not category_data.get("name"):
            return {
                "success": False,
                "message": "Category ID and name are required"
            }

        tools_service = get_mcp_tools_service()
        result = tools_service.create_category(category_data)
        
        if result:
            return {
                "success": True,
                "message": f"Category '{sanitize_for_log(category_data['id'])}' created successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_data['id'])}' already exists"
            }
    except Exception as e:
        logger.error(f"Failed to create category: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to create category: Internal server error"
        }

@router.put("/categories/{category_id}")
async def update_mcp_category(category_id: str, request: Dict[str, Any]):
    """更新MCP工具分类"""
    try:
        update_data = request
        
        tools_service = get_mcp_tools_service()
        result = tools_service.update_category(category_id, update_data)
        
        if result:
            return {
                "success": True,
                "message": f"Category '{sanitize_for_log(category_id)}' updated successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_id)}' not found"
            }
    except Exception as e:
        logger.error(f"Failed to update category: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to update category: Internal server error"
        }

@router.delete("/categories/{category_id}")
async def delete_mcp_category(category_id: str):
    """删除MCP工具分类"""
    try:
        tools_service = get_mcp_tools_service()
        result = tools_service.delete_category(category_id)
        
        if result:
            return {
                "success": True,
                "message": f"Category '{sanitize_for_log(category_id)}' deleted successfully"
            }
        else:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_id)}' not found or has associated tools"
            }
    except Exception as e:
        logger.error(f"Failed to delete category: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to delete category: Internal server error"
        }