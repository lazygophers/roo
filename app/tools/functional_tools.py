"""
函数式工具系统 - 替代MCP工具

提供简化的工具注册和执行系统，专注于核心功能
"""

import asyncio
import aiohttp
import aiofiles
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import hashlib

from app.core.functional_base import Result, safe, create_logger
from app.core.tools_functional import tool, category, get_global_registry

logger = create_logger('functional_tools')

# =============================================================================
# 工具分类注册
# =============================================================================

@category(
    category_id="core",
    name="核心工具",
    description="系统核心功能工具",
    icon="⚙️"
)
def register_core_category():
    pass

@category(
    category_id="file",
    name="文件操作",
    description="文件读写和处理工具",
    icon="📁"
)
def register_file_category():
    pass

@category(
    category_id="web",
    name="网络工具",
    description="网络请求和数据获取工具",
    icon="🌐"
)
def register_web_category():
    pass

@category(
    category_id="data",
    name="数据处理",
    description="数据分析和处理工具",
    icon="📊"
)
def register_data_category():
    pass

# =============================================================================
# 核心工具
# =============================================================================

@tool(
    name="get_current_time",
    description="获取当前时间",
    category="core",
    returns={"type": "string", "description": "ISO格式的当前时间"}
)
def get_current_time() -> str:
    """获取当前时间"""
    return datetime.now().isoformat()

@tool(
    name="generate_uuid",
    description="生成UUID",
    category="core",
    returns={"type": "string", "description": "生成的UUID字符串"}
)
def generate_uuid() -> str:
    """生成UUID"""
    import uuid
    return str(uuid.uuid4())

@tool(
    name="hash_text",
    description="计算文本的MD5哈希",
    category="core",
    parameters={
        "text": {"type": "string", "required": True, "description": "要哈希的文本"}
    },
    returns={"type": "string", "description": "MD5哈希值"}
)
def hash_text(text: str) -> str:
    """计算文本的MD5哈希"""
    return hashlib.md5(text.encode()).hexdigest()

# =============================================================================
# 文件操作工具
# =============================================================================

@tool(
    name="read_file",
    description="读取文件内容",
    category="file",
    parameters={
        "file_path": {"type": "string", "required": True, "description": "文件路径"},
        "encoding": {"type": "string", "required": False, "default": "utf-8", "description": "文件编码"}
    },
    returns={"type": "string", "description": "文件内容"}
)
async def read_file(file_path: str, encoding: str = "utf-8") -> Result:
    """读取文件内容"""
    try:
        async with aiofiles.open(file_path, mode='r', encoding=encoding) as f:
            content = await f.read()
        return Result(value=content)
    except Exception as e:
        return Result(error=e)

@tool(
    name="write_file",
    description="写入文件内容",
    category="file",
    parameters={
        "file_path": {"type": "string", "required": True, "description": "文件路径"},
        "content": {"type": "string", "required": True, "description": "文件内容"},
        "encoding": {"type": "string", "required": False, "default": "utf-8", "description": "文件编码"}
    },
    returns={"type": "boolean", "description": "是否写入成功"}
)
async def write_file(file_path: str, content: str, encoding: str = "utf-8") -> Result:
    """写入文件内容"""
    try:
        # 确保目录存在
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        async with aiofiles.open(file_path, mode='w', encoding=encoding) as f:
            await f.write(content)
        return Result(value=True)
    except Exception as e:
        return Result(error=e)

