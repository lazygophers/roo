"""
MCP (Model Context Protocol) server implementation
使用 FastMCP 提供 SSE 和 Streamable HTTP 传输
集成数据库工具管理系统
"""

import asyncio
import time
import platform
import psutil
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from mcp import types

from app.core.mcp_tools_service import get_mcp_tools_service
from app.core.database_service import get_database_service
from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log

logger = setup_logging("INFO")


class LazyAIMCPServer:
    """LazyAI Studio MCP 服务器实现"""
    
    def __init__(self):
        self.mcp = FastMCP("LazyAI Studio")
        self.tools_service = get_mcp_tools_service()
        self.db_service = get_database_service()
        self._setup_tools_from_database()
        
    def _setup_tools_from_database(self):
        """从数据库动态设置 MCP 工具"""
        enabled_tools = self.tools_service.get_tools(enabled_only=True)
        logger.info(f"Setting up {len(enabled_tools)} MCP tools from database")
        
        for tool_data in enabled_tools:
            tool_name = tool_data['name']
            self._register_tool(tool_data)
            logger.info(f"Registered MCP tool: {sanitize_for_log(tool_name)}")
    
    def _register_tool(self, tool_data: Dict[str, Any]):
        """注册单个工具到FastMCP"""
        tool_name = tool_data['name']
        tool_description = tool_data['description']
        tool_schema = tool_data['schema']
        
        # 创建工具实现函数
        if tool_name == "get_current_timestamp":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def get_current_timestamp_impl(**kwargs) -> str:
                """获取当前时间戳实现"""
                format_type = kwargs.get('format', 'iso')
                timezone = kwargs.get('timezone', 'local')
                
                now = datetime.now()
                unix_timestamp = int(time.time())
                
                if format_type == 'unix':
                    return str(unix_timestamp)
                elif format_type == 'formatted':
                    return now.strftime('%Y-%m-%d %H:%M:%S')
                else:  # iso
                    return now.isoformat()
                    
        elif tool_name == "get_system_info":
            @self.mcp.tool(name=tool_name, description=tool_description) 
            def get_system_info_impl(**kwargs) -> str:
                """获取系统信息实现"""
                detailed = kwargs.get('detailed', False)
                include_performance = kwargs.get('include_performance', True)
                
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1) if include_performance else 0
                
                result = f"""LazyAI Studio 系统信息:
- Python 版本: {platform.python_version()}
- 操作系统: {platform.system()} {platform.release()}
- CPU 使用率: {cpu_percent}%
- 内存使用: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
- 可用内存: {memory.available // 1024 // 1024}MB
- LazyGophers 出品 - 让 AI 替你思考！"""
                
                if detailed:
                    disk = psutil.disk_usage('/')
                    result += f"""
                    
详细信息:
- 磁盘使用: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)
- CPU 核心数: {psutil.cpu_count()}
- 启动时间: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}"""
                
                return result
                
        elif tool_name == "list_available_modes":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def list_available_modes_impl(**kwargs) -> str:
                """列出可用AI模式实现"""
                category = kwargs.get('category', 'all')
                include_description = kwargs.get('include_description', True)
                
                try:
                    models_data = self.db_service.get_models_data()
                    if category != 'all':
                        models_data = [m for m in models_data if category in m.get('groups', [])]
                    
                    result = "LazyAI Studio 可用模式:\n\n"
                    
                    for model in models_data[:10]:  # 限制数量
                        emoji_map = {
                            'orchestrator': '🧠', 'architect': '🏗️', 'ask': '📚',
                            'code': '🪄', 'code-python': '🐍', 'debug': '🔬',
                            'doc-writer': '✍️', 'giter': '⚙️', 'memory': '🧠',
                            'project-research': '🔍'
                        }
                        emoji = emoji_map.get(model.get('slug', ''), '🔧')
                        name = model.get('name', 'Unknown')
                        slug = model.get('slug', '')
                        
                        result += f"{emoji} {slug} - {name}\n"
                        
                        if include_description and model.get('description'):
                            result += f"   {model['description'][:100]}...\n"
                    
                    result += "\nLazyGophers - 让你做个聪明的懒人！ 🛋️"
                    return result
                    
                except Exception as e:
                    logger.error(f"Failed to list modes: {sanitize_for_log(str(e))}")
                    return "获取AI模式列表失败，请稍后重试"
        
        elif tool_name == "get_project_stats":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def get_project_stats_impl(**kwargs) -> str:
                """获取项目统计信息实现"""
                include_models = kwargs.get('include_models', True)
                include_files = kwargs.get('include_files', True)
                
                try:
                    result = "LazyAI Studio 项目统计:\n\n"
                    
                    if include_models:
                        models_data = self.db_service.get_models_data()
                        result += f"📊 模型统计:\n"
                        result += f"  - 总模型数量: {len(models_data)}\n"
                        
                        # 按分组统计
                        groups = {}
                        for model in models_data:
                            for group in model.get('groups', []):
                                groups[group] = groups.get(group, 0) + 1
                        
                        result += f"  - 分组分布: {dict(list(groups.items())[:5])}\n\n"
                    
                    if include_files:
                        tools_stats = self.tools_service.get_statistics()
                        result += f"🔧 工具统计:\n"
                        result += f"  - 可用工具: {tools_stats['enabled_tools']}\n"
                        result += f"  - 工具分类: {tools_stats['total_categories']}\n\n"
                    
                    result += f"📈 系统状态: 正常运行\n"
                    result += f"⏰ 统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += "\nLazyGophers - 数据驱动的智能工作室！ 📊"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Failed to get project stats: {sanitize_for_log(str(e))}")
                    return "获取项目统计失败，请稍后重试"
        
        elif tool_name == "health_check":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def health_check_impl(**kwargs) -> str:
                """系统健康检查实现"""
                check_database = kwargs.get('check_database', True)
                check_cache = kwargs.get('check_cache', True)
                
                try:
                    result = "LazyAI Studio 系统健康检查:\n\n"
                    overall_status = "✅ 健康"
                    
                    if check_database:
                        try:
                            models_count = len(self.db_service.get_models_data())
                            result += f"📊 数据库: ✅ 正常 ({models_count} 模型)\n"
                        except Exception as e:
                            result += f"📊 数据库: ❌ 异常\n"
                            overall_status = "⚠️ 部分异常"
                    
                    if check_cache:
                        try:
                            tools_count = len(self.tools_service.get_tools())
                            result += f"🔧 工具系统: ✅ 正常 ({tools_count} 工具)\n"
                        except Exception as e:
                            result += f"🔧 工具系统: ❌ 异常\n"
                            overall_status = "⚠️ 部分异常"
                    
                    # 系统资源检查
                    memory = psutil.virtual_memory()
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    
                    if memory.percent > 90:
                        result += f"💾 内存: ⚠️ 使用率过高 ({memory.percent}%)\n"
                        overall_status = "⚠️ 部分异常"
                    else:
                        result += f"💾 内存: ✅ 正常 ({memory.percent}%)\n"
                    
                    if cpu_percent > 80:
                        result += f"🖥️ CPU: ⚠️ 使用率过高 ({cpu_percent}%)\n"
                    else:
                        result += f"🖥️ CPU: ✅ 正常 ({cpu_percent}%)\n"
                    
                    result += f"\n🏥 整体状态: {overall_status}\n"
                    result += f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += "\nLazyGophers - 让系统健康运行！ 🏥"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Health check failed: {sanitize_for_log(str(e))}")
                    return "健康检查执行失败，请稍后重试"
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return self.tools_service.get_tools(enabled_only=True)
    
    def get_tools_by_category(self) -> Dict[str, Any]:
        """按分类获取工具"""
        return self.tools_service.get_tools_by_category()
    
    def refresh_tools(self) -> Dict[str, int]:
        """刷新工具配置"""
        logger.info("Refreshing MCP tools from database")
        
        # 重新注册内置工具
        result = self.tools_service.register_builtin_tools()
        
        # 重新设置FastMCP工具
        # 注意: FastMCP可能不支持动态重新注册，这里只是记录
        logger.info(f"Tools refreshed: {result}")
        return result
    
    def get_fastapi_app(self):
        """获取 FastAPI 应用实例用于集成"""
        return self.mcp


# 全局 MCP 服务器实例
_mcp_server = None

def get_mcp_server() -> LazyAIMCPServer:
    """获取 MCP 服务器实例"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = LazyAIMCPServer()
    return _mcp_server

def init_mcp_server() -> LazyAIMCPServer:
    """初始化 MCP 服务器"""
    logger.info("Initializing MCP server...")
    
    mcp_server = get_mcp_server()
    tools_count = len(mcp_server.get_available_tools())
    
    logger.info(f"MCP server initialized with {tools_count} tools")
    return mcp_server