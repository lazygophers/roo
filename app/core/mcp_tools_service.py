"""
MCP工具管理服务
负责管理MCP工具清单的数据库存储和更新
"""

import time
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from tinydb import TinyDB, Query

from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log

logger = setup_logging("INFO")

class MCPTool:
    """MCP工具数据模型"""
    
    def __init__(self, name: str, description: str, category: str, 
                 schema: Dict[str, Any], enabled: bool = True, 
                 implementation_type: str = "builtin", **kwargs):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.name = name
        self.description = description
        self.category = category
        self.schema = schema
        self.enabled = enabled
        self.implementation_type = implementation_type  # builtin, external, plugin
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.now().isoformat())
        self.metadata = kwargs.get('metadata', {})
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'schema': self.schema,
            'enabled': self.enabled,
            'implementation_type': self.implementation_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPTool':
        """从字典创建实例"""
        return cls(**data)

class MCPToolsService:
    """MCP工具管理服务"""
    
    def __init__(self, db_path: str = None):
        """初始化MCP工具服务"""
        if db_path is None:
            db_dir = PROJECT_ROOT / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "mcp_tools.db")
            
        self.db_path = db_path
        self.db = TinyDB(db_path)
        self.tools_table = self.db.table('mcp_tools')
        self.categories_table = self.db.table('mcp_categories')
        
        # 初始化默认分类
        self._initialize_categories()
        
        logger.info(f"MCPToolsService initialized with db: {sanitize_for_log(db_path)}")
    
    def _initialize_categories(self):
        """初始化默认工具分类"""
        default_categories = [
            {
                'id': 'system',
                'name': '系统工具',
                'description': '系统信息和监控相关工具',
                'icon': '🖥️',
                'enabled': True
            },
            {
                'id': 'time',
                'name': '时间工具', 
                'description': '时间戳和日期相关工具',
                'icon': '⏰',
                'enabled': True
            },
            {
                'id': 'ai',
                'name': 'AI工具',
                'description': 'AI模式和智能助手相关工具',
                'icon': '🤖',
                'enabled': True
            },
            {
                'id': 'dev',
                'name': '开发工具',
                'description': '开发和调试相关工具',
                'icon': '⚙️',
                'enabled': True
            },
            {
                'id': 'data',
                'name': '数据工具',
                'description': '数据处理和分析相关工具',
                'icon': '📊',
                'enabled': True
            }
        ]
        
        Query_obj = Query()
        for category in default_categories:
            existing = self.categories_table.get(Query_obj.id == category['id'])
            if not existing:
                category['created_at'] = datetime.now().isoformat()
                self.categories_table.insert(category)
                logger.info(f"Created default category: {sanitize_for_log(category['name'])}")
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """获取所有工具分类"""
        categories = self.categories_table.all()
        return [cat for cat in categories if cat.get('enabled', True)]
    
    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """获取特定分类"""
        Query_obj = Query()
        return self.categories_table.get(Query_obj.id == category_id)
    
    def register_builtin_tools(self):
        """注册内置MCP工具到数据库"""
        builtin_tools = [
            MCPTool(
                name="get_current_timestamp",
                description="获取当前时间戳，支持多种时间格式",
                category="time",
                schema={
                    "type": "object",
                    "properties": {
                        "format": {
                            "type": "string",
                            "description": "时间格式 (iso, unix, formatted)",
                            "enum": ["iso", "unix", "formatted"],
                            "default": "iso"
                        },
                        "timezone": {
                            "type": "string", 
                            "description": "时区设置",
                            "default": "local"
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["时间", "时间戳", "格式化"],
                    "examples": [
                        {"format": "iso"},
                        {"format": "unix"},
                        {"format": "formatted", "timezone": "UTC"}
                    ]
                }
            ),
            MCPTool(
                name="get_system_info",
                description="获取LazyAI Studio系统信息，包括CPU、内存、操作系统等",
                category="system",
                schema={
                    "type": "object",
                    "properties": {
                        "detailed": {
                            "type": "boolean",
                            "description": "是否返回详细信息",
                            "default": False
                        },
                        "include_performance": {
                            "type": "boolean",
                            "description": "是否包含性能统计",
                            "default": True
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
            ),
            MCPTool(
                name="list_available_modes", 
                description="列出LazyAI Studio可用的AI模式和智能助手",
                category="ai",
                schema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "description": "过滤特定分类的模式",
                            "enum": ["code", "debug", "doc", "research", "all"],
                            "default": "all"
                        },
                        "include_description": {
                            "type": "boolean",
                            "description": "是否包含详细描述",
                            "default": True
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["AI", "模式", "助手", "LazyGophers"],
                    "examples": [
                        {"category": "all"},
                        {"category": "code", "include_description": True}
                    ]
                }
            ),
            MCPTool(
                name="get_project_stats",
                description="获取项目统计信息，包括文件数量、模型数量等",
                category="data",
                schema={
                    "type": "object",
                    "properties": {
                        "include_models": {
                            "type": "boolean",
                            "description": "是否包含模型统计",
                            "default": True
                        },
                        "include_files": {
                            "type": "boolean", 
                            "description": "是否包含文件统计",
                            "default": True
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["统计", "项目", "数据"],
                    "examples": [
                        {"include_models": True, "include_files": True}
                    ]
                }
            ),
            MCPTool(
                name="health_check",
                description="执行系统健康检查，验证各组件状态",
                category="system",
                schema={
                    "type": "object",
                    "properties": {
                        "check_database": {
                            "type": "boolean",
                            "description": "是否检查数据库连接",
                            "default": True
                        },
                        "check_cache": {
                            "type": "boolean",
                            "description": "是否检查缓存系统",
                            "default": True
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["健康检查", "监控", "诊断"],
                    "examples": [
                        {"check_database": True, "check_cache": True}
                    ]
                }
            )
        ]
        
        registered_count = 0
        updated_count = 0
        
        Query_obj = Query()
        for tool in builtin_tools:
            existing = self.tools_table.get(Query_obj.name == tool.name)
            
            if existing:
                # 更新现有工具
                tool.id = existing['id']
                tool.created_at = existing['created_at']
                tool.updated_at = datetime.now().isoformat()
                
                self.tools_table.update(tool.to_dict(), Query_obj.name == tool.name)
                updated_count += 1
                logger.info(f"Updated builtin tool: {sanitize_for_log(tool.name)}")
            else:
                # 注册新工具
                self.tools_table.insert(tool.to_dict())
                registered_count += 1
                logger.info(f"Registered new builtin tool: {sanitize_for_log(tool.name)}")
        
        logger.info(f"Builtin tools registration completed: {registered_count} new, {updated_count} updated")
        return {"registered": registered_count, "updated": updated_count}
    
    def get_tools(self, category: str = None, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """获取工具清单"""
        Query_obj = Query()
        
        if category and enabled_only:
            tools = self.tools_table.search((Query_obj.category == category) & (Query_obj.enabled == True))
        elif category:
            tools = self.tools_table.search(Query_obj.category == category)
        elif enabled_only:
            tools = self.tools_table.search(Query_obj.enabled == True)
        else:
            tools = self.tools_table.all()
        
        return tools
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """根据名称获取单个工具"""
        Query_obj = Query()
        return self.tools_table.get(Query_obj.name == name)
    
    def get_tool_by_id(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """根据ID获取单个工具"""
        Query_obj = Query()
        return self.tools_table.get(Query_obj.id == tool_id)
    
    def enable_tool(self, name: str) -> bool:
        """启用工具"""
        Query_obj = Query()
        result = self.tools_table.update({'enabled': True, 'updated_at': datetime.now().isoformat()}, 
                                        Query_obj.name == name)
        if result:
            logger.info(f"Enabled tool: {sanitize_for_log(name)}")
        return len(result) > 0
    
    def disable_tool(self, name: str) -> bool:
        """禁用工具"""
        Query_obj = Query()
        result = self.tools_table.update({'enabled': False, 'updated_at': datetime.now().isoformat()}, 
                                        Query_obj.name == name)
        if result:
            logger.info(f"Disabled tool: {sanitize_for_log(name)}")
        return len(result) > 0
    
    def get_tools_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        """按分类获取工具清单"""
        categories = self.get_categories()
        tools_by_category = {}
        
        for category in categories:
            category_id = category['id']
            tools = self.get_tools(category=category_id, enabled_only=True)
            tools_by_category[category_id] = {
                'category_info': category,
                'tools': tools,
                'count': len(tools)
            }
        
        return tools_by_category
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取工具统计信息"""
        all_tools = self.tools_table.all()
        enabled_tools = [t for t in all_tools if t.get('enabled', True)]
        categories = self.get_categories()
        
        stats_by_category = {}
        for category in categories:
            category_tools = [t for t in enabled_tools if t.get('category') == category['id']]
            stats_by_category[category['id']] = {
                'name': category['name'],
                'icon': category.get('icon', '🔧'),
                'count': len(category_tools)
            }
        
        return {
            'total_tools': len(all_tools),
            'enabled_tools': len(enabled_tools),
            'disabled_tools': len(all_tools) - len(enabled_tools),
            'total_categories': len(categories),
            'by_category': stats_by_category,
            'last_updated': datetime.now().isoformat()
        }
    
    def close(self):
        """关闭数据库连接"""
        self.db.close()
        logger.info("MCPToolsService closed")


# 全局MCP工具服务实例
_mcp_tools_service = None

def get_mcp_tools_service() -> MCPToolsService:
    """获取MCP工具服务实例"""
    global _mcp_tools_service
    if _mcp_tools_service is None:
        _mcp_tools_service = MCPToolsService()
    return _mcp_tools_service

def init_mcp_tools_service() -> MCPToolsService:
    """初始化MCP工具服务"""
    logger.info("Initializing MCP tools service...")
    
    mcp_service = get_mcp_tools_service()
    
    # 注册内置工具
    result = mcp_service.register_builtin_tools()
    logger.info(f"MCP tools service initialized: {result}")
    
    return mcp_service