@tool(
    name="list_directory",
    description="列出目录内容",
    category="file",
    parameters={
        "directory_path": {"type": "string", "required": True, "description": "目录路径"},
        "pattern": {"type": "string", "required": False, "description": "文件模式过滤"}
    },
    returns={"type": "array", "description": "文件和目录列表"}
)
def list_directory(directory_path: str, pattern: Optional[str] = None) -> Result:
    """列出目录内容"""
    try:
        path = Path(directory_path)
        if not path.exists():
            return Result(error=FileNotFoundError(f"Directory not found: {directory_path}"))

        if not path.is_dir():
            return Result(error=ValueError(f"Path is not a directory: {directory_path}"))

        if pattern:
            files = list(path.glob(pattern))
        else:
            files = list(path.iterdir())

        result = []
        for file_path in files:
            result.append({
                "name": file_path.name,
                "path": str(file_path),
                "is_file": file_path.is_file(),
                "is_directory": file_path.is_dir(),
                "size": file_path.stat().st_size if file_path.is_file() else None,
                "modified_time": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })

        return Result(value=result)
    except Exception as e:
        return Result(error=e)

@tool(
    name="file_exists",
    description="检查文件是否存在",
    category="file",
    parameters={
        "file_path": {"type": "string", "required": True, "description": "文件路径"}
    },
    returns={"type": "boolean", "description": "文件是否存在"}
)
def file_exists(file_path: str) -> bool:
    """检查文件是否存在"""
    return Path(file_path).exists()

# =============================================================================
# 网络工具
# =============================================================================

