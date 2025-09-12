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
from app.core.unified_database import get_unified_database, TableNames

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
    
    def __init__(self, use_unified_db: bool = True):
        """初始化MCP工具服务"""
        self.use_unified_db = use_unified_db
        
        if use_unified_db:
            self.unified_db = get_unified_database()
            self.db = self.unified_db.db
            self.db_path = self.unified_db.db_path
        else:
            # 兼容模式：使用独立数据库文件
            db_dir = PROJECT_ROOT / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "mcp_tools.db")
            self.db_path = db_path
            self.db = TinyDB(db_path)
            self.unified_db = None
        
        # 使用统一表名
        self.tools_table = self.db.table(TableNames.MCP_TOOLS)
        self.categories_table = self.db.table(TableNames.MCP_CATEGORIES)
        
        logger.info(f"MCPToolsService initialized with unified db: {use_unified_db}")
    
    def register_builtin_categories(self):
        """注册内置工具分类到数据库（启动时覆盖）"""
        builtin_categories = [
            {
                'id': 'system',
                'name': '系统工具',
                'description': '系统信息和监控相关工具',
                'icon': '🖥️',
                'enabled': True,
                'sort_order': 1
            },
            {
                'id': 'time',
                'name': '时间工具', 
                'description': '时间戳和日期相关工具',
                'icon': '⏰',
                'enabled': True,
                'sort_order': 2
            },
            {
                'id': 'ai',
                'name': 'AI工具',
                'description': 'AI模式和智能助手相关工具',
                'icon': '🤖',
                'enabled': False,  # 默认禁用，因为没有工具
                'sort_order': 3
            },
            {
                'id': 'dev',
                'name': '开发工具',
                'description': '开发和调试相关工具',
                'icon': '⚙️',
                'enabled': False,  # 默认禁用，因为没有工具
                'sort_order': 4
            },
            {
                'id': 'data',
                'name': '数据工具',
                'description': '数据处理和分析相关工具',
                'icon': '📊',
                'enabled': False,  # 默认禁用，因为没有工具
                'sort_order': 5
            },
            {
                'id': 'file',
                'name': '文件工具',
                'description': '文件读写、目录操作和文件管理相关工具',
                'icon': '📁',
                'enabled': True,  # 启用文件工具分类
                'sort_order': 6
            }
        ]
        
        registered_count = 0
        updated_count = 0
        
        Query_obj = Query()
        for category in builtin_categories:
            existing = self.categories_table.get(Query_obj.id == category['id'])
            
            if existing:
                # 覆盖现有分类（保留enabled状态和created_at）
                category['enabled'] = existing.get('enabled', category['enabled'])
                category['created_at'] = existing['created_at']
                category['updated_at'] = datetime.now().isoformat()
                
                self.categories_table.update(category, Query_obj.id == category['id'])
                updated_count += 1
                logger.info(f"Updated builtin category: {sanitize_for_log(category['name'])}")
            else:
                # 注册新分类
                category['created_at'] = datetime.now().isoformat()
                category['updated_at'] = datetime.now().isoformat()
                self.categories_table.insert(category)
                registered_count += 1
                logger.info(f"Registered new builtin category: {sanitize_for_log(category['name'])}")
        
        logger.info(f"Builtin categories registration completed: {registered_count} new, {updated_count} updated")
        return {"registered": registered_count, "updated": updated_count}
    
    def get_categories(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """获取工具分类"""
        categories = self.categories_table.all()
        if enabled_only:
            categories = [cat for cat in categories if cat.get('enabled', True)]
        
        # 按sort_order排序
        return sorted(categories, key=lambda x: x.get('sort_order', 999))
    
    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """获取特定分类"""
        Query_obj = Query()
        return self.categories_table.get(Query_obj.id == category_id)
    
    def register_builtin_tools(self):
        """注册内置MCP工具到数据库（启动时覆盖）"""
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
                name="read_file",
                description="读取指定路径的文件内容",
                category="file",
                schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "要读取的文件路径（相对或绝对路径）"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "文件编码格式",
                            "default": "utf-8",
                            "enum": ["utf-8", "gbk", "ascii", "latin1"]
                        },
                        "max_lines": {
                            "type": "integer",
                            "description": "最大读取行数，0表示读取全部",
                            "default": 0,
                            "minimum": 0
                        }
                    },
                    "required": ["file_path"]
                },
                metadata={
                    "tags": ["文件", "读取", "内容"],
                    "examples": [
                        {"file_path": "config.yaml"},
                        {"file_path": "/etc/hosts", "encoding": "utf-8"},
                        {"file_path": "large_file.txt", "max_lines": 100}
                    ]
                }
            ),
            MCPTool(
                name="write_file",
                description="写入内容到指定路径的文件",
                category="file",
                schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "要写入的文件路径（相对或绝对路径）"
                        },
                        "content": {
                            "type": "string",
                            "description": "要写入的文件内容"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "文件编码格式",
                            "default": "utf-8",
                            "enum": ["utf-8", "gbk", "ascii", "latin1"]
                        },
                        "mode": {
                            "type": "string",
                            "description": "写入模式",
                            "default": "write",
                            "enum": ["write", "append"]
                        }
                    },
                    "required": ["file_path", "content"]
                },
                metadata={
                    "tags": ["文件", "写入", "创建"],
                    "examples": [
                        {"file_path": "output.txt", "content": "Hello World"},
                        {"file_path": "log.txt", "content": "New entry\\n", "mode": "append"}
                    ]
                }
            ),
            MCPTool(
                name="list_directory",
                description="列出指定目录下的文件和子目录",
                category="file",
                schema={
                    "type": "object",
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "要列出的目录路径",
                            "default": "."
                        },
                        "show_hidden": {
                            "type": "boolean",
                            "description": "是否显示隐藏文件（以.开头的文件）",
                            "default": False
                        },
                        "recursive": {
                            "type": "boolean", 
                            "description": "是否递归列出子目录",
                            "default": False
                        },
                        "file_info": {
                            "type": "boolean",
                            "description": "是否显示文件详细信息（大小、修改时间等）",
                            "default": True
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["目录", "文件列表", "浏览"],
                    "examples": [
                        {"directory_path": "."},
                        {"directory_path": "/home/user", "show_hidden": True},
                        {"directory_path": "src", "recursive": True, "file_info": True}
                    ]
                }
            ),
            MCPTool(
                name="create_directory",
                description="创建新目录（支持创建多级目录）",
                category="file",
                schema={
                    "type": "object",
                    "properties": {
                        "directory_path": {
                            "type": "string",
                            "description": "要创建的目录路径"
                        },
                        "parents": {
                            "type": "boolean",
                            "description": "是否创建父目录（类似mkdir -p）",
                            "default": True
                        }
                    },
                    "required": ["directory_path"]
                },
                metadata={
                    "tags": ["目录", "创建", "文件夹"],
                    "examples": [
                        {"directory_path": "new_folder"},
                        {"directory_path": "path/to/deep/folder", "parents": True}
                    ]
                }
            ),
            MCPTool(
                name="delete_file",
                description="删除指定的文件或空目录",
                category="file",
                schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "要删除的文件或目录路径"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "是否强制删除（删除非空目录）",
                            "default": False
                        }
                    },
                    "required": ["file_path"]
                },
                metadata={
                    "tags": ["删除", "文件", "目录"],
                    "examples": [
                        {"file_path": "temp.txt"},
                        {"file_path": "temp_folder", "force": True}
                    ]
                }
            ),
            MCPTool(
                name="file_info",
                description="获取文件或目录的详细信息",
                category="file",
                schema={
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "要查询的文件或目录路径"
                        },
                        "checksum": {
                            "type": "boolean",
                            "description": "是否计算文件校验和（仅对文件有效）",
                            "default": False
                        }
                    },
                    "required": ["file_path"]
                },
                metadata={
                    "tags": ["文件信息", "属性", "状态"],
                    "examples": [
                        {"file_path": "document.pdf"},
                        {"file_path": "important.txt", "checksum": True}
                    ]
                }
            ),
            MCPTool(
                name="get_file_security_info",
                description="获取文件工具安全配置信息，包括可访问的目录权限设置",
                category="system",
                schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                metadata={
                    "tags": ["安全", "配置", "权限", "文件系统"],
                    "examples": [{}]
                }
            ),
            MCPTool(
                name="update_file_security_paths",
                description="更新文件安全路径配置（可读取、可写入、可删除、禁止访问目录）",
                category="system", 
                schema={
                    "type": "object",
                    "properties": {
                        "config_type": {
                            "type": "string",
                            "description": "配置类型",
                            "enum": ["readable", "writable", "deletable", "forbidden"]
                        },
                        "paths": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "路径列表"
                        }
                    },
                    "required": ["config_type", "paths"]
                },
                metadata={
                    "tags": ["安全", "配置", "权限", "目录管理"],
                    "examples": [
                        {"config_type": "readable", "paths": ["/home/user", "/tmp"]},
                        {"config_type": "forbidden", "paths": ["/etc", "/bin"]}
                    ]
                }
            ),
            MCPTool(
                name="update_file_security_limits", 
                description="更新文件安全限制配置（最大文件大小、最大读取行数、严格模式）",
                category="system",
                schema={
                    "type": "object", 
                    "properties": {
                        "limit_type": {
                            "type": "string",
                            "description": "限制类型",
                            "enum": ["max_file_size", "max_read_lines", "strict_mode"]
                        },
                        "value": {
                            "description": "限制值（文件大小为字节数，行数为整数，严格模式为布尔值）"
                        }
                    },
                    "required": ["limit_type", "value"]
                },
                metadata={
                    "tags": ["安全", "配置", "限制", "参数设置"],
                    "examples": [
                        {"limit_type": "max_file_size", "value": 104857600},
                        {"limit_type": "max_read_lines", "value": 5000},
                        {"limit_type": "strict_mode", "value": True}
                    ]
                }
            ),
            MCPTool(
                name="reload_file_security_config",
                description="重新加载文件安全配置（从数据库刷新内存中的配置）",
                category="system",
                schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                metadata={
                    "tags": ["安全", "配置", "刷新", "重载"],
                    "examples": [{}]
                }
            )
        ]
        
        registered_count = 0
        updated_count = 0
        
        Query_obj = Query()
        for tool in builtin_tools:
            existing = self.tools_table.get(Query_obj.name == tool.name)
            
            if existing:
                # 覆盖现有工具（保留enabled状态和created_at）
                tool.id = existing['id']
                tool.enabled = existing.get('enabled', tool.enabled)
                tool.created_at = existing['created_at']
                tool.updated_at = datetime.now().isoformat()
                
                self.tools_table.update(tool.to_dict(), Query_obj.name == tool.name)
                updated_count += 1
                logger.info(f"Updated builtin tool: {sanitize_for_log(tool.name)}")
            else:
                # 注册新工具
                tool.created_at = datetime.now().isoformat()
                tool.updated_at = datetime.now().isoformat()
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
    
    def remove_tool(self, name: str) -> bool:
        """从数据库中删除工具"""
        Query_obj = Query()
        result = self.tools_table.remove(Query_obj.name == name)
        if result:
            logger.info(f"Removed tool: {sanitize_for_log(name)}")
        return len(result) > 0
    
    def enable_category(self, category_id: str) -> bool:
        """启用工具分类"""
        Query_obj = Query()
        result = self.categories_table.update({'enabled': True, 'updated_at': datetime.now().isoformat()}, 
                                            Query_obj.id == category_id)
        if result:
            logger.info(f"Enabled category: {sanitize_for_log(category_id)}")
        return len(result) > 0
    
    def disable_category(self, category_id: str) -> bool:
        """禁用工具分类"""
        Query_obj = Query()
        result = self.categories_table.update({'enabled': False, 'updated_at': datetime.now().isoformat()}, 
                                            Query_obj.id == category_id)
        if result:
            logger.info(f"Disabled category: {sanitize_for_log(category_id)}")
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
        if not self.use_unified_db:
            # 只有非统一数据库模式才需要手动关闭
            self.db.close()
        logger.info("MCPToolsService closed")


# 全局MCP工具服务实例
_mcp_tools_service = None

def get_mcp_tools_service(use_unified_db: bool = True) -> MCPToolsService:
    """获取MCP工具服务实例"""
    global _mcp_tools_service
    if _mcp_tools_service is None:
        _mcp_tools_service = MCPToolsService(use_unified_db=use_unified_db)
    return _mcp_tools_service

def init_mcp_tools_service(use_unified_db: bool = True) -> MCPToolsService:
    """初始化MCP工具服务"""
    logger.info("Initializing MCP tools service...")
    
    mcp_service = get_mcp_tools_service(use_unified_db=use_unified_db)
    
    # 注册内置分类
    categories_result = mcp_service.register_builtin_categories()
    logger.info(f"MCP categories registered: {categories_result}")
    
    # 注册内置工具
    tools_result = mcp_service.register_builtin_tools()
    logger.info(f"MCP tools registered: {tools_result}")
    
    logger.info(f"MCP tools service initialized successfully (unified_db: {use_unified_db})")
    return mcp_service