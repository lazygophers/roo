"""
函数式工具注册和执行系统

替代MCP工具系统，提供简洁的工具注册、分类和执行功能
"""

import asyncio
import inspect
from typing import Dict, List, Any, Callable, Optional, Union
from functools import wraps
from dataclasses import dataclass, field
from datetime import datetime
import json

from app.core.functional_base import (
    Result, safe, create_logger, pipe, merge_dicts
)

# =============================================================================
# 工具定义
# =============================================================================

@dataclass
class ToolDefinition:
    """工具定义"""
    name: str
    description: str
    func: Callable
    category: str = "general"
    parameters: Dict[str, Any] = field(default_factory=dict)
    returns: Dict[str, Any] = field(default_factory=dict)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'parameters': self.parameters,
            'returns': self.returns,
            'examples': self.examples,
            'tags': self.tags,
            'version': self.version,
            'created_at': self.created_at
        }

@dataclass
class ToolCategory:
    """工具分类"""
    category_id: str
    name: str
    description: str
    icon: str = "🔧"
    tools: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            'category_id': self.category_id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'tools': self.tools,
            'created_at': self.created_at
        }

# =============================================================================
# 工具注册表
# =============================================================================

def create_tool_registry() -> Dict[str, Any]:
    """创建工具注册表"""
    return {
        'tools': {},
        'categories': {},
        'logger': create_logger('tool_registry')
    }

def register_tool(registry: Dict[str, Any], tool_def: ToolDefinition) -> Result:
    """注册工具"""
    try:
        # 检查工具是否已存在
        if tool_def.name in registry['tools']:
            return Result(error=ValueError(f"Tool {tool_def.name} already exists"))

        # 验证工具函数
        if not callable(tool_def.func):
            return Result(error=ValueError("Tool function must be callable"))

        # 注册工具
        registry['tools'][tool_def.name] = tool_def

        # 更新分类
        if tool_def.category in registry['categories']:
            if tool_def.name not in registry['categories'][tool_def.category].tools:
                registry['categories'][tool_def.category].tools.append(tool_def.name)

        registry['logger'].info(f"Registered tool: {tool_def.name}")
        return Result(value=tool_def)

    except Exception as e:
        return Result(error=e)

def register_category(registry: Dict[str, Any], category: ToolCategory) -> Result:
    """注册工具分类"""
    try:
        registry['categories'][category.category_id] = category
        registry['logger'].info(f"Registered category: {category.category_id}")
        return Result(value=category)
    except Exception as e:
        return Result(error=e)

def unregister_tool(registry: Dict[str, Any], tool_name: str) -> Result:
    """注销工具"""
    try:
        if tool_name not in registry['tools']:
            return Result(error=ValueError(f"Tool {tool_name} not found"))

        tool_def = registry['tools'][tool_name]

        # 从分类中移除
        if tool_def.category in registry['categories']:
            category = registry['categories'][tool_def.category]
            if tool_name in category.tools:
                category.tools.remove(tool_name)

        # 删除工具
        del registry['tools'][tool_name]

        registry['logger'].info(f"Unregistered tool: {tool_name}")
        return Result(value=tool_def)

    except Exception as e:
        return Result(error=e)

# =============================================================================
# 工具装饰器
# =============================================================================

def create_tool_decorator(registry: Dict[str, Any]):
    """创建工具注册装饰器"""

    def tool(name: str = None, description: str = "", category: str = "general",
             parameters: Dict[str, Any] = None, returns: Dict[str, Any] = None,
             examples: List[Dict[str, Any]] = None, tags: List[str] = None,
             version: str = "1.0.0"):
        """工具注册装饰器"""

        def decorator(func: Callable):
            tool_name = name or func.__name__
            tool_description = description or func.__doc__ or "No description"

            # 自动推断参数信息
            if parameters is None:
                sig = inspect.signature(func)
                auto_parameters = {}
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue

                    param_info = {
                        'type': str(param.annotation) if param.annotation != param.empty else 'Any',
                        'required': param.default == param.empty
                    }

                    if param.default != param.empty:
                        param_info['default'] = param.default

                    auto_parameters[param_name] = param_info
            else:
                auto_parameters = parameters

            # 创建工具定义
            tool_def = ToolDefinition(
                name=tool_name,
                description=tool_description,
                func=func,
                category=category,
                parameters=auto_parameters or {},
                returns=returns or {},
                examples=examples or [],
                tags=tags or [],
                version=version
            )

            # 注册工具
            result = register_tool(registry, tool_def)
            if result.is_error:
                registry['logger'].error(f"Failed to register tool {tool_name}: {result.error}")

            return func

        return decorator

    return tool

