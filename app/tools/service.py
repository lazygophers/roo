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
                    },
                    'enable_security_features': True,
                    'enable_config_management': True,
                    'log_level': 'INFO'
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
                    'enable_path_validation': True,
                    'max_file_size_mb': 100,
                    'max_read_lines': 10000,
                    'allowed_extensions': [],  # 空列表表示允许所有扩展名
                    'blocked_extensions': ['.exe', '.bat', '.cmd', '.scr'],
                    'enable_backup_on_write': False,
                    'backup_directory': 'backups',
                    'encoding_detection': True,
                    'default_encoding': 'utf-8',
                    'enable_symlink_follow': False,
                    'enable_hidden_files': False,
                    'enable_recursive_operations': True,
                    'temp_directory': '/tmp'
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
                'name': 'GitHub工具',
                'description': 'GitHub API集成工具，包括仓库管理、issue处理、PR操作等',
                'icon': '🐙',
                'enabled': True,
                'sort_order': 5,
                'config': {
                    'api_base_url': 'https://api.github.com',
                    'default_per_page': 30,
                    'enable_rate_limit_check': True,
                    'enable_auto_retry': True,
                    'max_retry_attempts': 3,
                    'retry_delay_seconds': 1,
                    'timeout_seconds': 30,
                    'enable_request_logging': False,
                    'cache_responses': True,
                    'cache_ttl_seconds': 300,  # 5分钟缓存
                    'default_branch': 'main',
                    'enable_webhook_verification': True,
                    'supported_events': [
                        'push', 'pull_request', 'issues', 'releases',
                        'deployment', 'repository', 'organization'
                    ],
                    'enable_enterprise_features': False,
                    'enable_graphql_api': False,
                    'enable_security_scanning': True,
                    'enable_dependabot_integration': True
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
        builtin_tools = self._get_builtin_tools_definition()
        
        registered_count = 0
        updated_count = 0
        
        Query_obj = Query()
        for tool in builtin_tools:
            existing = self.tools_table.get(Query_obj.name == tool.name)
            
            if existing:
                # 覆盖现有工具（仅保留用户配置：enabled状态和created_at）
                user_enabled = existing.get('enabled', tool.enabled)
                user_created_at = existing.get('created_at', datetime.now().isoformat())

                # 完全覆盖所有内置属性（description、schema、metadata等）
                tool.id = existing.get('id')
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

    def _get_builtin_tools_definition(self):
        """获取内置工具定义（使用装饰器自动发现）"""
        from app.tools.registry import get_registered_tools, clear_registry

        # 清空注册表，重新发现工具
        clear_registry()

        # 自动发现工具模块
        tool_modules = [
            "app.tools.github_tools",
            "app.tools.time_tools",
            "app.tools.system_tools",
            "app.tools.file_tools",
            "app.tools.cache_tools",
        ]

        # 导入工具模块以触发装饰器注册
        import importlib
        for module_name in tool_modules:
            try:
                # 先导入模块
                module = __import__(module_name, fromlist=[''])
                # 强制重新加载以确保装饰器再次执行
                importlib.reload(module)
                logger.info(f"Loaded tool module: {module_name}")
            except ImportError as e:
                logger.warning(f"Failed to load tool module {module_name}: {e}")

        # 获取装饰器注册的工具
        all_tools = get_registered_tools()

        logger.info(f"Loaded {len(all_tools)} tools using decorator system")
        return all_tools

    def sync_tools_database(self):
        """同步工具数据库：自动添加新工具，移除不存在的工具"""
        try:
            # 获取当前定义的所有内置工具
            builtin_tools = self._get_builtin_tools_definition()

            # 创建工具名称集合，用于快速查找
            builtin_tool_names = {tool.name for tool in builtin_tools}

            # 获取数据库中的所有内置工具
            Query_obj = Query()
            db_tools = self.tools_table.search(Query_obj.implementation_type == "builtin")

            added_count = 0
            updated_count = 0
            removed_count = 0

            # 1. 添加或更新现有工具
            for tool in builtin_tools:
                existing = self.tools_table.get(Query_obj.name == tool.name)

                if existing:
                    # 更新现有工具（保留用户配置）
                    user_enabled = existing.get('enabled', tool.enabled)
                    user_created_at = existing.get('created_at', datetime.now().isoformat())

                    tool.id = existing.get('id')
                    tool.created_at = user_created_at
                    tool.updated_at = datetime.now().isoformat()
                    tool.enabled = user_enabled

                    self.tools_table.update(tool.to_dict(), Query_obj.name == tool.name)
                    updated_count += 1
                    logger.info(f"Updated tool: {sanitize_for_log(tool.name)}")
                else:
                    # 添加新工具
                    tool.created_at = datetime.now().isoformat()
                    tool.updated_at = datetime.now().isoformat()
                    self.tools_table.insert(tool.to_dict())
                    added_count += 1
                    logger.info(f"Added new tool: {sanitize_for_log(tool.name)}")

            # 2. 移除不存在的内置工具
            for db_tool in db_tools:
                if db_tool['name'] not in builtin_tool_names:
                    self.tools_table.remove(Query_obj.name == db_tool['name'])
                    removed_count += 1
                    logger.info(f"Removed obsolete tool: {sanitize_for_log(db_tool['name'])}")

            result = {
                "added": added_count,
                "updated": updated_count,
                "removed": removed_count,
                "total_tools": len(builtin_tools)
            }

            logger.info(f"Tool database sync completed: {added_count} added, {updated_count} updated, {removed_count} removed")
            return result

        except Exception as e:
            logger.error(f"Failed to sync tools database: {sanitize_for_log(str(e))}")
            return {"error": str(e), "added": 0, "updated": 0, "removed": 0}
    
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