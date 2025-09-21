"""
MCP (Model Context Protocol) API 路由
提供 SSE 和 Streamable HTTP 端点
"""

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field, field_validator
import json
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.tools.service import get_mcp_tools_service
from app.tools.server import get_mcp_server
from app.core.mcp_tools_service import get_mcp_config_service
from app.core.mcp_permissions import check_tool_permission, get_permission_manager, refresh_permission_manager

# 导入权限装饰器
def require_edit_permission(func):
    """装饰器：要求编辑权限"""
    import functools
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        config_service = get_mcp_config_service()
        if not config_service.is_tool_edit_allowed():
            raise HTTPException(
                status_code=401,
                detail="在远程环境中，MCP工具编辑被禁用。请在本地环境中使用此功能。"
            )
        return await func(*args, **kwargs)
    return wrapper

logger = setup_logging()

router = APIRouter(prefix="/mcp", tags=["MCP"])

# Pydantic 模型定义用于输入验证
class MCPToolCallRequest(BaseModel):
    """MCP 工具调用请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="工具名称")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="工具参数")

    @field_validator('name')
    @classmethod
    def validate_tool_name(cls, v):
        # 只允许字母数字、下划线和连字符
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('工具名称只能包含字母、数字、下划线和连字符')
        return v

    @field_validator('arguments')
    @classmethod
    def validate_arguments(cls, v):
        # 限制参数字典的大小以防止DoS攻击
        if len(str(v)) > 10000:  # 限制序列化后的大小
            raise ValueError('工具参数过大，序列化后不能超过10000字符')

        # 检查参数数量
        if isinstance(v, dict) and len(v) > 50:
            raise ValueError('工具参数数量不能超过50个')

        # 检查嵌套深度
        def check_depth(obj, depth=0):
            if depth > 10:  # 限制嵌套深度
                raise ValueError('工具参数嵌套深度不能超过10层')
            if isinstance(obj, dict):
                for value in obj.values():
                    check_depth(value, depth + 1)
            elif isinstance(obj, list):
                for item in obj:
                    check_depth(item, depth + 1)

        check_depth(v)
        return v

@router.get("/tools")
async def list_mcp_tools():
    """列出可用的 MCP 工具"""
    try:
        # 从MCP工具服务获取真实的工具数据
        tools_service = get_mcp_tools_service()
        all_tools = tools_service.get_tools(enabled_only=False)  # 获取所有工具，包括禁用的

        # 根据权限过滤工具
        permission_manager = get_permission_manager()
        allowed_tools = []
        blocked_tools = []

        for tool in all_tools:
            if check_tool_permission(tool['name']):
                allowed_tools.append(tool)
            else:
                blocked_tools.append({
                    "name": tool['name'],
                    "description": tool['description'],
                    "category": tool['category'],
                    "permission_level": permission_manager.get_permission_level(tool['name']),
                    "blocked_reason": f"需要 {permission_manager.get_permission_level(tool['name'])} 权限，在 {permission_manager.environment} 环境下不可用"
                })

        return {
            "success": True,
            "message": "MCP tools retrieved successfully",
            "data": {
                "tools": allowed_tools,
                "blocked_tools": blocked_tools,
                "environment": permission_manager.environment,
                "permission_info": permission_manager.get_permission_info(),
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
async def call_mcp_tool(request: MCPToolCallRequest):
    """调用 MCP 工具"""
    try:
        # 检查环境权限
        config_service = get_mcp_config_service()
        if not config_service.is_tool_call_allowed():
            return {
                "success": False,
                "message": "在远程环境中，MCP工具调用被禁用。请在本地环境中使用此功能。"
            }

        tool_name = request.name
        arguments = request.arguments

        # 输入验证已通过 Pydantic 模型完成

        # 权限检查：检查工具是否允许在当前环境下使用
        if not check_tool_permission(tool_name):
            permission_manager = get_permission_manager()
            permission_level = permission_manager.get_permission_level(tool_name)
            return {
                "success": False,
                "message": f"工具 '{sanitize_for_log(tool_name)}' 在 {permission_manager.environment} 环境下不可用。此工具需要 {permission_level} 权限，仅在本地环境中可用。",
                "error_code": "TOOL_PERMISSION_DENIED",
                "data": {
                    "tool_name": tool_name,
                    "environment": permission_manager.environment,
                    "permission_level": permission_level,
                    "allowed": False
                }
            }
        
        # 获取MCP服务器实例并调用工具
        try:
            from app.tools.server import get_mcp_server
            mcp_server = get_mcp_server()
            
            # 检查工具是否存在
            available_tools = mcp_server.get_available_tools()
            if tool_name not in [tool['name'] for tool in available_tools]:
                return {
                    "success": False,
                    "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
                }
            
            # 调用MCP工具
            result = await mcp_server.call_tool(tool_name, arguments)
            
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
            logger.error(f"Error calling MCP tool {tool_name}: {sanitize_for_log(str(e))}")
            return {
                "success": False,
                "message": f"Tool execution failed: {str(e)}"
            }
        
        # Legacy fallback implementation (should not be reached with new MCP server)
        if tool_name == "get_current_timestamp":
            import time
            from datetime import datetime
            from app.core.time_tools_service import get_time_tools_service
            
            try:
                # 从参数获取格式设置
                format_type = arguments.get('format', 'iso')
                
                # 获取时间工具配置服务
                time_service = get_time_tools_service()
                
                # 获取配置的时区
                tz_obj = time_service.get_timezone_object()
                show_tz_info = time_service.should_display_timezone_info()
                default_tz_str = time_service.get_default_timezone()
                
                # 生成时间
                if tz_obj:
                    now = datetime.now(tz_obj)
                    tz_name = str(tz_obj)
                else:
                    now = datetime.now()
                    tz_name = str(now.astimezone().tzinfo)
                
                unix_timestamp = int(now.timestamp())
                
                if format_type == 'unix':
                    result = f"Unix时间戳: {unix_timestamp}"
                elif format_type == 'formatted':
                    if show_tz_info:
                        result = f"格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')} ({tz_name})"
                    else:
                        result = f"格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                else:  # iso
                    result = f"ISO格式时间: {now.isoformat()}"
                
                # 完整信息总是包含
                result += f"""