@tool(
    name="fetch_url",
    description="获取URL内容",
    category="web",
    parameters={
        "url": {"type": "string", "required": True, "description": "要获取的URL"},
        "method": {"type": "string", "required": False, "default": "GET", "description": "HTTP方法"},
        "headers": {"type": "object", "required": False, "description": "请求头"},
        "timeout": {"type": "number", "required": False, "default": 30, "description": "超时时间（秒）"}
    },
    returns={"type": "object", "description": "响应数据"}
)
async def fetch_url(url: str, method: str = "GET", headers: Optional[Dict[str, str]] = None,
                   timeout: int = 30) -> Result:
    """获取URL内容"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.request(method, url, headers=headers) as response:
                content = await response.text()

                return Result(value={
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "content": content,
                    "url": str(response.url)
                })
    except Exception as e:
        return Result(error=e)

@tool(
    name="fetch_json",
    description="获取JSON数据",
    category="web",
    parameters={
        "url": {"type": "string", "required": True, "description": "JSON API URL"},
        "headers": {"type": "object", "required": False, "description": "请求头"},
        "timeout": {"type": "number", "required": False, "default": 30, "description": "超时时间（秒）"}
    },
    returns={"type": "object", "description": "JSON数据"}
)
async def fetch_json(url: str, headers: Optional[Dict[str, str]] = None,
                    timeout: int = 30) -> Result:
    """获取JSON数据"""
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.get(url, headers=headers) as response:
                if response.content_type != 'application/json':
                    logger.warning(f"Response content type is not JSON: {response.content_type}")

                data = await response.json()
                return Result(value=data)
    except Exception as e:
        return Result(error=e)

@tool(
    name="post_json",
    description="发送JSON数据",
    category="web",
    parameters={
        "url": {"type": "string", "required": True, "description": "目标URL"},
        "data": {"type": "object", "required": True, "description": "要发送的JSON数据"},
        "headers": {"type": "object", "required": False, "description": "请求头"},
        "timeout": {"type": "number", "required": False, "default": 30, "description": "超时时间（秒）"}
    },
    returns={"type": "object", "description": "响应数据"}
)
async def post_json(url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None,
                   timeout: int = 30) -> Result:
    """发送JSON数据"""
    try:
        request_headers = {"Content-Type": "application/json"}
        if headers:
            request_headers.update(headers)

        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=timeout)) as session:
            async with session.post(url, json=data, headers=request_headers) as response:
                content = await response.text()

                return Result(value={
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "content": content
                })
    except Exception as e:
        return Result(error=e)

# =============================================================================
# 数据处理工具
# =============================================================================

@tool(
    name="parse_json",
    description="解析JSON字符串",
    category="data",
    parameters={
        "json_string": {"type": "string", "required": True, "description": "JSON字符串"}
    },
    returns={"type": "object", "description": "解析后的对象"}
)
def parse_json(json_string: str) -> Result:
    """解析JSON字符串"""
    try:
        data = json.loads(json_string)
        return Result(value=data)
    except Exception as e:
        return Result(error=e)

@tool(
    name="stringify_json",
    description="将对象转换为JSON字符串",
    category="data",
    parameters={
        "data": {"type": "object", "required": True, "description": "要转换的对象"},
        "indent": {"type": "number", "required": False, "description": "缩进空格数"}
    },
    returns={"type": "string", "description": "JSON字符串"}
)
def stringify_json(data: Any, indent: Optional[int] = None) -> Result:
    """将对象转换为JSON字符串"""
    try:
        json_string = json.dumps(data, indent=indent, ensure_ascii=False)
        return Result(value=json_string)
    except Exception as e:
        return Result(error=e)

@tool(
    name="filter_list",
    description="过滤列表",
    category="data",
    parameters={
        "items": {"type": "array", "required": True, "description": "要过滤的列表"},
        "key": {"type": "string", "required": True, "description": "过滤键"},
        "value": {"type": "any", "required": True, "description": "过滤值"}
    },
    returns={"type": "array", "description": "过滤后的列表"}
)
def filter_list(items: List[Dict[str, Any]], key: str, value: Any) -> Result:
    """过滤列表"""
    try:
        filtered_items = [item for item in items if item.get(key) == value]
        return Result(value=filtered_items)
    except Exception as e:
        return Result(error=e)

@tool(
    name="sort_list",
    description="排序列表",
    category="data",
    parameters={
        "items": {"type": "array", "required": True, "description": "要排序的列表"},
        "key": {"type": "string", "required": True, "description": "排序键"},
        "reverse": {"type": "boolean", "required": False, "default": False, "description": "是否倒序"}
    },
    returns={"type": "array", "description": "排序后的列表"}
)
def sort_list(items: List[Dict[str, Any]], key: str, reverse: bool = False) -> Result:
    """排序列表"""
    try:
        sorted_items = sorted(items, key=lambda x: x.get(key, ''), reverse=reverse)
        return Result(value=sorted_items)
    except Exception as e:
        return Result(error=e)

# =============================================================================
# 工具管理功能
# =============================================================================

def get_available_tools() -> Dict[str, Any]:
    """获取所有可用工具"""
    registry = get_global_registry()
    from app.core.tools_functional import get_all_tools, get_all_categories

    tools = get_all_tools(registry)
    categories = get_all_categories(registry)

    return {
        "tools": [tool.to_dict() for tool in tools],
        "categories": [category.to_dict() for category in categories],
        "total_tools": len(tools),
        "total_categories": len(categories)
    }

def get_tool_by_name(tool_name: str) -> Optional[Dict[str, Any]]:
    """根据名称获取工具"""
    registry = get_global_registry()
    from app.core.tools_functional import get_tool

    tool_def = get_tool(registry, tool_name)
    if tool_def:
        return tool_def.to_dict()
    return None

async def execute_tool_by_name(tool_name: str, **kwargs) -> Result:
    """根据名称执行工具"""
    registry = get_global_registry()
    from app.core.tools_functional import execute_tool_async

    return await execute_tool_async(registry, tool_name, kwargs=kwargs)

# =============================================================================
# 初始化函数
# =============================================================================

def initialize_functional_tools():
    """初始化函数式工具系统"""
    logger.info("Initializing functional tools system...")

    # 注册分类（通过导入自动执行）
    register_core_category()
    register_file_category()
    register_web_category()
    register_data_category()

    # 工具已通过装饰器自动注册
    registry = get_global_registry()
    from app.core.tools_functional import get_registry_stats

    stats = get_registry_stats(registry)
    logger.info(f"Functional tools initialized: {stats['total_tools']} tools in {stats['total_categories']} categories")

    return stats

# 自动初始化
if __name__ != "__main__":
    initialize_functional_tools()