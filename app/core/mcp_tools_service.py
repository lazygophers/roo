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
                'sort_order': 2,
                'config': {
                    'default_timezone': 'local',
                    'display_format': 'formatted',
                    'show_timezone_info': True,
                    'auto_detect_timezone': True,
                    'precision_level': 'second',
                    'date_format_locale': 'zh_CN',
                    'enable_relative_time': False,
                    'cache_timezone_info': True,
                    'enable_business_days': False
                }
            },
            {
                'id': 'file',
                'name': '文件工具',
                'description': '文件读写、目录操作和文件管理相关工具',
                'icon': '📁',
                'enabled': True,
                'sort_order': 3
            },
            {
                'id': 'cache',
                'name': '缓存工具',
                'description': '缓存操作相关工具',
                'icon': '🗄️',
                'enabled': True,
                'sort_order': 4,
                'config': {
                    'default_ttl': 3600,  # 1小时默认TTL
                    'persistence_enabled': True,
                    'compression_enabled': False,
                    'stats_enabled': True
                }
            }
        ]
        
        registered_count = 0
        updated_count = 0
        
        Query_obj = Query()
        for category in builtin_categories:
            existing = self.categories_table.get(Query_obj.id == category['id'])
            
            if existing:
                # 覆盖现有分类（仅保留用户配置：enabled状态、created_at和用户自定义的config）
                user_enabled = existing.get('enabled', category['enabled'])
                user_created_at = existing['created_at']
                user_config = existing.get('config', {})

                # 完全覆盖内置属性
                category['created_at'] = user_created_at
                category['updated_at'] = datetime.now().isoformat()
                category['enabled'] = user_enabled

                # 合并配置：内置配置为基础，保留用户的自定义配置覆盖
                if 'config' in category:
                    # 内置配置作为基础
                    builtin_config = category['config']
                    # 用户配置覆盖内置配置（保留用户自定义）
                    merged_config = {**builtin_config, **user_config}
                    category['config'] = merged_config
                else:
                    category['config'] = user_config
                
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
    
    def get_category_config(self, category_id: str) -> Optional[Dict[str, Any]]:
        """获取分类的配置"""
        category = self.get_category(category_id)
        if category:
            return category.get('config', {})
        return None
    
    def update_category_config(self, category_id: str, config_key: str, config_value: Any) -> bool:
        """更新分类的特定配置项"""
        try:
            Query_obj = Query()
            category = self.categories_table.get(Query_obj.id == category_id)
            
            if not category:
                logger.warning(f"Category '{category_id}' not found for config update")
                return False
            
            # 确保config字段存在
            if 'config' not in category:
                category['config'] = {}
            
            # 更新配置项
            category['config'][config_key] = config_value
            category['updated_at'] = datetime.now().isoformat()
            
            # 保存到数据库
            self.categories_table.update(category, Query_obj.id == category_id)
            logger.info(f"Updated category '{category_id}' config: {config_key} = {sanitize_for_log(str(config_value))}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update category config: {sanitize_for_log(str(e))}")
            return False
    
    def update_category_configs(self, category_id: str, configs: Dict[str, Any]) -> bool:
        """批量更新分类配置"""
        try:
            Query_obj = Query()
            category = self.categories_table.get(Query_obj.id == category_id)
            
            if not category:
                logger.warning(f"Category '{category_id}' not found for config update")
                return False
            
            # 确保config字段存在
            if 'config' not in category:
                category['config'] = {}
            
            # 批量更新配置项
            category['config'].update(configs)
            category['updated_at'] = datetime.now().isoformat()
            
            # 保存到数据库
            self.categories_table.update(category, Query_obj.id == category_id)
            logger.info(f"Updated category '{category_id}' configs: {len(configs)} items")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update category configs: {sanitize_for_log(str(e))}")
            return False
    
    def register_builtin_tools(self):
        """注册内置MCP工具到数据库（启动时覆盖）"""
        builtin_tools = [
            MCPTool(
                name="get_current_timestamp",
                description="获取当前Unix时间戳（纯数字）",
                category="time",
                schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                metadata={
                    "tags": ["时间戳", "Unix", "数字"],
                    "examples": [{}]
                }
            ),
            MCPTool(
                name="format_time",
                description="格式化时间输出，支持多种格式和时区",
                category="time",
                schema={
                    "type": "object",
                    "properties": {
                        "timestamp": {
                            "type": ["number", "string"],
                            "description": "Unix时间戳或ISO格式时间字符串。如不提供则使用当前时间",
                            "default": None
                        },
                        "format": {
                            "type": "string",
                            "description": "输出格式",
                            "enum": ["iso", "formatted", "custom"],
                            "default": "formatted"
                        },
                        "custom_format": {
                            "type": "string",
                            "description": "自定义时间格式（如：%Y-%m-%d %H:%M:%S）",
                            "default": "%Y-%m-%d %H:%M:%S"
                        },
                        "timezone": {
                            "type": "string",
                            "description": "目标时区（如：UTC, Asia/Shanghai, local）。如不指定则使用全局配置",
                            "default": None
                        },
                        "include_timezone_info": {
                            "type": "boolean",
                            "description": "是否包含时区信息",
                            "default": None
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["时间格式化", "时区", "日期"],
                    "examples": [
                        {},
                        {"format": "iso"},
                        {"format": "custom", "custom_format": "%Y年%m月%d日 %H时%M分"},
                        {"timestamp": 1234567890, "timezone": "UTC"}
                    ]
                }
            ),
            MCPTool(
                name="convert_timezone",
                description="时区转换工具，将时间从一个时区转换到另一个时区",
                category="time",
                schema={
                    "type": "object",
                    "properties": {
                        "time_input": {
                            "type": "string",
                            "description": "输入的时间（支持ISO格式或Unix时间戳）",
                        },
                        "from_timezone": {
                            "type": "string",
                            "description": "源时区（如：UTC, Asia/Shanghai）",
                            "default": "local"
                        },
                        "to_timezone": {
                            "type": "string",
                            "description": "目标时区（如：UTC, Asia/Tokyo）",
                        },
                        "output_format": {
                            "type": "string",
                            "description": "输出格式",
                            "enum": ["iso", "formatted", "unix"],
                            "default": "formatted"
                        }
                    },
                    "required": ["time_input", "to_timezone"]
                },
                metadata={
                    "tags": ["时区转换", "国际化", "时间"],
                    "examples": [
                        {"time_input": "2023-12-25 15:30:00", "from_timezone": "Asia/Shanghai", "to_timezone": "UTC"},
                        {"time_input": "1703574600", "from_timezone": "UTC", "to_timezone": "America/New_York"}
                    ]
                }
            ),
            MCPTool(
                name="parse_time",
                description="解析和标准化时间字符串，支持多种格式识别",
                category="time",
                schema={
                    "type": "object",
                    "properties": {
                        "time_string": {
                            "type": "string",
                            "description": "要解析的时间字符串"
                        },
                        "input_format": {
                            "type": "string",
                            "description": "输入格式提示（如：%Y-%m-%d %H:%M:%S）。留空自动识别",
                            "default": None
                        },
                        "timezone": {
                            "type": "string",
                            "description": "输入时间的时区（如未指定则假设为本地时区）",
                            "default": "local"
                        },
                        "output_timezone": {
                            "type": "string",
                            "description": "输出时区（转换后的时区）",
                            "default": None
                        }
                    },
                    "required": ["time_string"]
                },
                metadata={
                    "tags": ["时间解析", "格式识别", "标准化"],
                    "examples": [
                        {"time_string": "2023-12-25 15:30:00"},
                        {"time_string": "Dec 25, 2023 3:30 PM"},
                        {"time_string": "25/12/2023 15:30", "input_format": "%d/%m/%Y %H:%M"}
                    ]
                }
            ),
            MCPTool(
                name="calculate_time_diff",
                description="计算两个时间之间的差值",
                category="time",
                schema={
                    "type": "object",
                    "properties": {
                        "start_time": {
                            "type": "string",
                            "description": "开始时间（Unix时间戳或ISO格式）"
                        },
                        "end_time": {
                            "type": "string",
                            "description": "结束时间（Unix时间戳或ISO格式）。如不提供则使用当前时间",
                            "default": None
                        },
                        "unit": {
                            "type": "string",
                            "description": "输出单位",
                            "enum": ["seconds", "minutes", "hours", "days", "weeks", "months", "years", "auto"],
                            "default": "auto"
                        },
                        "precision": {
                            "type": "integer",
                            "description": "小数点精度",
                            "default": 2,
                            "minimum": 0,
                            "maximum": 6
                        },
                        "human_readable": {
                            "type": "boolean",
                            "description": "是否输出人类可读的格式（如：2天3小时30分钟）",
                            "default": True
                        }
                    },
                    "required": ["start_time"]
                },
                metadata={
                    "tags": ["时间差", "持续时间", "计算"],
                    "examples": [
                        {"start_time": "2023-12-25 10:00:00"},
                        {"start_time": "1703573400", "end_time": "1703659800", "unit": "hours"},
                        {"start_time": "2023-01-01", "end_time": "2023-12-31", "unit": "days"}
                    ]
                }
            ),
            MCPTool(
                name="get_timezone_info",
                description="获取时区信息，包括当前时间、UTC偏移等",
                category="time",
                schema={
                    "type": "object",
                    "properties": {
                        "timezone": {
                            "type": "string",
                            "description": "时区名称（如：Asia/Shanghai, UTC）",
                            "default": "local"
                        },
                        "include_dst_info": {
                            "type": "boolean",
                            "description": "是否包含夏令时信息",
                            "default": True
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["时区信息", "UTC偏移", "夏令时"],
                    "examples": [
                        {},
                        {"timezone": "Asia/Shanghai"},
                        {"timezone": "America/New_York", "include_dst_info": True}
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
            ),
            # 缓存工具
            MCPTool(
                name="cache_set",
                description="设置缓存键值对，支持TTL过期时间",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "缓存键名"
                        },
                        "value": {
                            "description": "缓存值（支持任意类型）"
                        },
                        "ttl": {
                            "type": "integer",
                            "description": "生存时间（秒），不指定则使用默认值",
                            "minimum": 1
                        },
                        "tags": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表，用于批量操作"
                        }
                    },
                    "required": ["key", "value"]
                },
                metadata={
                    "tags": ["缓存", "SET", "存储"],
                    "examples": [
                        {"key": "user:123", "value": "Alice"},
                        {"key": "session", "value": {"user_id": 123, "token": "abc"}, "ttl": 3600}
                    ]
                }
            ),
            MCPTool(
                name="cache_get",
                description="获取缓存值",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "缓存键名"
                        }
                    },
                    "required": ["key"]
                },
                metadata={
                    "tags": ["缓存", "GET", "读取"],
                    "examples": [
                        {"key": "user:123"},
                        {"key": "session"}
                    ]
                }
            ),
            MCPTool(
                name="cache_delete",
                description="删除缓存键",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "要删除的缓存键名"
                        }
                    },
                    "required": ["key"]
                },
                metadata={
                    "tags": ["缓存", "DEL", "删除"],
                    "examples": [
                        {"key": "user:123"}
                    ]
                }
            ),
            MCPTool(
                name="cache_exists",
                description="检查缓存键是否存在",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "要检查的缓存键名"
                        }
                    },
                    "required": ["key"]
                },
                metadata={
                    "tags": ["缓存", "EXISTS", "检查"],
                    "examples": [
                        {"key": "user:123"}
                    ]
                }
            ),
            MCPTool(
                name="cache_ttl",
                description="获取缓存键的剩余生存时间",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "缓存键名"
                        }
                    },
                    "required": ["key"]
                },
                metadata={
                    "tags": ["缓存", "TTL", "过期"],
                    "examples": [
                        {"key": "user:123"}
                    ]
                }
            ),
            MCPTool(
                name="cache_expire",
                description="设置缓存键的过期时间",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "缓存键名"
                        },
                        "ttl": {
                            "type": "integer",
                            "description": "生存时间（秒）",
                            "minimum": 1
                        }
                    },
                    "required": ["key", "ttl"]
                },
                metadata={
                    "tags": ["缓存", "EXPIRE", "设置过期"],
                    "examples": [
                        {"key": "user:123", "ttl": 3600}
                    ]
                }
            ),
            MCPTool(
                name="cache_keys",
                description="查找匹配模式的缓存键",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "pattern": {
                            "type": "string",
                            "description": "匹配模式，支持*通配符",
                            "default": "*"
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["缓存", "KEYS", "查找"],
                    "examples": [
                        {},
                        {"pattern": "user:*"},
                        {"pattern": "session:*"}
                    ]
                }
            ),
            MCPTool(
                name="cache_mset",
                description="批量设置多个缓存键值对",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key_values": {
                            "type": "object",
                            "description": "键值对字典"
                        },
                        "ttl": {
                            "type": "integer",
                            "description": "统一的生存时间（秒）",
                            "minimum": 1
                        }
                    },
                    "required": ["key_values"]
                },
                metadata={
                    "tags": ["缓存", "MSET", "批量设置", "批量"],
                    "examples": [
                        {"key_values": {"user:1": "Alice", "user:2": "Bob"}},
                        {"key_values": {"temp:1": "data1", "temp:2": "data2"}, "ttl": 300}
                    ]
                }
            ),
            MCPTool(
                name="cache_mget",
                description="批量获取多个缓存键的值",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "keys": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "要获取的键列表"
                        }
                    },
                    "required": ["keys"]
                },
                metadata={
                    "tags": ["缓存", "MGET", "批量获取", "批量"],
                    "examples": [
                        {"keys": ["user:1", "user:2", "user:3"]}
                    ]
                }
            ),
            MCPTool(
                name="cache_incr",
                description="原子性递增数值型缓存值",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": "缓存键名"
                        },
                        "amount": {
                            "type": "integer",
                            "description": "递增量",
                            "default": 1
                        }
                    },
                    "required": ["key"]
                },
                metadata={
                    "tags": ["缓存", "INCR", "递增", "计数器"],
                    "examples": [
                        {"key": "counter"},
                        {"key": "visits", "amount": 5}
                    ]
                }
            ),
            MCPTool(
                name="cache_info",
                description="获取缓存系统信息和统计",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                metadata={
                    "tags": ["缓存", "INFO", "信息", "统计"],
                    "examples": [{}]
                }
            ),
            MCPTool(
                name="cache_flushall",
                description="清空所有缓存数据",
                category="cache",
                schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                metadata={
                    "tags": ["缓存", "FLUSHALL", "清空", "删除全部"],
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
                # 覆盖现有工具（仅保留用户配置：enabled状态和created_at）
                user_enabled = existing.get('enabled', tool.enabled)
                user_created_at = existing['created_at']

                # 完全覆盖所有内置属性（description、schema、metadata等）
                tool.id = existing['id']
                tool.created_at = user_created_at
                tool.updated_at = datetime.now().isoformat()
                tool.enabled = user_enabled
                
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
    
    def create_category(self, category_data: Dict[str, Any]) -> bool:
        """创建新的工具分类"""
        try:
            # 检查分类ID是否已存在
            Query_obj = Query()
            existing = self.categories_table.get(Query_obj.id == category_data['id'])
            if existing:
                logger.warning(f"Category with ID '{sanitize_for_log(category_data['id'])}' already exists")
                return False
            
            # 设置默认值
            category = {
                'id': category_data['id'],
                'name': category_data['name'],
                'description': category_data.get('description', ''),
                'icon': category_data.get('icon', '🔧'),
                'enabled': category_data.get('enabled', True),
                'sort_order': category_data.get('sort_order', 999),
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat()
            }
            
            self.categories_table.insert(category)
            logger.info(f"Created new category: {sanitize_for_log(category['name'])}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create category: {sanitize_for_log(str(e))}")
            return False
    
    def update_category(self, category_id: str, updates: Dict[str, Any]) -> bool:
        """更新工具分类"""
        try:
            Query_obj = Query()
            existing = self.categories_table.get(Query_obj.id == category_id)
            if not existing:
                logger.warning(f"Category with ID '{sanitize_for_log(category_id)}' not found")
                return False
            
            # 准备更新数据
            update_data = {}
            allowed_fields = ['name', 'description', 'icon', 'enabled', 'sort_order']
            
            for field in allowed_fields:
                if field in updates:
                    update_data[field] = updates[field]
            
            if update_data:
                update_data['updated_at'] = datetime.now().isoformat()
                self.categories_table.update(update_data, Query_obj.id == category_id)
                logger.info(f"Updated category: {sanitize_for_log(category_id)}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update category: {sanitize_for_log(str(e))}")
            return False
    
    def delete_category(self, category_id: str, force: bool = False) -> bool:
        """删除工具分类（需要检查是否有关联的工具）"""
        try:
            Query_obj = Query()
            
            # 检查分类是否存在
            existing = self.categories_table.get(Query_obj.id == category_id)
            if not existing:
                logger.warning(f"Category with ID '{sanitize_for_log(category_id)}' not found")
                return False
            
            # 检查是否有关联的工具
            if not force:
                tools_in_category = self.tools_table.search(Query_obj.category == category_id)
                if tools_in_category:
                    logger.warning(f"Cannot delete category '{sanitize_for_log(category_id)}': {len(tools_in_category)} tools still in this category")
                    return False
            
            # 删除分类
            self.categories_table.remove(Query_obj.id == category_id)
            
            # 如果强制删除，也删除分类下的所有工具
            if force:
                deleted_tools = self.tools_table.remove(Query_obj.category == category_id)
                logger.info(f"Force deleted category '{sanitize_for_log(category_id)}' and {len(deleted_tools)} associated tools")
            else:
                logger.info(f"Deleted category: {sanitize_for_log(category_id)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete category: {sanitize_for_log(str(e))}")
            return False
    
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