完整时间信息:
- ISO 格式: {now.isoformat()}
- Unix 时间戳: {unix_timestamp}
- 格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"""
                if show_tz_info:
                    result += f"\n- 配置时区: {default_tz_str}"
                    result += f"\n- 实际时区: {tz_name}"
                
            except Exception as e:
                logger.error(f"Error in get_current_timestamp API: {sanitize_for_log(str(e))}")
                # 回退实现
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

@router.get("/environment")
async def get_environment_info():
    """获取环境信息"""
    try:
        config_service = get_mcp_config_service()
        environment_type = config_service.get_environment_type()

        return {
            "success": True,
            "message": "Environment information retrieved successfully",
            "data": {
                "environment": environment_type,
                "is_local": environment_type == "local",
                "is_remote": environment_type == "remote",
                "tool_call_allowed": config_service.is_tool_call_allowed(),
                "tool_edit_allowed": config_service.is_tool_edit_allowed()
            }
        }
    except Exception as e:
        logger.error(f"Failed to get environment info: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get environment information: Internal server error"
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
        # 输入验证：只允许安全的分类名称
        import re
        if not re.match(r'^[a-zA-Z0-9_-]+$', category) or len(category) > 50:
            raise HTTPException(
                status_code=400,
                detail="无效的分类名称：只能包含字母、数字、下划线和连字符，长度不超过50字符"
            )

        tools_service = get_mcp_tools_service()

        # 验证分类是否存在
        category_info = tools_service.get_category(category)
        if not category_info:
            raise HTTPException(
                status_code=404,
                detail=f"分类 '{sanitize_for_log(category)}' 未找到"
            )
        
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

@router.post("/tools/sync")
async def sync_mcp_tools():
    """同步 MCP 工具数据库：自动添加新工具，移除不存在的工具"""
    try:
        tools_service = get_mcp_tools_service()

        # 同步工具数据库
        result = tools_service.sync_tools_database()

        if 'error' in result:
            return {
                "success": False,
                "message": f"Failed to sync tools database: {result['error']}",
                "data": result
            }

        return {
            "success": True,
            "message": "MCP tools database synced successfully",
            "data": {
                "sync_result": result,
                "timestamp": datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Failed to sync MCP tools database: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to sync tools database: Internal server error"
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

            # 权限检查：检查工具是否允许在当前环境下使用
            if not check_tool_permission(tool_name):
                permission_manager = get_permission_manager()
                permission_level = permission_manager.get_permission_level(tool_name)
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -2,
                        "message": f"工具 '{sanitize_for_log(tool_name)}' 在 {permission_manager.environment} 环境下不可用。此工具需要 {permission_level} 权限，仅在本地环境中可用。",
                        "data": {
                            "tool_name": tool_name,
                            "environment": permission_manager.environment,
                            "permission_level": permission_level,
                            "allowed": False,
                            "error_code": "TOOL_PERMISSION_DENIED"
                        }
                    }
                }

            # 获取MCP服务器实例并调用工具
            try:
                from app.tools.server import get_mcp_server
                mcp_server = get_mcp_server()
                
                # 检查工具是否存在
                available_tools = mcp_server.get_available_tools()
                if tool_name not in [tool['name'] for tool in available_tools]:
                    return {
                        "jsonrpc": "2.0",
                        "id": request.get("id"), 
                        "error": {
                            "code": -1,
                            "message": f"Tool '{sanitize_for_log(tool_name)}' not found"
                        }
                    }
                
                # 调用MCP工具
                result = await mcp_server.call_tool(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": result
                            }
                        ]
                    }
                }
                
            except Exception as e:
                logger.error(f"Error in streamable MCP tool call: {sanitize_for_log(str(e))}")
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "error": {
                        "code": -1,
                        "message": f"Tool execution failed: {str(e)}"
                    }
                }
            
            # Legacy fallback implementation
            if tool_name == "get_current_timestamp":
                import time
                from datetime import datetime
                from app.core.time_tools_service import get_time_tools_service
                
                try:
                    # 从参数获取格式设置
                    format_type = arguments.get('format', 'iso')
                    
                    # 获取时间工具配置服务
                    time_service = get_time_tools_service()
                    
                    # 获取配置的时区
                    tz_obj = time_service.get_timezone_object()
                    show_tz_info = time_service.should_display_timezone_info()
                    default_tz_str = time_service.get_default_timezone()
                    
                    # 生成时间
                    if tz_obj:
                        now = datetime.now(tz_obj)
                        tz_name = str(tz_obj)
                    else:
                        now = datetime.now()
                        tz_name = str(now.astimezone().tzinfo)
                    
                    unix_timestamp = int(now.timestamp())
                    
                    if format_type == 'unix':
                        result = f"Unix时间戳: {unix_timestamp}"
                    elif format_type == 'formatted':
                        if show_tz_info:
                            result = f"格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')} ({tz_name})"
                        else:
                            result = f"格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
                    else:  # iso
                        result = f"ISO格式时间: {now.isoformat()}"
                    
                    # 完整信息总是包含
                    result += f"""