def create_category_decorator(registry: Dict[str, Any]):
    """创建分类注册装饰器"""

    def category(category_id: str, name: str, description: str, icon: str = "🔧"):
        """分类注册装饰器"""

        def decorator(func: Callable):
            cat = ToolCategory(
                category_id=category_id,
                name=name,
                description=description,
                icon=icon
            )

            result = register_category(registry, cat)
            if result.is_error:
                registry['logger'].error(f"Failed to register category {category_id}: {result.error}")

            return func

        return decorator

    return category

# =============================================================================
# 工具执行
# =============================================================================

def execute_tool(registry: Dict[str, Any], tool_name: str,
                args: List[Any] = None, kwargs: Dict[str, Any] = None) -> Result:
    """执行工具"""
    try:
        if tool_name not in registry['tools']:
            return Result(error=ValueError(f"Tool {tool_name} not found"))

        tool_def = registry['tools'][tool_name]
        args = args or []
        kwargs = kwargs or {}

        # 执行工具函数
        if asyncio.iscoroutinefunction(tool_def.func):
            # 异步函数
            return Result(error=ValueError("Use execute_tool_async for async tools"))
        else:
            # 同步函数
            result = tool_def.func(*args, **kwargs)
            return Result(value=result)

    except Exception as e:
        return Result(error=e)

async def execute_tool_async(registry: Dict[str, Any], tool_name: str,
                           args: List[Any] = None, kwargs: Dict[str, Any] = None) -> Result:
    """异步执行工具"""
    try:
        if tool_name not in registry['tools']:
            return Result(error=ValueError(f"Tool {tool_name} not found"))

        tool_def = registry['tools'][tool_name]
        args = args or []
        kwargs = kwargs or {}

        # 执行工具函数
        if asyncio.iscoroutinefunction(tool_def.func):
            result = await tool_def.func(*args, **kwargs)
        else:
            result = tool_def.func(*args, **kwargs)

        return Result(value=result)

    except Exception as e:
        return Result(error=e)

def safe_execute_tool(registry: Dict[str, Any], tool_name: str,
                     args: List[Any] = None, kwargs: Dict[str, Any] = None) -> Result:
    """安全执行工具（捕获所有异常）"""
    try:
        return execute_tool(registry, tool_name, args, kwargs)
    except Exception as e:
        registry['logger'].error(f"Tool execution failed: {tool_name}, error: {e}")
        return Result(error=e)

async def safe_execute_tool_async(registry: Dict[str, Any], tool_name: str,
                                args: List[Any] = None, kwargs: Dict[str, Any] = None) -> Result:
    """安全异步执行工具"""
    try:
        return await execute_tool_async(registry, tool_name, args, kwargs)
    except Exception as e:
        registry['logger'].error(f"Async tool execution failed: {tool_name}, error: {e}")
        return Result(error=e)

# =============================================================================
# 工具查询
# =============================================================================

def get_tool(registry: Dict[str, Any], tool_name: str) -> Optional[ToolDefinition]:
    """获取工具定义"""
    return registry['tools'].get(tool_name)

def get_tools_by_category(registry: Dict[str, Any], category: str) -> List[ToolDefinition]:
    """按分类获取工具"""
    return [tool for tool in registry['tools'].values() if tool.category == category]

def get_all_tools(registry: Dict[str, Any]) -> List[ToolDefinition]:
    """获取所有工具"""
    return list(registry['tools'].values())

def get_all_categories(registry: Dict[str, Any]) -> List[ToolCategory]:
    """获取所有分类"""
    return list(registry['categories'].values())

def search_tools(registry: Dict[str, Any], query: str, search_in: List[str] = None) -> List[ToolDefinition]:
    """搜索工具"""
    if search_in is None:
        search_in = ['name', 'description', 'tags']

    query_lower = query.lower()
    results = []

    for tool in registry['tools'].values():
        found = False

        if 'name' in search_in and query_lower in tool.name.lower():
            found = True
        elif 'description' in search_in and query_lower in tool.description.lower():
            found = True
        elif 'tags' in search_in and any(query_lower in tag.lower() for tag in tool.tags):
            found = True

        if found:
            results.append(tool)

    return results

def filter_tools(registry: Dict[str, Any], filters: Dict[str, Any]) -> List[ToolDefinition]:
    """过滤工具"""
    tools = get_all_tools(registry)

    for key, value in filters.items():
        if key == 'category':
            tools = [t for t in tools if t.category == value]
        elif key == 'tags':
            if isinstance(value, str):
                tools = [t for t in tools if value in t.tags]
            elif isinstance(value, list):
                tools = [t for t in tools if any(tag in t.tags for tag in value)]
        elif key == 'version':
            tools = [t for t in tools if t.version == value]

    return tools

# =============================================================================
# 工具批量操作
# =============================================================================

