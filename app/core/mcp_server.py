"""
MCP (Model Context Protocol) server implementation
使用 FastMCP 提供 SSE 和 Streamable HTTP 传输
"""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from mcp import types


class LazyAIMCPServer:
    """LazyAI Studio MCP 服务器实现"""
    
    def __init__(self):
        self.mcp = FastMCP("LazyAI Studio")
        self._setup_tools()
        
    def _setup_tools(self):
        """设置 MCP 工具"""
        
        @self.mcp.tool()
        def get_current_timestamp() -> str:
            """获取当前时间戳
            
            Returns:
                str: 当前时间的 ISO 格式字符串和 Unix 时间戳
            """
            now = datetime.now()
            unix_timestamp = int(time.time())
            
            return f"""当前时间信息:
- ISO 格式: {now.isoformat()}
- Unix 时间戳: {unix_timestamp}
- 格式化时间: {now.strftime('%Y-%m-%d %H:%M:%S')}
- 时区: {now.astimezone().tzname()}"""

        @self.mcp.tool()
        def get_system_info() -> str:
            """获取 LazyAI Studio 系统信息
            
            Returns:
                str: 系统信息和状态
            """
            import platform
            import psutil
            
            memory = psutil.virtual_memory()
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return f"""LazyAI Studio 系统信息:
- Python 版本: {platform.python_version()}
- 操作系统: {platform.system()} {platform.release()}
- CPU 使用率: {cpu_percent}%
- 内存使用: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
- 可用内存: {memory.available // 1024 // 1024}MB
- LazyGophers 出品 - 让 AI 替你思考！"""

        @self.mcp.tool()
        def list_available_modes() -> str:
            """列出可用的 AI 模式
            
            Returns:
                str: 可用模式列表
            """
            modes = [
                "🧠 orchestrator - Brain (智能中枢)",
                "🏗️ architect - 顶尖架构师",
                "📚 ask - 学术顾问", 
                "🪄 code - 代码魔法师",
                "🐍 code-python - Python 代码魔法师",
                "🔬 debug - 异常分析师",
                "✍️ doc-writer - 文档工程师",
                "⚙️ giter - 版本控制专家",
                "🧠 memory - 记忆中枢",
                "🔍 project-research - 项目研究员"
            ]
            
            return f"""LazyAI Studio 可用模式:

{chr(10).join(modes)}

🎯 快速选择建议:
- 需要架构设计 → architect
- 编写代码功能 → code 或 code-python
- 调试问题 → debug  
- 分析项目 → project-research
- 任务规划 → orchestrator

LazyGophers - 让你做个聪明的懒人！ 🛋️"""

    def get_fastapi_app(self):
        """获取 FastAPI 应用实例用于集成"""
        return self.mcp


# 全局 MCP 服务器实例
mcp_server = LazyAIMCPServer()

def get_mcp_server() -> LazyAIMCPServer:
    """获取 MCP 服务器实例"""
    return mcp_server