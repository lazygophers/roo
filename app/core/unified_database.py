"""
统一数据库服务
Unified Database Service

将所有TinyDB数据库合并为单一文件，使用不同的table进行区分
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from tinydb import TinyDB, Query
from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging

logger = setup_logging("INFO")

class UnifiedDatabase:
    """统一数据库管理器"""
    
    _instance: Optional['UnifiedDatabase'] = None
    _db: Optional[TinyDB] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._db is None:
            self._init_database()
    
    def _init_database(self):
        """初始化统一数据库"""
        db_dir = PROJECT_ROOT / "data"
        db_dir.mkdir(exist_ok=True)
        
        db_path = str(db_dir / "lazyai.db")
        self._db = TinyDB(db_path)
        self.db_path = db_path
        
        logger.info(f"Unified database initialized: {db_path}")
    
    @property
    def db(self) -> TinyDB:
        """获取数据库实例"""
        if self._db is None:
            self._init_database()
        return self._db
    
    def get_table(self, table_name: str):
        """获取指定表"""
        return self.db.table(table_name)
    
    def close(self):
        """关闭数据库连接"""
        if self._db:
            self._db.close()
            self._db = None
            logger.info("Unified database closed")
    
    def get_all_tables(self) -> Dict[str, int]:
        """获取所有表及其记录数"""
        tables_info = {}
        for table_name in self.db.tables():
            table = self.db.table(table_name)
            tables_info[table_name] = len(table.all())
        return tables_info
    
    def migrate_from_old_databases(self):
        """从旧数据库迁移数据"""
        data_dir = PROJECT_ROOT / "data"
        migration_log = []
        
        # 定义旧数据库和对应的表映射
        old_dbs_mapping = {
            "cache.db": {
                "files": "cache_files",
                "metadata": "cache_metadata", 
                "models_cache": "models_cache",
                "hooks_cache": "hooks_cache",
                "rules_cache": "rules_cache"
            },
            "file_security.db": {
                "security_paths": "security_paths",
                "security_limits": "security_limits"
            },
            "mcp_tools.db": {
                "mcp_tools": "mcp_tools",
                "mcp_categories": "mcp_categories"
            },
            "lite_cache.db": {
                "models": "lite_models",
                "metadata": "lite_metadata"
            }
        }
        
        for old_db_name, table_mapping in old_dbs_mapping.items():
            old_db_path = data_dir / old_db_name
            if old_db_path.exists():
                try:
                    old_db = TinyDB(str(old_db_path))
                    
                    # 迁移每个表的数据
                    for old_table_name, new_table_name in table_mapping.items():
                        if old_table_name in old_db.tables():
                            old_table = old_db.table(old_table_name)
                            new_table = self.get_table(new_table_name)
                            
                            # 获取旧表数据
                            old_data = old_table.all()
                            if old_data:
                                # 清空新表（避免重复数据）
                                new_table.truncate()
                                # 插入数据
                                new_table.insert_multiple(old_data)
                                migration_log.append(
                                    f"Migrated {len(old_data)} records from {old_db_name}:{old_table_name} to {new_table_name}"
                                )
                    
                    old_db.close()
                    
                    # 备份旧数据库文件
                    backup_path = data_dir / f"{old_db_name}.backup"
                    old_db_path.rename(backup_path)
                    migration_log.append(f"Backed up {old_db_name} to {backup_path}")
                    
                except Exception as e:
                    migration_log.append(f"Failed to migrate {old_db_name}: {e}")
                    logger.error(f"Migration error for {old_db_name}: {e}")
        
        # 记录迁移结果
        for log_entry in migration_log:
            logger.info(log_entry)
        
        return migration_log

# 全局数据库实例
_unified_db = None

def get_unified_database() -> UnifiedDatabase:
    """获取统一数据库实例"""
    global _unified_db
    if _unified_db is None:
        _unified_db = UnifiedDatabase()
    return _unified_db

def close_unified_database():
    """关闭统一数据库"""
    global _unified_db
    if _unified_db:
        _unified_db.close()
        _unified_db = None

# 表名常量定义
class TableNames:
    """数据库表名常量"""
    # 缓存相关表
    CACHE_FILES = "cache_files"
    CACHE_METADATA = "cache_metadata"
    MODELS_CACHE = "models_cache"  
    HOOKS_CACHE = "hooks_cache"
    RULES_CACHE = "rules_cache"
    
    # 文件安全相关表
    SECURITY_PATHS = "security_paths"
    SECURITY_LIMITS = "security_limits"
    
    # MCP工具相关表
    MCP_TOOLS = "mcp_tools"
    MCP_CATEGORIES = "mcp_categories"
    
    # 轻量级缓存表
    LITE_MODELS = "lite_models"
    LITE_METADATA = "lite_metadata"
    
    # 系统表
    SYSTEM_CONFIG = "system_config"
    SYSTEM_LOGS = "system_logs"
    
    # 回收站表
    RECYCLE_BIN = "recycle_bin"
    
    # 时间工具配置表
    TIME_TOOLS_CONFIG = "time_tools_config"

def init_unified_database():
    """初始化统一数据库并执行迁移"""
    logger.info("Initializing unified database system...")
    
    db = get_unified_database()
    
    # 执行数据迁移
    migration_log = db.migrate_from_old_databases()
    
    # 输出表统计信息
    tables_info = db.get_all_tables()
    logger.info(f"Unified database tables: {tables_info}")
    
    return db, migration_log