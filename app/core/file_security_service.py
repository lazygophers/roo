"""
文件安全配置数据库服务
负责文件工具安全配置的数据库存储和管理
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from tinydb import TinyDB, Query

from app.core.config import PROJECT_ROOT
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging
from app.core.unified_database import get_unified_database, TableNames

logger = setup_logging("INFO")

class FileSecurityConfig:
    """文件安全配置数据模型"""
    
    def __init__(self, config_type: str, name: str, description: str, 
                 paths: List[str], enabled: bool = True, **kwargs):
        self.id = kwargs.get('id', config_type)  # 使用配置类型作为ID
        self.config_type = config_type  # readable, writable, deletable, forbidden
        self.name = name
        self.description = description
        self.paths = paths  # 路径列表
        self.enabled = enabled
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.now().isoformat())
        self.metadata = kwargs.get('metadata', {})
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'config_type': self.config_type,
            'name': self.name,
            'description': self.description,
            'paths': self.paths,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileSecurityConfig':
        """从字典创建实例"""
        return cls(**data)

class FileSecurityLimits:
    """文件安全限制数据模型"""
    
    def __init__(self, limit_type: str, name: str, value: Any, 
                 description: str, enabled: bool = True, **kwargs):
        self.id = kwargs.get('id', limit_type)  # 使用限制类型作为ID
        self.limit_type = limit_type  # max_file_size, max_read_lines, strict_mode
        self.name = name
        self.value = value
        self.description = description
        self.enabled = enabled
        self.created_at = kwargs.get('created_at', datetime.now().isoformat())
        self.updated_at = kwargs.get('updated_at', datetime.now().isoformat())
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'limit_type': self.limit_type,
            'name': self.name,
            'value': self.value,
            'description': self.description,
            'enabled': self.enabled,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileSecurityLimits':
        """从字典创建实例"""
        return cls(**data)

class FileSecurityService:
    """文件安全配置数据库服务"""
    
    def __init__(self, use_unified_db: bool = True):
        """初始化文件安全配置服务"""
        self.use_unified_db = use_unified_db
        
        if use_unified_db:
            self.unified_db = get_unified_database()
            self.db = self.unified_db.db
            self.db_path = self.unified_db.db_path
        else:
            # 兼容模式：使用独立数据库文件
            db_dir = PROJECT_ROOT / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "file_security.db")
            self.db_path = db_path
            self.db = TinyDB(db_path)
            self.unified_db = None
        
        # 使用统一表名
        self.paths_table = self.db.table(TableNames.SECURITY_PATHS)
        self.limits_table = self.db.table(TableNames.SECURITY_LIMITS)
        
        logger.info(f"FileSecurityService initialized with unified db: {use_unified_db}")
        
        # 初始化默认配置
        self._init_default_config()
    
    def _init_default_config(self):
        """初始化默认安全配置"""
        logger.info("Initializing default file security configuration...")
        
        # 默认路径配置（空路径表示允许所有路径）
        default_path_configs = [
            FileSecurityConfig(
                config_type="readable",
                name="可读取目录",
                description="允许读取文件的目录列表（空表示允许所有路径）",
                paths=[]
            ),
            FileSecurityConfig(
                config_type="writable", 
                name="可写入目录",
                description="允许写入/创建文件的目录列表（空表示允许所有路径）",
                paths=[]
            ),
            FileSecurityConfig(
                config_type="deletable",
                name="可删除目录", 
                description="允许删除文件的目录列表（空表示允许所有路径）",
                paths=[]
            ),
            FileSecurityConfig(
                config_type="forbidden",
                name="禁止访问目录",
                description="严禁访问的系统重要目录列表",
                paths=[
                    "/etc",
                    "/bin", 
                    "/sbin",
                    "/usr/bin",
                    "/usr/sbin",
                    "/System",  # macOS系统目录
                    "/private/etc",  # macOS系统配置
                    str(Path.home() / ".ssh"),  # SSH密钥目录
                ]
            )
        ]
        
        # 默认限制配置
        default_limit_configs = [
            FileSecurityLimits(
                limit_type="max_file_size",
                name="最大文件大小",
                value=100 * 1024 * 1024,  # 100MB
                description="单个文件的最大大小限制（字节）"
            ),
            FileSecurityLimits(
                limit_type="max_read_lines",
                name="最大读取行数", 
                value=10000,
                description="单次文件读取的最大行数限制"
            ),
            FileSecurityLimits(
                limit_type="strict_mode",
                name="严格模式",
                value=False,
                description="是否启用严格模式（严格模式下只能访问明确允许的目录）"
            )
        ]
        
        # 注册默认路径配置
        Query_obj = Query()
        for config in default_path_configs:
            existing = self.paths_table.get(Query_obj.id == config.id)
            if not existing:
                self.paths_table.insert(config.to_dict())
                logger.info(f"Initialized default path config: {sanitize_for_log(config.name)}")
        
        # 注册默认限制配置
        for limit_config in default_limit_configs:
            existing = self.limits_table.get(Query_obj.id == limit_config.id)
            if not existing:
                self.limits_table.insert(limit_config.to_dict())
                logger.info(f"Initialized default limit config: {sanitize_for_log(limit_config.name)}")
    
    def get_path_config(self, config_type: str) -> Optional[Dict[str, Any]]:
        """获取指定类型的路径配置"""
        Query_obj = Query()
        return self.paths_table.get(Query_obj.config_type == config_type)
    
    def get_all_path_configs(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """获取所有路径配置"""
        if enabled_only:
            Query_obj = Query()
            return self.paths_table.search(Query_obj.enabled == True)
        return self.paths_table.all()
    
    def update_path_config(self, config_type: str, paths: List[str]) -> bool:
        """更新路径配置"""
        Query_obj = Query()
        result = self.paths_table.update({
            'paths': paths,
            'updated_at': datetime.now().isoformat()
        }, Query_obj.config_type == config_type)
        
        if result:
            logger.info(f"Updated path config: {sanitize_for_log(config_type)}")
        return len(result) > 0
    
    def get_limit_config(self, limit_type: str) -> Optional[Dict[str, Any]]:
        """获取指定类型的限制配置"""
        Query_obj = Query()
        return self.limits_table.get(Query_obj.limit_type == limit_type)
    
    def get_all_limit_configs(self, enabled_only: bool = True) -> List[Dict[str, Any]]:
        """获取所有限制配置"""
        if enabled_only:
            Query_obj = Query()
            return self.limits_table.search(Query_obj.enabled == True)
        return self.limits_table.all()
    
    def update_limit_config(self, limit_type: str, value: Any) -> bool:
        """更新限制配置"""
        Query_obj = Query()
        result = self.limits_table.update({
            'value': value,
            'updated_at': datetime.now().isoformat()
        }, Query_obj.limit_type == limit_type)
        
        if result:
            logger.info(f"Updated limit config: {sanitize_for_log(limit_type)} = {sanitize_for_log(str(value))}")
        return len(result) > 0
    
    def enable_path_config(self, config_type: str) -> bool:
        """启用路径配置"""
        Query_obj = Query()
        result = self.paths_table.update({
            'enabled': True,
            'updated_at': datetime.now().isoformat()
        }, Query_obj.config_type == config_type)
        return len(result) > 0
    
    def disable_path_config(self, config_type: str) -> bool:
        """禁用路径配置"""
        Query_obj = Query()
        result = self.paths_table.update({
            'enabled': False,
            'updated_at': datetime.now().isoformat()
        }, Query_obj.config_type == config_type)
        return len(result) > 0
    
    def get_security_summary(self) -> Dict[str, Any]:
        """获取安全配置总览"""
        path_configs = self.get_all_path_configs()
        limit_configs = self.get_all_limit_configs()
        
        summary = {
            'path_configs': {},
            'limit_configs': {},
            'total_paths': 0,
            'enabled_path_configs': 0
        }
        
        for config in path_configs:
            summary['path_configs'][config['config_type']] = {
                'name': config['name'],
                'paths': config['paths'],
                'enabled': config['enabled'],
                'count': len(config['paths'])
            }
            summary['total_paths'] += len(config['paths'])
            if config['enabled']:
                summary['enabled_path_configs'] += 1
        
        for config in limit_configs:
            summary['limit_configs'][config['limit_type']] = {
                'name': config['name'],
                'value': config['value'],
                'enabled': config['enabled'],
                'description': config['description']
            }
        
        summary['last_updated'] = datetime.now().isoformat()
        return summary
    
    def close(self):
        """关闭数据库连接"""
        if not self.use_unified_db:
            # 只有非统一数据库模式才需要手动关闭
            self.db.close()
        logger.info("FileSecurityService closed")


# 全局文件安全服务实例
_file_security_service = None

def get_file_security_service(use_unified_db: bool = True) -> FileSecurityService:
    """获取文件安全服务实例"""
    global _file_security_service
    if _file_security_service is None:
        _file_security_service = FileSecurityService(use_unified_db=use_unified_db)
    return _file_security_service