完整时间信息:
- ISO 格式: {now.isoformat()}
- Unix 时间戳: {unix_timestamp}
- 格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"""
                    if show_tz_info:
                        result += f"\n- 配置时区: {default_tz_str}"
                        result += f"\n- 实际时区: {tz_name}"
                        
                except Exception as e:
                    logger.error(f"Error in get_current_timestamp streamable: {sanitize_for_log(str(e))}")
                    # 回退实现
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
@require_edit_permission
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
@require_edit_permission
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
@require_edit_permission
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
@require_edit_permission
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
@require_edit_permission
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

@router.get("/categories/{category_id}/config")
async def get_category_config(category_id: str):
    """获取MCP工具分类的配置"""
    try:
        tools_service = get_mcp_tools_service()
        config = tools_service.get_category_config(category_id)
        
        if config is None:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_id)}' not found"
            }
        
        return {
            "success": True,
            "message": "Category configuration retrieved successfully",
            "data": {
                "category_id": category_id,
                "config": config
            }
        }
    except Exception as e:
        logger.error(f"Failed to get category config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get category configuration: Internal server error"
        }

@router.put("/categories/{category_id}/config")
@require_edit_permission
async def update_category_config(category_id: str, request: Dict[str, Any]):
    """更新MCP工具分类的配置"""
    try:
        config_data = request.get("config", {})
        if not config_data:
            return {
                "success": False,
                "message": "Configuration data is required"
            }
        
        tools_service = get_mcp_tools_service()
        result = tools_service.update_category_configs(category_id, config_data)
        
        if result:
            return {
                "success": True,
                "message": f"Category '{sanitize_for_log(category_id)}' configuration updated successfully",
                "data": {
                    "category_id": category_id,
                    "updated_config": config_data,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_id)}' not found or update failed"
            }
    except Exception as e:
        logger.error(f"Failed to update category config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to update category configuration: Internal server error"
        }

@router.put("/categories/{category_id}/config/{config_key}")
@require_edit_permission
async def update_category_config_item(category_id: str, config_key: str, request: Dict[str, Any]):
    """更新MCP工具分类配置的单个项目"""
    try:
        config_value = request.get("value")
        if config_value is None:
            return {
                "success": False,
                "message": "Configuration value is required"
            }

        tools_service = get_mcp_tools_service()
        result = tools_service.update_category_config(category_id, config_key, config_value)

        if result:
            return {
                "success": True,
                "message": f"Category '{sanitize_for_log(category_id)}' configuration '{sanitize_for_log(config_key)}' updated successfully",
                "data": {
                    "category_id": category_id,
                    "config_key": config_key,
                    "config_value": config_value,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": f"Category '{sanitize_for_log(category_id)}' not found or update failed"
            }
    except Exception as e:
        logger.error(f"Failed to update category config item: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to update category configuration item: Internal server error"
        }

@router.get("/permissions")
async def get_mcp_permissions():
    """获取MCP工具权限信息"""
    try:
        permission_manager = get_permission_manager()

        return {
            "success": True,
            "message": "MCP permissions retrieved successfully",
            "data": {
                "environment": permission_manager.environment,
                "permission_info": permission_manager.get_permission_info(),
                "allowed_tools": permission_manager.get_allowed_tools(),
                "blocked_tools": permission_manager.get_blocked_tools(),
                "restrictions_active": permission_manager.environment != "local"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get MCP permissions: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get MCP permissions: Internal server error"
        }

class RefreshPermissionsRequest(BaseModel):
    """刷新权限请求模型"""
    environment: Optional[str] = Field(None, description="环境类型 (local/remote)")

@router.post("/permissions/refresh")
async def refresh_mcp_permissions(request: RefreshPermissionsRequest = None):
    """刷新MCP工具权限管理器（重新读取环境变量）"""
    try:
        environment = request.environment if request else None
        permission_manager = refresh_permission_manager(environment)

        return {
            "success": True,
            "message": "MCP permissions refreshed successfully",
            "data": {
                "environment": permission_manager.environment,
                "permission_info": permission_manager.get_permission_info(),
                "allowed_tools": permission_manager.get_allowed_tools(),
                "blocked_tools": permission_manager.get_blocked_tools(),
                "restrictions_active": permission_manager.environment != "local"
            }
        }
    except Exception as e:
        logger.error(f"Failed to refresh MCP permissions: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to refresh MCP permissions: Internal server error"
        }

@router.get("/categories/github/token-status")
async def check_github_token_status():
    """检查GitHub Token状态"""
    try:
        tools_service = get_mcp_tools_service()

        # 获取GitHub分类配置
        github_config = tools_service.get_category_config('github')

        if not github_config:
            return {
                "success": True,
                "message": "GitHub token status checked",
                "data": {
                    "valid": False,
                    "reason": "GitHub工具未配置"
                }
            }

        # 检查token是否存在
        github_token = github_config.get('github_token', '').strip()

        if not github_token:
            return {
                "success": True,
                "message": "GitHub token status checked",
                "data": {
                    "valid": False,
                    "reason": "GitHub Token为空，请在工具配置中设置GitHub Token"
                }
            }

        # 简单验证token格式
        if not github_token.startswith(('ghp_', 'github_pat_')) or len(github_token) < 20:
            return {
                "success": True,
                "message": "GitHub token status checked",
                "data": {
                    "valid": False,
                    "reason": "GitHub Token格式无效，请检查token格式"
                }
            }

        return {
            "success": True,
            "message": "GitHub token status checked",
            "data": {
                "valid": True,
                "reason": "GitHub Token已配置"
            }
        }

    except Exception as e:
        logger.error(f"Failed to check GitHub token status: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "检查GitHub Token状态失败",
            "data": {
                "valid": False,
                "reason": "系统错误，请稍后重试"
            }
        }

# File-based GitHub Configuration Endpoints
@router.get("/tools/github/config")
async def get_github_file_config():
    """获取GitHub工具的文件配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()
        config = config_service.get_config("github")
        file_info = config_service.get_config_file_info("github")

        return {
            "success": True,
            "message": "GitHub configuration retrieved successfully",
            "data": {
                "config": config,
                "file_info": file_info,
                "storage_type": "file"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get GitHub file config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get GitHub configuration: Internal server error"
        }

@router.put("/tools/github/config")
@require_edit_permission
async def update_github_file_config(request: Dict[str, Any]):
    """更新GitHub工具的文件配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_data = request.get("config", {})
        if not config_data:
            return {
                "success": False,
                "message": "Configuration data is required"
            }

        config_service = get_tool_config_service()

        # 备份当前配置
        backup_file = config_service.backup_config("github")

        # 更新配置
        success = config_service.set_config("github", config_data)

        if success:
            return {
                "success": True,
                "message": "GitHub configuration updated successfully",
                "data": {
                    "updated_config": config_data,
                    "backup_file": backup_file,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to update GitHub configuration"
            }

    except Exception as e:
        logger.error(f"Failed to update GitHub file config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to update GitHub configuration: Internal server error"
        }

@router.post("/tools/github/config/migrate")
@require_edit_permission
async def migrate_github_config_to_file():
    """将GitHub配置从数据库迁移到文件"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        # 获取当前数据库配置
        tools_service = get_mcp_tools_service()
        db_config = tools_service.get_category_config('github')

        if not db_config or not db_config.get('config'):
            return {
                "success": False,
                "message": "No database configuration found to migrate"
            }

        # 转换配置格式
        file_config = {
            "enabled": True,
            "github_token": db_config.get('config', {}).get('github_token', ''),
            "api_base_url": "https://api.github.com",
            "timeout": 30,
            "retry_count": 3,
            "rate_limit": {
                "enabled": True,
                "max_requests_per_hour": 5000
            },
            "features": {
                "repository_management": True,
                "issue_management": True,
                "pull_request_management": True,
                "release_management": True,
                "organization_access": True,
                "gist_management": True
            },
            "security": {
                "verify_ssl": True,
                "log_api_calls": False,
                "mask_sensitive_data": True
            },
            "cache": {
                "enabled": True,
                "ttl_seconds": 300,
                "max_entries": 1000
            },
            "version": "1.0",
            "migrated_from_database": True,
            "migration_timestamp": datetime.now().isoformat()
        }

        # 将其他数据库配置项复制到文件配置
        for key, value in db_config.get('config', {}).items():
            if key not in file_config:
                file_config[key] = value

        config_service = get_tool_config_service()
        success = config_service.set_config("github", file_config)

        if success:
            return {
                "success": True,
                "message": "GitHub configuration migrated to file successfully",
                "data": {
                    "migrated_config": file_config,
                    "source": "database",
                    "target": "file",
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to migrate GitHub configuration to file"
            }

    except Exception as e:
        logger.error(f"Failed to migrate GitHub config to file: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to migrate GitHub configuration: Internal server error"
        }

@router.get("/tools/github/config/status")
async def get_github_config_status():
    """获取GitHub配置状态（数据库 vs 文件）"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()
        tools_service = get_mcp_tools_service()

        # 检查文件配置
        file_exists = config_service.config_exists("github")
        file_config = config_service.get_config("github") if file_exists else None
        file_info = config_service.get_config_file_info("github")

        # 检查数据库配置
        db_config = tools_service.get_category_config('github')
        has_db_config = db_config and db_config.get('config')

        return {
            "success": True,
            "message": "GitHub configuration status retrieved successfully",
            "data": {
                "file_storage": {
                    "exists": file_exists,
                    "config": file_config,
                    "file_info": file_info
                },
                "database_storage": {
                    "exists": has_db_config,
                    "config": db_config
                },
                "recommendation": "file" if file_exists else "migrate_to_file",
                "status": "file_based" if file_exists else "database_based"
            }
        }

    except Exception as e:
        logger.error(f"Failed to get GitHub config status: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get GitHub configuration status: Internal server error"
        }

# File Tools Configuration Endpoints
@router.get("/tools/file_tools/config")
async def get_file_tools_config():
    """获取文件工具的配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()
        config = config_service.get_config("file_tools")
        file_info = config_service.get_config_file_info("file_tools")

        return {
            "success": True,
            "message": "File tools configuration retrieved successfully",
            "data": {
                "config": config,
                "file_info": file_info,
                "storage_type": "file"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get file tools config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get file tools configuration: Internal server error"
        }

@router.put("/tools/file_tools/config")
@require_edit_permission
async def update_file_tools_config(request: Dict[str, Any]):
    """更新文件工具的配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_data = request.get("config", {})
        if not config_data:
            return {
                "success": False,
                "message": "Configuration data is required"
            }

        config_service = get_tool_config_service()

        # 备份当前配置
        backup_file = config_service.backup_config("file_tools")

        # 更新配置
        success = config_service.set_config("file_tools", config_data)

        if success:
            return {
                "success": True,
                "message": "File tools configuration updated successfully",
                "data": {
                    "updated_config": config_data,
                    "backup_file": backup_file,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to update file tools configuration"
            }

    except Exception as e:
        logger.error(f"Failed to update file tools config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to update file tools configuration: Internal server error"
        }

@router.get("/tools/file_tools/config/status")
async def get_file_tools_config_status():
    """获取文件工具配置状态"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()
        tools_service = get_mcp_tools_service()

        # 检查文件配置
        file_exists = config_service.config_exists("file_tools")
        file_config = config_service.get_config("file_tools") if file_exists else None
        file_info = config_service.get_config_file_info("file_tools")

        # 检查数据库配置
        db_config = tools_service.get_category_config('file_tools')
        has_db_config = db_config and db_config.get('config')

        return {
            "success": True,
            "message": "File tools configuration status retrieved successfully",
            "data": {
                "file_storage": {
                    "exists": file_exists,
                    "config": file_config,
                    "file_info": file_info
                },
                "database_storage": {
                    "exists": has_db_config,
                    "config": db_config
                },
                "recommendation": "file" if file_exists else "create_file_config",
                "status": "file_based" if file_exists else "database_based"
            }
        }

    except Exception as e:
        logger.error(f"Failed to get file tools config status: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get file tools configuration status: Internal server error"
        }

# Time Tools Configuration Endpoints
@router.get("/tools/time_tools/config")
async def get_time_tools_config():
    """获取时间工具的配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()
        config = config_service.get_config("time_tools")
        file_info = config_service.get_config_file_info("time_tools")

        return {
            "success": True,
            "message": "Time tools configuration retrieved successfully",
            "data": {
                "config": config,
                "file_info": file_info,
                "storage_type": "file"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get time tools config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get time tools configuration: Internal server error"
        }

@router.put("/tools/time_tools/config")
@require_edit_permission
async def update_time_tools_config(request: Dict[str, Any]):
    """更新时间工具的配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_data = request.get("config", {})
        if not config_data:
            return {
                "success": False,
                "message": "Configuration data is required"
            }

        config_service = get_tool_config_service()

        # 备份当前配置
        backup_file = config_service.backup_config("time_tools")

        # 更新配置
        success = config_service.set_config("time_tools", config_data)

        if success:
            return {
                "success": True,
                "message": "Time tools configuration updated successfully",
                "data": {
                    "updated_config": config_data,
                    "backup_file": backup_file,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to update time tools configuration"
            }

    except Exception as e:
        logger.error(f"Failed to update time tools config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to update time tools configuration: Internal server error"
        }

@router.get("/tools/time_tools/config/status")
async def get_time_tools_config_status():
    """获取时间工具配置状态"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()
        tools_service = get_mcp_tools_service()

        # 检查文件配置
        file_exists = config_service.config_exists("time_tools")
        file_config = config_service.get_config("time_tools") if file_exists else None
        file_info = config_service.get_config_file_info("time_tools")

        # 检查数据库配置
        db_config = tools_service.get_category_config('time_tools')
        has_db_config = db_config and db_config.get('config')

        return {
            "success": True,
            "message": "Time tools configuration status retrieved successfully",
            "data": {
                "file_storage": {
                    "exists": file_exists,
                    "config": file_config,
                    "file_info": file_info
                },
                "database_storage": {
                    "exists": has_db_config,
                    "config": db_config
                },
                "recommendation": "file" if file_exists else "create_file_config",
                "status": "file_based" if file_exists else "database_based"
            }
        }

    except Exception as e:
        logger.error(f"Failed to get time tools config status: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get time tools configuration status: Internal server error"
        }

# Cache Tools Configuration Endpoints
@router.get("/tools/cache_tools/config")
async def get_cache_tools_config():
    """获取缓存工具的配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()
        config = config_service.get_config("cache_tools")
        file_info = config_service.get_config_file_info("cache_tools")

        return {
            "success": True,
            "message": "Cache tools configuration retrieved successfully",
            "data": {
                "config": config,
                "file_info": file_info,
                "storage_type": "file"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get cache tools config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get cache tools configuration: Internal server error"
        }

@router.put("/tools/cache_tools/config")
@require_edit_permission
async def update_cache_tools_config(request: Dict[str, Any]):
    """更新缓存工具的配置"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_data = request.get("config", {})
        if not config_data:
            return {
                "success": False,
                "message": "Configuration data is required"
            }

        config_service = get_tool_config_service()

        # 备份当前配置
        backup_file = config_service.backup_config("cache_tools")

        # 更新配置
        success = config_service.set_config("cache_tools", config_data)

        if success:
            return {
                "success": True,
                "message": "Cache tools configuration updated successfully",
                "data": {
                    "updated_config": config_data,
                    "backup_file": backup_file,
                    "timestamp": datetime.now().isoformat()
                }
            }
        else:
            return {
                "success": False,
                "message": "Failed to update cache tools configuration"
            }

    except Exception as e:
        logger.error(f"Failed to update cache tools config: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to update cache tools configuration: Internal server error"
        }

@router.get("/tools/cache_tools/config/status")
async def get_cache_tools_config_status():
    """获取缓存工具配置状态"""
    try:
        from app.core.tool_config_service import get_tool_config_service

        config_service = get_tool_config_service()

        # 检查文件配置
        file_exists = config_service.config_exists("cache_tools")
        file_config = config_service.get_config("cache_tools") if file_exists else None
        file_info = config_service.get_config_file_info("cache_tools")

        return {
            "success": True,
            "message": "Cache tools configuration status retrieved successfully",
            "data": {
                "file_storage": {
                    "exists": file_exists,
                    "config": file_config,
                    "file_info": file_info
                },
                "recommendation": "file_based",
                "status": "file_based"
            }
        }

    except Exception as e:
        logger.error(f"Failed to get cache tools config status: {sanitize_for_log(str(e))}")
        return {
            "success": False,
            "message": "Failed to get cache tools configuration status: Internal server error"
        }

