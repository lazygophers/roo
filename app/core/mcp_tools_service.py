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

        # 启动时自动清理数据库中的旧工具名称
        self._cleanup_legacy_tools()
        
        logger.info(f"MCPToolsService initialized with unified db: {use_unified_db}")

    def _cleanup_legacy_tools(self):
        """清理数据库中的旧工具名称和重复注册"""
        try:
            # 删除所有git_前缀的工具（它们应该是github_前缀）
            git_tools_count = 0
            all_tools = self.tools_table.all()

            for tool in all_tools:
                if tool['name'].startswith('git_'):
                    self.tools_table.remove(doc_ids=[tool.doc_id])
                    git_tools_count += 1

            if git_tools_count > 0:
                logger.info(f"Cleaned up {git_tools_count} legacy git_ prefixed tools")

            # 清理重复的工具名称，只保留最新的
            tool_names = {}
            duplicates_count = 0

            for tool in self.tools_table.all():
                name = tool['name']
                if name in tool_names:
                    # 保留更新时间较新的
                    existing_tool = tool_names[name]
                    existing_time = existing_tool.get('updated_at', '')
                    current_time = tool.get('updated_at', '')

                    if current_time > existing_time:
                        # 当前工具更新，删除旧的
                        self.tools_table.remove(doc_ids=[existing_tool['doc_id']])
                        tool_names[name] = tool
                        duplicates_count += 1
                    else:
                        # 旧工具更新，删除当前的
                        self.tools_table.remove(doc_ids=[tool.doc_id])
                        duplicates_count += 1
                else:
                    tool_names[name] = tool

            if duplicates_count > 0:
                logger.info(f"Cleaned up {duplicates_count} duplicate tool registrations")

        except Exception as e:
            logger.error(f"Error during legacy tools cleanup: {e}")

    def register_builtin_categories(self):
        """注册内置工具分类到数据库（启动时覆盖）"""
        builtin_categories = [
            {
                'id': 'system',
                'name': '系统工具',
                'description': '系统信息和监控相关工具',
                'icon': '🖥️',
                'enabled': True,
                'sort_order': 1,
                'config': {
                    'enable_system_info': True,
                    'show_detailed_info': False,
                    'include_network_info': True,
                    'include_disk_info': True,
                    'include_process_info': False,
                    'refresh_interval': 5,  # 秒
                    'enable_monitoring': True,
                    'alert_thresholds': {
                        'cpu_usage': 80,  # 百分比
                        'memory_usage': 85,  # 百分比
                        'disk_usage': 90   # 百分比
                    }
                }
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
                'sort_order': 3,
                'config': {
                    'allowed_paths': [],  # 空数组表示允许所有路径
                    'blocked_paths': ['/etc/passwd', '/etc/shadow'],  # 安全敏感路径
                    'max_file_size': 10485760,  # 10MB
                    'enable_backup': True,
                    'backup_suffix': '.bak',
                    'enable_encryption': False,
                    'encoding': 'utf-8',
                    'line_endings': 'auto',  # auto, lf, crlf
                    'enable_file_watching': False,
                    'watch_recursive': False,
                    'ignore_patterns': ['.git', '__pycache__', '*.pyc', '.DS_Store']
                }
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
            },
            {
                'id': 'github',
                'name': 'GitHub',
                'description': 'GitHub REST API 工具集，支持仓库、问题、拉取请求等操作',
                'icon': '🐙',
                'enabled': True,
                'sort_order': 5,
                'config': {
                    'base_url': 'https://api.github.com',
                    'default_per_page': 30,
                    'enable_rate_limit_handling': True,
                    'request_timeout': 30,
                    'auth_required': True,
                    'supported_auth_types': ['token', 'app']
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
                name="time_get_ts",
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
                name="time_format",
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
                name="time_convert_tz",
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
                name="time_parse",
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
                name="time_calc_diff",
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
                name="time_get_tz",
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
                name="sys_get_info",
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
                name="file_read",
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
                name="file_write",
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
                name="file_ls_dir",
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
                name="file_new_dir",
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
                name="file_del",
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
                name="file_get_info",
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
                name="sys_get_security",
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
                name="sys_set_security_paths",
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
                name="sys_set_security_limits", 
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
                name="sys_reload_security",
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
                name="cache_del",
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
                name="cache_get_ttl",
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
                name="cache_set_ttl",
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
                name="cache_ls_keys",
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
                name="cache_set_multi",
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
                name="cache_get_multi",
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
                name="cache_get_info",
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
                name="cache_flush_all",
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
            ),
            # ============ GitHub API 工具 ============
            MCPTool(
                name="github_get_repo",
                description="获取 GitHub 仓库信息",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者（用户名或组织名）"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "仓库", "信息", "查询"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World"},
                        {"owner": "microsoft", "repo": "vscode"}
                    ]
                }
            ),
            MCPTool(
                name="github_ls_repos",
                description="列出用户或组织的仓库",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "description": "仓库类型",
                            "enum": ["all", "owner", "public", "private", "member"],
                            "default": "owner"
                        },
                        "sort": {
                            "type": "string",
                            "description": "排序方式",
                            "enum": ["created", "updated", "pushed", "full_name"],
                            "default": "updated"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["GitHub", "仓库", "列表", "分页"],
                    "examples": [
                        {"type": "owner", "sort": "updated"},
                        {"type": "public", "per_page": 10, "page": 2}
                    ]
                }
            ),
            MCPTool(
                name="github_new_repo",
                description="创建新的 GitHub 仓库",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "description": {
                            "type": "string",
                            "description": "仓库描述",
                            "default": ""
                        },
                        "private": {
                            "type": "boolean",
                            "description": "是否为私有仓库",
                            "default": False
                        },
                        "has_issues": {
                            "type": "boolean",
                            "description": "是否启用问题跟踪",
                            "default": True
                        },
                        "has_projects": {
                            "type": "boolean",
                            "description": "是否启用项目",
                            "default": True
                        },
                        "has_wiki": {
                            "type": "boolean",
                            "description": "是否启用 Wiki",
                            "default": True
                        },
                        "auto_init": {
                            "type": "boolean",
                            "description": "是否自动初始化（创建 README）",
                            "default": False
                        }
                    },
                    "required": ["name"]
                },
                metadata={
                    "tags": ["GitHub", "仓库", "创建", "初始化"],
                    "examples": [
                        {"name": "my-new-project", "description": "A new project", "private": True},
                        {"name": "demo", "auto_init": True, "has_wiki": False}
                    ]
                }
            ),
            MCPTool(
                name="github_ls_issues",
                description="列出仓库的问题（Issues）",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "state": {
                            "type": "string",
                            "description": "问题状态",
                            "enum": ["open", "closed", "all"],
                            "default": "open"
                        },
                        "labels": {
                            "type": "string",
                            "description": "标签过滤（逗号分隔）",
                            "default": ""
                        },
                        "sort": {
                            "type": "string",
                            "description": "排序方式",
                            "enum": ["created", "updated", "comments"],
                            "default": "created"
                        },
                        "direction": {
                            "type": "string",
                            "description": "排序方向",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "问题", "Issues", "列表"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "state": "open"},
                        {"owner": "microsoft", "repo": "vscode", "labels": "bug,help wanted"}
                    ]
                }
            ),
            MCPTool(
                name="github_get_issue",
                description="获取特定的问题详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                metadata={
                    "tags": ["GitHub", "问题", "详情", "查询"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "issue_number": 1}
                    ]
                }
            ),
            MCPTool(
                name="github_new_issue",
                description="创建新的问题（Issue）",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "title": {
                            "type": "string",
                            "description": "问题标题"
                        },
                        "body": {
                            "type": "string",
                            "description": "问题描述",
                            "default": ""
                        },
                        "assignees": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "指派人列表"
                        },
                        "labels": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "标签列表"
                        },
                        "milestone": {
                            "type": "integer",
                            "description": "里程碑编号"
                        }
                    },
                    "required": ["owner", "repo", "title"]
                },
                metadata={
                    "tags": ["GitHub", "问题", "创建", "Issues"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "title": "Bug report", "body": "Found a bug..."},
                        {"owner": "user", "repo": "project", "title": "Feature request", "labels": ["enhancement"]}
                    ]
                }
            ),
            MCPTool(
                name="github_ls_prs",
                description="列出拉取请求（Pull Requests）",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "state": {
                            "type": "string",
                            "description": "PR 状态",
                            "enum": ["open", "closed", "all"],
                            "default": "open"
                        },
                        "head": {
                            "type": "string",
                            "description": "源分支（user:branch格式）",
                            "default": ""
                        },
                        "base": {
                            "type": "string",
                            "description": "目标分支",
                            "default": ""
                        },
                        "sort": {
                            "type": "string",
                            "description": "排序方式",
                            "enum": ["created", "updated", "popularity", "long-running"],
                            "default": "created"
                        },
                        "direction": {
                            "type": "string",
                            "description": "排序方向",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "拉取请求", "PR", "列表"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "state": "open"},
                        {"owner": "microsoft", "repo": "vscode", "base": "main"}
                    ]
                }
            ),
            MCPTool(
                name="github_get_pr",
                description="获取特定拉取请求的详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "pull_number": {
                            "type": "integer",
                            "description": "拉取请求编号",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "pull_number"]
                },
                metadata={
                    "tags": ["GitHub", "拉取请求", "详情", "PR"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "pull_number": 1}
                    ]
                }
            ),
            MCPTool(
                name="github_new_pr",
                description="创建新的拉取请求",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "title": {
                            "type": "string",
                            "description": "拉取请求标题"
                        },
                        "head": {
                            "type": "string",
                            "description": "源分支（user:branch 格式）"
                        },
                        "base": {
                            "type": "string",
                            "description": "目标分支"
                        },
                        "body": {
                            "type": "string",
                            "description": "拉取请求描述",
                            "default": ""
                        },
                        "maintainer_can_modify": {
                            "type": "boolean",
                            "description": "是否允许维护者修改",
                            "default": True
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "是否为草稿状态",
                            "default": False
                        }
                    },
                    "required": ["owner", "repo", "title", "head", "base"]
                },
                metadata={
                    "tags": ["GitHub", "拉取请求", "创建", "PR"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "title": "Add new feature", "head": "octocat:feature", "base": "main"},
                        {"owner": "user", "repo": "project", "title": "Fix bug", "head": "user:bugfix", "base": "develop", "draft": True}
                    ]
                }
            ),
            MCPTool(
                name="github_search_repos",
                description="搜索 GitHub 仓库",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "q": {
                            "type": "string",
                            "description": "搜索查询字符串"
                        },
                        "sort": {
                            "type": "string",
                            "description": "排序方式",
                            "enum": ["stars", "forks", "updated"],
                            "default": "updated"
                        },
                        "order": {
                            "type": "string",
                            "description": "排序方向",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["q"]
                },
                metadata={
                    "tags": ["GitHub", "搜索", "仓库", "查询"],
                    "examples": [
                        {"q": "machine learning language:python"},
                        {"q": "react hooks", "sort": "stars", "order": "desc"}
                    ]
                }
            ),
            MCPTool(
                name="github_get_user",
                description="获取 GitHub 用户信息",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "username": {
                            "type": "string",
                            "description": "GitHub 用户名（为空则获取当前认证用户信息）",
                            "default": ""
                        }
                    },
                    "required": []
                },
                metadata={
                    "tags": ["GitHub", "用户", "信息", "个人资料"],
                    "examples": [
                        {"username": "octocat"},
                        {}
                    ]
                }
            ),
            MCPTool(
                name="github_ls_branches",
                description="列出仓库分支",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "protected": {
                            "type": "boolean",
                            "description": "是否只显示受保护分支"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "分支", "列表", "版本控制"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World"},
                        {"owner": "microsoft", "repo": "vscode", "protected": True}
                    ]
                }
            ),
            MCPTool(
                name="github_get_rate_limit",
                description="获取 GitHub API 速率限制信息",
                category="github",
                schema={
                    "type": "object",
                    "properties": {},
                    "required": []
                },
                metadata={
                    "tags": ["GitHub", "速率限制", "API", "配额"],
                    "examples": [{}]
                }
            ),

            # ============ GitHub 仓库内容工具 ============
            MCPTool(
                name="github_get_contents",
                description="获取 GitHub 仓库内容（文件或目录）",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "path": {
                            "type": "string",
                            "description": "文件或目录路径（空字符串表示根目录）",
                            "default": ""
                        },
                        "ref": {
                            "type": "string",
                            "description": "Git 引用（分支名、标签或提交 SHA），默认为默认分支",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "仓库内容", "文件", "目录"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "path": "", "ref": ""},
                        {"owner": "microsoft", "repo": "vscode", "path": "src", "ref": "main"}
                    ]
                }
            ),
            MCPTool(
                name="github_get_file",
                description="获取 GitHub 仓库中单个文件的内容和元数据",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "path": {
                            "type": "string",
                            "description": "文件路径"
                        },
                        "ref": {
                            "type": "string",
                            "description": "Git 引用（分支名、标签或提交 SHA），默认为默认分支",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "path"]
                },
                metadata={
                    "tags": ["GitHub", "文件内容", "下载", "读取"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "path": "README.md"},
                        {"owner": "microsoft", "repo": "vscode", "path": "package.json", "ref": "main"}
                    ]
                }
            ),
            MCPTool(
                name="github_get_tree",
                description="获取 GitHub 仓库目录树结构",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tree_sha": {
                            "type": "string",
                            "description": "树的 SHA 值或分支名"
                        },
                        "recursive": {
                            "type": "boolean",
                            "description": "是否递归获取所有子目录",
                            "default": False
                        }
                    },
                    "required": ["owner", "repo", "tree_sha"]
                },
                metadata={
                    "tags": ["GitHub", "目录树", "文件结构", "递归"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World", "tree_sha": "main", "recursive": False},
                        {"owner": "facebook", "repo": "react", "tree_sha": "main", "recursive": True}
                    ]
                }
            ),
            MCPTool(
                name="github_get_readme",
                description="获取 GitHub 仓库的 README 文件",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "ref": {
                            "type": "string",
                            "description": "Git 引用（分支名、标签或提交 SHA），默认为默认分支",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "README", "文档", "说明"],
                    "examples": [
                        {"owner": "octocat", "repo": "Hello-World"},
                        {"owner": "golang", "repo": "go", "ref": "master"}
                    ]
                }
            ),
            MCPTool(
                name="github_new_file",
                description="在 GitHub 仓库中创建新文件",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "path": {
                            "type": "string",
                            "description": "文件路径"
                        },
                        "message": {
                            "type": "string",
                            "description": "提交信息"
                        },
                        "content": {
                            "type": "string",
                            "description": "文件内容（将自动进行 base64 编码）"
                        },
                        "branch": {
                            "type": "string",
                            "description": "目标分支，默认为仓库默认分支",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "path", "message", "content"]
                },
                metadata={
                    "tags": ["GitHub", "创建文件", "提交", "上传"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "path": "new-file.txt",
                            "message": "Add new file",
                            "content": "Hello, world!"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_set_file",
                description="更新 GitHub 仓库中的现有文件",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "path": {
                            "type": "string",
                            "description": "文件路径"
                        },
                        "message": {
                            "type": "string",
                            "description": "提交信息"
                        },
                        "content": {
                            "type": "string",
                            "description": "新的文件内容（将自动进行 base64 编码）"
                        },
                        "sha": {
                            "type": "string",
                            "description": "要更新的文件的当前 SHA"
                        },
                        "branch": {
                            "type": "string",
                            "description": "目标分支，默认为仓库默认分支",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "path", "message", "content", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "更新文件", "修改", "提交"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "path": "README.md",
                            "message": "Update README",
                            "content": "# Updated README",
                            "sha": "7c258a9869f33c1e1e1f74fbb32f07c86cb5a75b"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_del_file",
                description="删除 GitHub 仓库中的文件",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "path": {
                            "type": "string",
                            "description": "文件路径"
                        },
                        "message": {
                            "type": "string",
                            "description": "提交信息"
                        },
                        "sha": {
                            "type": "string",
                            "description": "要删除的文件的当前 SHA"
                        },
                        "branch": {
                            "type": "string",
                            "description": "目标分支，默认为仓库默认分支",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "path", "message", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "删除文件", "移除", "提交"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "path": "old-file.txt",
                            "message": "Remove old file",
                            "sha": "7c258a9869f33c1e1e1f74fbb32f07c86cb5a75b"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_blob",
                description="获取 GitHub 仓库中的 blob 对象（文件内容）",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "file_sha": {
                            "type": "string",
                            "description": "文件的 SHA 值"
                        }
                    },
                    "required": ["owner", "repo", "file_sha"]
                },
                metadata={
                    "tags": ["GitHub", "blob", "文件对象", "SHA"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "file_sha": "7c258a9869f33c1e1e1f74fbb32f07c86cb5a75b"
                        }
                    ]
                }
            ),

            # ============ GitHub Git 操作工具 ============
            MCPTool(
                name="github_new_blob",
                description="创建 GitHub 仓库中的 blob 对象",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "content": {
                            "type": "string",
                            "description": "文件内容（UTF-8字符串或base64编码）"
                        },
                        "encoding": {
                            "type": "string",
                            "description": "内容编码方式",
                            "enum": ["utf-8", "base64"],
                            "default": "utf-8"
                        }
                    },
                    "required": ["owner", "repo", "content"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "blob", "对象"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "content": "Hello, World!",
                            "encoding": "utf-8"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_new_tree",
                description="创建 GitHub 仓库中的目录树对象",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tree": {
                            "type": "array",
                            "description": "树对象列表",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "文件路径"},
                                    "mode": {"type": "string", "description": "文件模式"},
                                    "type": {"type": "string", "description": "对象类型"},
                                    "sha": {"type": "string", "description": "对象SHA"}
                                }
                            }
                        },
                        "base_tree": {
                            "type": "string",
                            "description": "基础树的 SHA（可选）",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "tree"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "tree", "目录树"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "tree": [
                                {
                                    "path": "file.txt",
                                    "mode": "100644",
                                    "type": "blob",
                                    "sha": "44b4fc6d56897b048c772eb4087f854f46256132"
                                }
                            ]
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_new_commit",
                description="创建 GitHub 仓库中的提交对象",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "message": {
                            "type": "string",
                            "description": "提交信息"
                        },
                        "tree": {
                            "type": "string",
                            "description": "树对象的 SHA"
                        },
                        "parents": {
                            "type": "array",
                            "description": "父提交的 SHA 列表",
                            "items": {"type": "string"}
                        },
                        "author": {
                            "type": "object",
                            "description": "作者信息",
                            "properties": {
                                "name": {"type": "string"},
                                "email": {"type": "string"},
                                "date": {"type": "string"}
                            }
                        }
                    },
                    "required": ["owner", "repo", "message", "tree"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commit", "提交"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "message": "Add new feature",
                            "tree": "cd8274d15fa3ae2ab983129fb037999f264ba9a7",
                            "parents": ["7638417db6d59f3c431d3e1f261cc637155684cd"]
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_new_ref",
                description="创建 GitHub 仓库中的引用（分支/标签）",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "ref": {
                            "type": "string",
                            "description": "引用名称（如 refs/heads/feature-branch）"
                        },
                        "sha": {
                            "type": "string",
                            "description": "指向的提交 SHA"
                        }
                    },
                    "required": ["owner", "repo", "ref", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "reference", "分支", "标签"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "ref": "refs/heads/feature-branch",
                            "sha": "aa218f56b14c9653891f9e74264a383fa43fefbd"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_set_ref",
                description="更新 GitHub 仓库中的引用",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "ref": {
                            "type": "string",
                            "description": "引用名称（如 heads/main）"
                        },
                        "sha": {
                            "type": "string",
                            "description": "新的提交 SHA"
                        },
                        "force": {
                            "type": "boolean",
                            "description": "是否强制更新",
                            "default": False
                        }
                    },
                    "required": ["owner", "repo", "ref", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "reference", "更新"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "ref": "heads/main",
                            "sha": "aa218f56b14c9653891f9e74264a383fa43fefbd",
                            "force": False
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_ref",
                description="获取 GitHub 仓库中的引用信息",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "ref": {
                            "type": "string",
                            "description": "引用名称（如 heads/main）"
                        }
                    },
                    "required": ["owner", "repo", "ref"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "reference", "查询"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "ref": "heads/main"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_ls_refs",
                description="列出 GitHub 仓库中的引用",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "namespace": {
                            "type": "string",
                            "description": "命名空间过滤（如 heads, tags）",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "reference", "列表"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "namespace": "heads"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_del_ref",
                description="删除 GitHub 仓库中的引用",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "ref": {
                            "type": "string",
                            "description": "引用名称（如 heads/feature-branch）"
                        }
                    },
                    "required": ["owner", "repo", "ref"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "reference", "删除"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "ref": "heads/feature-branch"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_new_tag",
                description="创建 GitHub 仓库中的标签对象",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tag": {
                            "type": "string",
                            "description": "标签名称"
                        },
                        "message": {
                            "type": "string",
                            "description": "标签信息"
                        },
                        "object_sha": {
                            "type": "string",
                            "description": "标签指向的对象 SHA"
                        },
                        "object_type": {
                            "type": "string",
                            "description": "对象类型",
                            "enum": ["commit", "tree", "blob"],
                            "default": "commit"
                        }
                    },
                    "required": ["owner", "repo", "tag", "message", "object_sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "tag", "标签"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "tag": "v1.0.0",
                            "message": "Release version 1.0.0",
                            "object_sha": "c3d0be41ecbe669545ee3e94d31ed9a4bc91ee3c",
                            "object_type": "commit"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_tag",
                description="获取 GitHub 仓库中的标签对象",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tag_sha": {
                            "type": "string",
                            "description": "标签对象的 SHA"
                        }
                    },
                    "required": ["owner", "repo", "tag_sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "tag", "查询"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "tag_sha": "940bd336248efae0f9ee5bc7b2d5c985887b16ac"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_compare_commits",
                description="比较 GitHub 仓库中的两个提交",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "base": {
                            "type": "string",
                            "description": "基础提交（分支名、标签或SHA）"
                        },
                        "head": {
                            "type": "string",
                            "description": "目标提交（分支名、标签或SHA）"
                        }
                    },
                    "required": ["owner", "repo", "base", "head"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "compare", "比较", "diff"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "base": "main",
                            "head": "feature-branch"
                        }
                    ]
                }
            ),
            # Git Commits 工具
            MCPTool(
                name="github_ls_commits",
                description="列出 GitHub 仓库的提交历史",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "sha": {
                            "type": "string",
                            "description": "SHA 或分支名称，默认为默认分支",
                            "default": ""
                        },
                        "path": {
                            "type": "string",
                            "description": "只返回影响此路径的提交",
                            "default": ""
                        },
                        "author": {
                            "type": "string",
                            "description": "GitHub 用户名或邮箱",
                            "default": ""
                        },
                        "committer": {
                            "type": "string",
                            "description": "GitHub 用户名或邮箱",
                            "default": ""
                        },
                        "since": {
                            "type": "string",
                            "description": "ISO 8601 日期时间字符串，只返回此日期之后的提交",
                            "default": ""
                        },
                        "until": {
                            "type": "string",
                            "description": "ISO 8601 日期时间字符串，只返回此日期之前的提交",
                            "default": ""
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "default": 1,
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commits", "提交", "历史"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        },
                        {
                            "owner": "microsoft",
                            "repo": "vscode",
                            "sha": "main",
                            "since": "2023-01-01T00:00:00Z"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_commit",
                description="获取 GitHub 仓库中的单个提交详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "sha": {
                            "type": "string",
                            "description": "提交 SHA"
                        }
                    },
                    "required": ["owner", "repo", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commit", "提交", "详情"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_ls_commit_comments",
                description="列出 GitHub 仓库提交的评论",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "sha": {
                            "type": "string",
                            "description": "提交 SHA"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "default": 1,
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commit", "comments", "评论"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_new_commit_comment",
                description="创建 GitHub 仓库提交评论",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "sha": {
                            "type": "string",
                            "description": "提交 SHA"
                        },
                        "body": {
                            "type": "string",
                            "description": "评论内容"
                        },
                        "path": {
                            "type": "string",
                            "description": "文件路径（用于行级评论）",
                            "default": ""
                        },
                        "line": {
                            "type": "integer",
                            "description": "文件行号（用于行级评论）"
                        },
                        "position": {
                            "type": "integer",
                            "description": "差异位置（用于行级评论）"
                        }
                    },
                    "required": ["owner", "repo", "sha", "body"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commit", "comment", "评论"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
                            "body": "This is a great change!"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_commit_status",
                description="获取 GitHub 仓库提交的状态信息",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "sha": {
                            "type": "string",
                            "description": "提交 SHA"
                        }
                    },
                    "required": ["owner", "repo", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commit", "status", "状态"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_ls_commit_statuses",
                description="列出 GitHub 仓库提交的所有状态",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "sha": {
                            "type": "string",
                            "description": "提交 SHA"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页数量",
                            "default": 30,
                            "minimum": 1,
                            "maximum": 100
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "default": 1,
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "sha"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commit", "statuses", "状态列表"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_new_commit_status",
                description="创建 GitHub 仓库提交状态",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "sha": {
                            "type": "string",
                            "description": "提交 SHA"
                        },
                        "state": {
                            "type": "string",
                            "description": "状态",
                            "enum": ["error", "failure", "pending", "success"]
                        },
                        "target_url": {
                            "type": "string",
                            "description": "目标 URL",
                            "default": ""
                        },
                        "description": {
                            "type": "string",
                            "description": "状态描述",
                            "default": ""
                        },
                        "context": {
                            "type": "string",
                            "description": "状态上下文",
                            "default": "default"
                        }
                    },
                    "required": ["owner", "repo", "sha", "state"]
                },
                metadata={
                    "tags": ["GitHub", "Git", "commit", "status", "创建状态"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "sha": "6dcb09b5b57875f334f61aebed695e2e4193db5e",
                            "state": "success",
                            "description": "Build successful"
                        }
                    ]
                }
            ),

            # ===== Issues 管理工具 (12 个) =====

            # 40. List issue comments
            MCPTool(
                name="github_ls_issue_comments",
                description="列出 GitHub 问题的所有评论",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        },
                        "sort": {
                            "type": "string",
                            "description": "排序方式",
                            "enum": ["created", "updated"],
                            "default": "created"
                        },
                        "direction": {
                            "type": "string",
                            "description": "排序方向",
                            "enum": ["asc", "desc"],
                            "default": "asc"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的评论数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "comments", "评论列表"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1,
                            "sort": "created",
                            "direction": "asc"
                        }
                    ]
                }
            ),

            # 41. Get issue comment
            MCPTool(
                name="github_get_issue_comment",
                description="获取 GitHub 问题的单个评论详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "comment_id": {
                            "type": "integer",
                            "description": "评论 ID"
                        }
                    },
                    "required": ["owner", "repo", "comment_id"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "comment", "单个评论"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "comment_id": 1
                        }
                    ]
                }
            ),

            # 42. Create issue comment
            MCPTool(
                name="github_new_issue_comment",
                description="为 GitHub 问题创建新评论",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        },
                        "body": {
                            "type": "string",
                            "description": "评论内容，支持 Markdown 格式"
                        }
                    },
                    "required": ["owner", "repo", "issue_number", "body"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "comment", "创建评论"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1,
                            "body": "This is a comment"
                        }
                    ]
                }
            ),

            # 43. Update issue comment
            MCPTool(
                name="github_set_issue_comment",
                description="更新 GitHub 问题评论内容",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "comment_id": {
                            "type": "integer",
                            "description": "评论 ID"
                        },
                        "body": {
                            "type": "string",
                            "description": "新的评论内容，支持 Markdown 格式"
                        }
                    },
                    "required": ["owner", "repo", "comment_id", "body"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "comment", "更新评论"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "comment_id": 1,
                            "body": "Updated comment content"
                        }
                    ]
                }
            ),

            # 44. Delete issue comment
            MCPTool(
                name="github_del_issue_comment",
                description="删除 GitHub 问题评论",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "comment_id": {
                            "type": "integer",
                            "description": "要删除的评论 ID"
                        }
                    },
                    "required": ["owner", "repo", "comment_id"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "comment", "删除评论"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "comment_id": 1
                        }
                    ]
                }
            ),

            # 45. List issue labels
            MCPTool(
                name="github_ls_issue_labels",
                description="列出 GitHub 问题的所有标签",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "labels", "标签列表"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1
                        }
                    ]
                }
            ),

            # 46. Add labels to issue
            MCPTool(
                name="github_add_issue_labels",
                description="为 GitHub 问题添加标签",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        },
                        "labels": {
                            "type": "array",
                            "description": "要添加的标签列表",
                            "items": {"type": "string"}
                        }
                    },
                    "required": ["owner", "repo", "issue_number", "labels"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "labels", "添加标签"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1,
                            "labels": ["bug", "urgent"]
                        }
                    ]
                }
            ),

            # 47. Remove label from issue
            MCPTool(
                name="github_del_issue_label",
                description="从 GitHub 问题中移除指定标签",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        },
                        "name": {
                            "type": "string",
                            "description": "要移除的标签名称"
                        }
                    },
                    "required": ["owner", "repo", "issue_number", "name"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "labels", "移除标签"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1,
                            "name": "bug"
                        }
                    ]
                }
            ),

            # 48. Replace all labels
            MCPTool(
                name="github_set_issue_labels",
                description="替换 GitHub 问题的所有标签",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        },
                        "labels": {
                            "type": "array",
                            "description": "新的标签列表（将替换所有现有标签）",
                            "items": {"type": "string"},
                            "default": []
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "labels", "替换标签"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1,
                            "labels": ["enhancement", "feature"]
                        }
                    ]
                }
            ),

            # 49. Lock issue
            MCPTool(
                name="github_lock_issue",
                description="锁定 GitHub 问题，防止进一步讨论",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        },
                        "lock_reason": {
                            "type": "string",
                            "description": "锁定原因",
                            "enum": ["off-topic", "too heated", "resolved", "spam"],
                            "default": "resolved"
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "lock", "锁定问题"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1,
                            "lock_reason": "resolved"
                        }
                    ]
                }
            ),

            # 50. Unlock issue
            MCPTool(
                name="github_unlock_issue",
                description="解锁 GitHub 问题，允许继续讨论",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "unlock", "解锁问题"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1
                        }
                    ]
                }
            ),

            # 51. List issue events
            MCPTool(
                name="github_ls_issue_events",
                description="列出 GitHub 问题的所有事件（状态变更、标签变更等）",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "issue_number": {
                            "type": "integer",
                            "description": "问题编号"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的事件数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["owner", "repo", "issue_number"]
                },
                metadata={
                    "tags": ["GitHub", "Issues", "events", "问题事件"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "issue_number": 1
                        }
                    ]
                }
            ),

            # ============ GitHub Releases 管理工具 ============
            MCPTool(
                name="github_ls_releases",
                description="列出 GitHub 仓库的 releases",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的 releases 数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "发布", "版本"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_release",
                description="获取 GitHub 仓库中特定 release 的详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "release_id": {
                            "type": "integer",
                            "description": "Release ID",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "release_id"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "详情", "查询"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "release_id": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_latest_release",
                description="获取 GitHub 仓库的最新 release",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "最新版本", "latest"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_release_by_tag",
                description="根据标签获取 GitHub 仓库的 release",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tag": {
                            "type": "string",
                            "description": "标签名称"
                        }
                    },
                    "required": ["owner", "repo", "tag"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "标签", "tag"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "tag": "v1.0.0"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_new_release",
                description="创建 GitHub 仓库的新 release",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "标签名称"
                        },
                        "target_commitish": {
                            "type": "string",
                            "description": "指定目标分支或提交的 SHA。默认为仓库的默认分支",
                            "default": ""
                        },
                        "name": {
                            "type": "string",
                            "description": "Release 名称",
                            "default": ""
                        },
                        "body": {
                            "type": "string",
                            "description": "Release 说明内容",
                            "default": ""
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "是否为草稿状态",
                            "default": False
                        },
                        "prerelease": {
                            "type": "boolean",
                            "description": "是否为预发布版本",
                            "default": False
                        },
                        "discussion_category_name": {
                            "type": "string",
                            "description": "讨论分类名称",
                            "default": ""
                        },
                        "generate_release_notes": {
                            "type": "boolean",
                            "description": "是否自动生成 release 说明",
                            "default": False
                        },
                        "make_latest": {
                            "type": "string",
                            "description": "是否设为最新版本",
                            "enum": ["true", "false", "legacy"],
                            "default": "true"
                        }
                    },
                    "required": ["owner", "repo", "tag_name"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "创建", "发布"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "tag_name": "v1.0.0",
                            "name": "Version 1.0.0",
                            "body": "First stable release"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_set_release",
                description="更新 GitHub 仓库的 release",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "release_id": {
                            "type": "integer",
                            "description": "Release ID",
                            "minimum": 1
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "标签名称",
                            "default": ""
                        },
                        "target_commitish": {
                            "type": "string",
                            "description": "指定目标分支或提交的 SHA",
                            "default": ""
                        },
                        "name": {
                            "type": "string",
                            "description": "Release 名称",
                            "default": ""
                        },
                        "body": {
                            "type": "string",
                            "description": "Release 说明内容",
                            "default": ""
                        },
                        "draft": {
                            "type": "boolean",
                            "description": "是否为草稿状态"
                        },
                        "prerelease": {
                            "type": "boolean",
                            "description": "是否为预发布版本"
                        },
                        "discussion_category_name": {
                            "type": "string",
                            "description": "讨论分类名称",
                            "default": ""
                        },
                        "make_latest": {
                            "type": "string",
                            "description": "是否设为最新版本",
                            "enum": ["true", "false", "legacy"],
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "release_id"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "更新", "修改"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "release_id": 1,
                            "name": "Updated Version 1.0.0"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_del_release",
                description="删除 GitHub 仓库的 release",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "release_id": {
                            "type": "integer",
                            "description": "Release ID",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "release_id"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "删除", "移除"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "release_id": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_ls_release_assets",
                description="列出 GitHub release 的资产文件",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "release_id": {
                            "type": "integer",
                            "description": "Release ID",
                            "minimum": 1
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的资产数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        }
                    },
                    "required": ["owner", "repo", "release_id"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "资产", "附件"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "release_id": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_release_asset",
                description="获取 GitHub release 资产文件的详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "asset_id": {
                            "type": "integer",
                            "description": "资产 ID",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "asset_id"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "资产详情", "下载"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "asset_id": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_set_release_asset",
                description="更新 GitHub release 资产文件信息",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "asset_id": {
                            "type": "integer",
                            "description": "资产 ID",
                            "minimum": 1
                        },
                        "name": {
                            "type": "string",
                            "description": "资产文件名",
                            "default": ""
                        },
                        "label": {
                            "type": "string",
                            "description": "资产标签",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "asset_id"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "资产更新", "重命名"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "asset_id": 1,
                            "name": "app-v1.0.0.zip"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_del_release_asset",
                description="删除 GitHub release 资产文件",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "asset_id": {
                            "type": "integer",
                            "description": "资产 ID",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "asset_id"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "资产删除", "移除"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "asset_id": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_gen_release_notes",
                description="生成 GitHub release 说明",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tag_name": {
                            "type": "string",
                            "description": "标签名称"
                        },
                        "target_commitish": {
                            "type": "string",
                            "description": "指定目标分支或提交的 SHA",
                            "default": ""
                        },
                        "previous_tag_name": {
                            "type": "string",
                            "description": "上一个标签名称",
                            "default": ""
                        },
                        "configuration_file_path": {
                            "type": "string",
                            "description": "配置文件路径",
                            "default": ".github/release.yml"
                        }
                    },
                    "required": ["owner", "repo", "tag_name"]
                },
                metadata={
                    "tags": ["GitHub", "Releases", "自动生成", "说明"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "tag_name": "v1.0.0",
                            "previous_tag_name": "v0.9.0"
                        }
                    ]
                }
            ),

            # ============ GitHub Security 安全工具 ============

            # Code Scanning 代码扫描工具
            MCPTool(
                name="github_ls_code_alerts",
                description="列出 GitHub 仓库的代码扫描警报",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tool_name": {
                            "type": "string",
                            "description": "扫描工具名称过滤",
                            "default": ""
                        },
                        "tool_guid": {
                            "type": "string",
                            "description": "工具 GUID 过滤",
                            "default": ""
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的警报数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        },
                        "ref": {
                            "type": "string",
                            "description": "Git 引用过滤",
                            "default": ""
                        },
                        "state": {
                            "type": "string",
                            "description": "警报状态过滤",
                            "enum": ["open", "closed", "dismissed", "fixed"],
                            "default": ""
                        },
                        "severity": {
                            "type": "string",
                            "description": "严重级别过滤",
                            "enum": ["critical", "high", "medium", "low", "warning", "note", "error"],
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Code Scanning", "代码扫描"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "state": "open",
                            "severity": "high"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_code_alert",
                description="获取 GitHub 仓库特定代码扫描警报的详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "alert_number": {
                            "type": "integer",
                            "description": "警报编号",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "alert_number"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Code Scanning", "警报详情"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "alert_number": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_set_code_alert",
                description="更新 GitHub 仓库代码扫描警报状态",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "alert_number": {
                            "type": "integer",
                            "description": "警报编号",
                            "minimum": 1
                        },
                        "state": {
                            "type": "string",
                            "description": "警报状态",
                            "enum": ["open", "dismissed"]
                        },
                        "dismissed_reason": {
                            "type": "string",
                            "description": "忽略原因",
                            "default": ""
                        },
                        "dismissed_comment": {
                            "type": "string",
                            "description": "忽略评论",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "alert_number", "state"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Code Scanning", "警报管理"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "alert_number": 1,
                            "state": "dismissed",
                            "dismissed_reason": "false positive"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_ls_code_analyses",
                description="列出 GitHub 仓库的代码扫描分析",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "tool_name": {
                            "type": "string",
                            "description": "扫描工具名称过滤",
                            "default": ""
                        },
                        "ref": {
                            "type": "string",
                            "description": "Git 引用过滤",
                            "default": ""
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的分析数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Code Scanning", "扫描分析"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "tool_name": "CodeQL"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_code_analysis",
                description="获取 GitHub 仓库特定代码扫描分析的详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "analysis_id": {
                            "type": "integer",
                            "description": "分析 ID",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "analysis_id"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Code Scanning", "分析详情"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "analysis_id": 123
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_del_code_analysis",
                description="删除 GitHub 仓库的代码扫描分析",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "analysis_id": {
                            "type": "integer",
                            "description": "分析 ID",
                            "minimum": 1
                        },
                        "confirm_delete": {
                            "type": "string",
                            "description": "确认删除参数",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "analysis_id"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Code Scanning", "删除分析"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "analysis_id": 123
                        }
                    ]
                }
            ),

            # Secret Scanning 密钥扫描工具
            MCPTool(
                name="github_ls_secret_alerts",
                description="列出 GitHub 仓库的密钥扫描警报",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "state": {
                            "type": "string",
                            "description": "警报状态过滤",
                            "enum": ["open", "resolved"],
                            "default": ""
                        },
                        "secret_type": {
                            "type": "string",
                            "description": "密钥类型过滤",
                            "default": ""
                        },
                        "resolution": {
                            "type": "string",
                            "description": "解决方案过滤",
                            "enum": ["false_positive", "wont_fix", "revoked", "pattern_edited", "pattern_deleted", "used_in_tests"],
                            "default": ""
                        },
                        "sort": {
                            "type": "string",
                            "description": "排序方式",
                            "enum": ["created", "updated"],
                            "default": "created"
                        },
                        "direction": {
                            "type": "string",
                            "description": "排序方向",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的警报数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Secret Scanning", "密钥扫描"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "state": "open"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_secret_alert",
                description="获取 GitHub 仓库特定密钥扫描警报的详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "alert_number": {
                            "type": "integer",
                            "description": "警报编号",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "alert_number"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Secret Scanning", "警报详情"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "alert_number": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_set_secret_alert",
                description="更新 GitHub 仓库密钥扫描警报状态",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "alert_number": {
                            "type": "integer",
                            "description": "警报编号",
                            "minimum": 1
                        },
                        "state": {
                            "type": "string",
                            "description": "警报状态",
                            "enum": ["open", "resolved"]
                        },
                        "resolution": {
                            "type": "string",
                            "description": "解决方案",
                            "enum": ["false_positive", "wont_fix", "revoked", "pattern_edited", "pattern_deleted", "used_in_tests"],
                            "default": ""
                        },
                        "resolution_comment": {
                            "type": "string",
                            "description": "解决方案评论",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "alert_number", "state"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Secret Scanning", "警报管理"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "alert_number": 1,
                            "state": "resolved",
                            "resolution": "revoked"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_ls_secret_locations",
                description="列出 GitHub 仓库密钥扫描警报的位置信息",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "alert_number": {
                            "type": "integer",
                            "description": "警报编号",
                            "minimum": 1
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的位置数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        }
                    },
                    "required": ["owner", "repo", "alert_number"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Secret Scanning", "警报位置"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "alert_number": 1
                        }
                    ]
                }
            ),

            # Dependabot 依赖项安全工具
            MCPTool(
                name="github_ls_dependabot_alerts",
                description="列出 GitHub 仓库的 Dependabot 安全警报",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "state": {
                            "type": "string",
                            "description": "警报状态过滤",
                            "enum": ["auto_dismissed", "dismissed", "fixed", "open"],
                            "default": ""
                        },
                        "severity": {
                            "type": "string",
                            "description": "严重级别过滤",
                            "enum": ["low", "medium", "high", "critical"],
                            "default": ""
                        },
                        "ecosystem": {
                            "type": "string",
                            "description": "生态系统过滤",
                            "default": ""
                        },
                        "package": {
                            "type": "string",
                            "description": "包名过滤",
                            "default": ""
                        },
                        "scope": {
                            "type": "string",
                            "description": "依赖范围过滤",
                            "enum": ["development", "runtime"],
                            "default": ""
                        },
                        "sort": {
                            "type": "string",
                            "description": "排序方式",
                            "enum": ["created", "updated"],
                            "default": "created"
                        },
                        "direction": {
                            "type": "string",
                            "description": "排序方向",
                            "enum": ["asc", "desc"],
                            "default": "desc"
                        },
                        "page": {
                            "type": "integer",
                            "description": "页码",
                            "minimum": 1,
                            "default": 1
                        },
                        "per_page": {
                            "type": "integer",
                            "description": "每页返回的警报数量",
                            "minimum": 1,
                            "maximum": 100,
                            "default": 30
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Dependabot", "依赖项安全"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "state": "open",
                            "severity": "high"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_dependabot_alert",
                description="获取 GitHub 仓库特定 Dependabot 警报的详情",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "alert_number": {
                            "type": "integer",
                            "description": "警报编号",
                            "minimum": 1
                        }
                    },
                    "required": ["owner", "repo", "alert_number"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Dependabot", "警报详情"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "alert_number": 1
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_set_dependabot_alert",
                description="更新 GitHub 仓库 Dependabot 警报状态",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        },
                        "alert_number": {
                            "type": "integer",
                            "description": "警报编号",
                            "minimum": 1
                        },
                        "state": {
                            "type": "string",
                            "description": "警报状态",
                            "enum": ["dismissed", "open"]
                        },
                        "dismissed_reason": {
                            "type": "string",
                            "description": "忽略原因",
                            "enum": ["fix_started", "inaccurate", "no_bandwidth", "not_used", "tolerable_risk"],
                            "default": ""
                        },
                        "dismissed_comment": {
                            "type": "string",
                            "description": "忽略评论",
                            "default": ""
                        }
                    },
                    "required": ["owner", "repo", "alert_number", "state"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Dependabot", "警报管理"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World",
                            "alert_number": 1,
                            "state": "dismissed",
                            "dismissed_reason": "tolerable_risk"
                        }
                    ]
                }
            ),

            # Security Configuration 安全配置工具
            MCPTool(
                name="github_get_security_config",
                description="获取 GitHub 仓库的安全配置",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Configuration", "安全配置"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_on_auto_security",
                description="启用 GitHub 仓库的自动安全修复",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Automated Fixes", "自动修复"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_off_auto_security",
                description="禁用 GitHub 仓库的自动安全修复",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Automated Fixes", "禁用修复"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_get_vuln_alerts",
                description="获取 GitHub 仓库漏洞警报的启用状态",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Vulnerability Alerts", "漏洞警报"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_on_vuln_alerts",
                description="启用 GitHub 仓库的漏洞警报",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Vulnerability Alerts", "启用警报"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
                    ]
                }
            ),
            MCPTool(
                name="github_off_vuln_alerts",
                description="禁用 GitHub 仓库的漏洞警报",
                category="github",
                schema={
                    "type": "object",
                    "properties": {
                        "owner": {
                            "type": "string",
                            "description": "仓库所有者用户名或组织名"
                        },
                        "repo": {
                            "type": "string",
                            "description": "仓库名称"
                        }
                    },
                    "required": ["owner", "repo"]
                },
                metadata={
                    "tags": ["GitHub", "Security", "Vulnerability Alerts", "禁用警报"],
                    "examples": [
                        {
                            "owner": "octocat",
                            "repo": "Hello-World"
                        }
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