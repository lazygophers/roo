"""
MCP工具注册装饰器系统
通过装饰器自动注册和发现MCP工具，支持模块化管理
"""
import inspect
import importlib.util
from pathlib import Path
from typing import Dict, List, Callable, Any, Optional
from functools import wraps
from app.models.mcp_tool import MCPTool
from app.core.logging import setup_logging

logger = setup_logging()

# 全局工具注册表
_TOOL_REGISTRY: Dict[str, MCPTool] = {}
_CATEGORY_REGISTRY: Dict[str, List[str]] = {}

# 分类定义注册表（存储分类的元数据）
_CATEGORY_DEFINITIONS: Dict[str, Dict[str, Any]] = {}


def mcp_category(
    category_id: str,
    name: str,
    description: str,
    icon: str = "📦",
    enabled: bool = True,
    sort_order: int = 999,
    config: Optional[Dict[str, Any]] = None
):
    """
    MCP工具分类注册装饰器

    Args:
        category_id: 分类ID（唯一标识符）
        name: 分类名称
        description: 分类描述
        icon: 分类图标
        enabled: 是否默认启用
        sort_order: 排序顺序（数字越小越靠前）
        config: 分类配置

    Usage:
        @mcp_category(
            category_id="fetch",
            name="网络抓取工具",
            description="网页抓取、HTTP请求、API调用等网络数据获取工具",
            icon="🌐",
            sort_order=6
        )
        def register_fetch_category():
            pass
    """
    def decorator(func):
        from datetime import datetime

        # 构建分类定义
        category_def = {
            "id": category_id,
            "name": name,
            "description": description,
            "icon": icon,
            "enabled": enabled,
            "sort_order": sort_order,
            "config": config or {},
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # 注册到分类定义表
        _CATEGORY_DEFINITIONS[category_id] = category_def
        logger.debug(f"Registered MCP category: {category_id} - {name}")

        return func

    return decorator


def mcp_tool(
    name: str,
    description: str,
    category: str,
    schema: Dict[str, Any],
    returns: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    enabled: bool = True
):
    """
    MCP工具注册装饰器

    Args:
        name: 工具名称
        description: 工具描述
        category: 工具分类
        schema: 输入参数的JSON Schema定义
        returns: 返回值的JSON Schema定义
        metadata: 元数据信息
        enabled: 是否默认启用

    Usage:
        @mcp_tool(
            name="github_get_repo",
            description="获取GitHub仓库信息",
            category="github",
            schema={
                "type": "object",
                "properties": {
                    "owner": {"type": "string", "description": "仓库所有者"},
                    "repo": {"type": "string", "description": "仓库名称"}
                },
                "required": ["owner", "repo"]
            },
            returns={
                "type": "object",
                "properties": {
                    "id": {"type": "integer", "description": "仓库ID"},
                    "name": {"type": "string", "description": "仓库名称"},
                    "full_name": {"type": "string", "description": "完整仓库名"},
                    "description": {"type": "string", "description": "仓库描述"},
                    "private": {"type": "boolean", "description": "是否私有"},
                    "stargazers_count": {"type": "integer", "description": "星标数量"}
                },
                "required": ["id", "name", "full_name"]
            },
            metadata={"tags": ["github", "repository"]}
        )
        def github_get_repo():
            pass
    """
    def decorator(func: Callable) -> Callable:
        # 自动添加分类前缀（如果名称还没有前缀）
        final_name = name
        prefix = f"{category}_"
        if not name.startswith(prefix):
            final_name = f"{prefix}{name}"

        # 创建MCPTool实例
        tool = MCPTool(
            name=final_name,
            description=description,
            category=category,
            schema=schema,
            returns=returns,
            metadata=metadata or {},
            enabled=enabled,
            implementation_type="builtin"
        )

        # 注册到全局注册表
        _TOOL_REGISTRY[final_name] = tool

        # 注册到分类表
        if category not in _CATEGORY_REGISTRY:
            _CATEGORY_REGISTRY[category] = []
        _CATEGORY_REGISTRY[category].append(final_name)

        logger.debug(f"Registered MCP tool: {final_name} in category: {category}")

        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # 将工具元数据附加到函数
        wrapper._mcp_tool = tool
        return wrapper

    return decorator


def get_registered_tools() -> List[MCPTool]:
    """获取所有已注册的工具"""
    return list(_TOOL_REGISTRY.values())


def get_tools_by_category(category: str) -> List[MCPTool]:
    """获取指定分类的工具"""
    if category not in _CATEGORY_REGISTRY:
        return []

    tools = []
    for tool_name in _CATEGORY_REGISTRY[category]:
        if tool_name in _TOOL_REGISTRY:
            tools.append(_TOOL_REGISTRY[tool_name])

    return tools


def get_tool_by_name(name: str) -> Optional[MCPTool]:
    """根据名称获取工具"""
    return _TOOL_REGISTRY.get(name)


def clear_registry():
    """清空注册表（主要用于测试）"""
    global _TOOL_REGISTRY, _CATEGORY_REGISTRY, _CATEGORY_DEFINITIONS
    _TOOL_REGISTRY.clear()
    _CATEGORY_REGISTRY.clear()
    _CATEGORY_DEFINITIONS.clear()


def auto_discover_tools(module_paths: List[str]) -> int:
    """
    自动发现和注册工具

    Args:
        module_paths: 要扫描的模块路径列表

    Returns:
        发现的工具数量
    """
    discovered_count = 0

    for module_path in module_paths:
        try:
            # 如果是文件路径，直接导入
            if module_path.endswith('.py'):
                spec = importlib.util.spec_from_file_location("temp_module", module_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    discovered_count += _scan_module_for_tools(module)
            else:
                # 如果是模块名，尝试导入
                try:
                    module = importlib.import_module(module_path)
                    discovered_count += _scan_module_for_tools(module)
                except ImportError as e:
                    logger.warning(f"Failed to import module {module_path}: {e}")

        except Exception as e:
            logger.error(f"Error discovering tools in {module_path}: {e}")

    logger.info(f"Auto-discovered {discovered_count} MCP tools")
    return discovered_count


def _scan_module_for_tools(module) -> int:
    """扫描模块中的装饰器注册工具"""
    count = 0

    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and hasattr(obj, '_mcp_tool'):
            count += 1
            logger.debug(f"Found decorated tool function: {name}")

    return count


def scan_tools_directory(directory: str, pattern: str = "**/*_tools.py") -> int:
    """
    扫描指定目录下的工具文件

    Args:
        directory: 要扫描的目录
        pattern: 文件匹配模式

    Returns:
        发现的工具数量
    """
    directory_path = Path(directory)
    if not directory_path.exists():
        logger.warning(f"Tools directory does not exist: {directory}")
        return 0

    tool_files = list(directory_path.glob(pattern))
    module_paths = [str(f) for f in tool_files]

    logger.info(f"Scanning {len(tool_files)} tool files in {directory}")
    return auto_discover_tools(module_paths)


def get_registry_stats() -> Dict[str, Any]:
    """获取注册表统计信息"""
    return {
        "total_tools": len(_TOOL_REGISTRY),
        "categories": len(_CATEGORY_REGISTRY),
        "category_definitions": len(_CATEGORY_DEFINITIONS),
        "tools_by_category": {
            category: len(tools)
            for category, tools in _CATEGORY_REGISTRY.items()
        },
        "registered_tools": list(_TOOL_REGISTRY.keys()),
        "registered_categories": list(_CATEGORY_DEFINITIONS.keys())
    }


def get_registered_categories() -> List[Dict[str, Any]]:
    """获取所有已注册的分类定义"""
    return list(_CATEGORY_DEFINITIONS.values())


def get_category_definition(category_id: str) -> Optional[Dict[str, Any]]:
    """获取指定分类的定义"""
    return _CATEGORY_DEFINITIONS.get(category_id)


# 便捷的分类装饰器
def github_tool(name: str, description: str, schema: Dict[str, Any], **kwargs):
    """GitHub工具装饰器快捷方式"""
    return mcp_tool(name, description, "github", schema, **kwargs)


def time_tool(name: str, description: str, schema: Dict[str, Any], **kwargs):
    """时间工具装饰器快捷方式"""
    return mcp_tool(name, description, "time", schema, **kwargs)


def file_tool(name: str, description: str, schema: Dict[str, Any], **kwargs):
    """文件工具装饰器快捷方式"""
    return mcp_tool(name, description, "file", schema, **kwargs)


def system_tool(name: str, description: str, schema: Dict[str, Any], **kwargs):
    """系统工具装饰器快捷方式"""
    return mcp_tool(name, description, "system", schema, **kwargs)


def cache_tool(name: str, description: str, schema: Dict[str, Any], **kwargs):
    """缓存工具装饰器快捷方式"""
    return mcp_tool(name, description, "cache", schema, **kwargs)


def fetch_tool(name: str, description: str, schema: Dict[str, Any], **kwargs):
    """网络抓取工具装饰器快捷方式"""
    return mcp_tool(name, description, "fetch", schema, **kwargs)