def batch_execute_tools(registry: Dict[str, Any],
                       tool_calls: List[Dict[str, Any]]) -> List[Result]:
    """批量执行工具"""
    results = []

    for call in tool_calls:
        tool_name = call.get('name')
        args = call.get('args', [])
        kwargs = call.get('kwargs', {})

        result = safe_execute_tool(registry, tool_name, args, kwargs)
        results.append(result)

    return results

async def batch_execute_tools_async(registry: Dict[str, Any],
                                   tool_calls: List[Dict[str, Any]]) -> List[Result]:
    """批量异步执行工具"""
    tasks = []

    for call in tool_calls:
        tool_name = call.get('name')
        args = call.get('args', [])
        kwargs = call.get('kwargs', {})

        task = safe_execute_tool_async(registry, tool_name, args, kwargs)
        tasks.append(task)

    return await asyncio.gather(*tasks)

def execute_tool_pipeline(registry: Dict[str, Any],
                         pipeline: List[Dict[str, Any]]) -> Result:
    """执行工具管道"""
    try:
        result = None

        for step in pipeline:
            tool_name = step.get('name')
            args = step.get('args', [])
            kwargs = step.get('kwargs', {})

            # 如果有前一步的结果，作为输入
            if result is not None and step.get('use_previous_result', False):
                if args:
                    args = [result] + list(args)
                else:
                    args = [result]

            # 执行工具
            execution_result = execute_tool(registry, tool_name, args, kwargs)

            if execution_result.is_error:
                return execution_result

            result = execution_result.value

        return Result(value=result)

    except Exception as e:
        return Result(error=e)

# =============================================================================
# 工具导出和导入
# =============================================================================

def export_tools(registry: Dict[str, Any], include_functions: bool = False) -> Dict[str, Any]:
    """导出工具注册表"""
    export_data = {
        'tools': {},
        'categories': {}
    }

    # 导出工具定义（不包含函数）
    for name, tool in registry['tools'].items():
        tool_data = tool.to_dict()
        if not include_functions:
            tool_data.pop('func', None)
        export_data['tools'][name] = tool_data

    # 导出分类
    for category_id, category in registry['categories'].items():
        export_data['categories'][category_id] = category.to_dict()

    return export_data

def import_tools(registry: Dict[str, Any], import_data: Dict[str, Any]) -> Result:
    """导入工具注册表"""
    try:
        # 导入分类
        for category_id, category_data in import_data.get('categories', {}).items():
            category = ToolCategory(**category_data)
            register_category(registry, category)

        # 注意：不能导入工具函数，只能导入元数据
        registry['logger'].info("Tools metadata imported successfully")
        return Result(value=len(import_data.get('tools', {})))

    except Exception as e:
        return Result(error=e)

# =============================================================================
# 工具统计和监控
# =============================================================================

def get_registry_stats(registry: Dict[str, Any]) -> Dict[str, Any]:
    """获取注册表统计信息"""
    tools = get_all_tools(registry)
    categories = get_all_categories(registry)

    category_stats = {}
    for category in categories:
        category_stats[category.category_id] = {
            'name': category.name,
            'tool_count': len(category.tools)
        }

    return {
        'total_tools': len(tools),
        'total_categories': len(categories),
        'category_stats': category_stats,
        'tools_by_category': {cat.category_id: len(cat.tools) for cat in categories}
    }

def validate_registry(registry: Dict[str, Any]) -> Result:
    """验证注册表完整性"""
    errors = []

    # 检查工具引用
    for tool_name, tool in registry['tools'].items():
        if tool.category not in registry['categories']:
            errors.append(f"Tool {tool_name} references unknown category: {tool.category}")

    # 检查分类引用
    for category_id, category in registry['categories'].items():
        for tool_name in category.tools:
            if tool_name not in registry['tools']:
                errors.append(f"Category {category_id} references unknown tool: {tool_name}")

    if errors:
        return Result(error=ValueError(f"Registry validation failed: {'; '.join(errors)}"))

    return Result(value=True)

# =============================================================================
# 全局注册表实例
# =============================================================================

# 创建全局注册表
_global_registry = create_tool_registry()

# 导出装饰器
tool = create_tool_decorator(_global_registry)
category = create_category_decorator(_global_registry)

# 导出常用函数
def get_global_registry() -> Dict[str, Any]:
    """获取全局工具注册表"""
    return _global_registry

def execute_global_tool(tool_name: str, *args, **kwargs) -> Result:
    """执行全局注册表中的工具"""
    return execute_tool(_global_registry, tool_name, list(args), kwargs)

async def execute_global_tool_async(tool_name: str, *args, **kwargs) -> Result:
    """异步执行全局注册表中的工具"""
    return await execute_tool_async(_global_registry, tool_name, list(args), kwargs)