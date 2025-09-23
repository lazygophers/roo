import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from tinydb import TinyDB, Query
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import yaml
import asyncio
import threading
from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging
from app.core.secure_logging import secure_log_key_value, sanitize_for_log
from app.core.unified_database import get_unified_database, TableNames
from app.core.json_cache_service import get_json_cache_service

logger = setup_logging("INFO")

class DatabaseService:
    """数据库服务：自动扫描文件并生成数据库表"""
    
    def __init__(self, use_unified_db: bool = True, enable_json_export: bool = True):
        """初始化数据库服务

        Args:
            use_unified_db: 是否使用统一数据库，默认为True
            enable_json_export: 是否启用JSON导出，默认为True
        """
        self.use_unified_db = use_unified_db
        self.enable_json_export = enable_json_export

        if use_unified_db:
            self.unified_db = get_unified_database()
            self.db = self.unified_db.db
        else:
            # 兼容模式：使用独立数据库文件
            db_dir = PROJECT_ROOT / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "cache.db")
            self.db = TinyDB(db_path)
            self.unified_db = None

        # 初始化JSON缓存服务
        if self.enable_json_export:
            # 确保缓存目录存在
            json_cache_dir = PROJECT_ROOT / "data" / "roo"
            json_cache_dir.mkdir(parents=True, exist_ok=True)
            self.json_cache_service = get_json_cache_service("data/roo")
            logger.info(f"JSON cache service enabled with directory: {json_cache_dir}")
        else:
            self.json_cache_service = None

        self.file_monitor = None
        self.observer = None
        self._scan_configs = {}
        self._running = False

        # 初始化表（使用统一表名）
        self.files_table = self.db.table(TableNames.CACHE_FILES)
        self.metadata_table = self.db.table(TableNames.CACHE_METADATA)
        
    def add_scan_config(self, name: str, path: str, patterns: List[str] = None, 
                       parser_func: callable = None, watch: bool = True):
        """添加扫描配置
        
        Args:
            name: 配置名称
            path: 扫描路径
            patterns: 文件匹配模式，默认为 ['*.yaml', '*.yml']
            parser_func: 自定义解析函数
            watch: 是否监听文件变化
        """
        if patterns is None:
            patterns = ['*.yaml', '*.yml']
            
        # 为每个配置创建独立的表（使用统一命名规范）
        table_name = f'{name}_cache'
        if name == 'models':
            table_name = TableNames.MODELS_CACHE
        elif name == 'hooks':
            table_name = TableNames.HOOKS_CACHE
        elif name == 'rules':
            table_name = TableNames.RULES_CACHE
        
        self._scan_configs[name] = {
            'path': Path(path),
            'patterns': patterns,
            'parser_func': parser_func or self._default_yaml_parser,
            'watch': watch,
            'table_name': table_name
        }
        table = self.db.table(table_name)
        logger.info(f"Added scan config: {name} -> {path} (table: {table_name})")
        
    def _default_yaml_parser(self, file_path: Path) -> Dict[str, Any]:
        """默认YAML文件解析器"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return {}
    
    def _get_file_hash(self, file_path: Path) -> str:
        """计算文件内容哈希"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to hash {file_path}: {e}")
            return ""
    
    def _scan_directory(self, config_name: str) -> List[Dict[str, Any]]:
        """扫描目录并解析文件"""
        config = self._scan_configs[config_name]
        scan_path = config['path']
        patterns = config['patterns']
        parser_func = config['parser_func']
        
        results = []
        
        if not scan_path.exists():
            logger.warning(f"Scan path does not exist: {scan_path}")
            return results
            
        # 遍历目录查找匹配的文件
        for pattern in patterns:
            for file_path in scan_path.rglob(pattern):
                if file_path.is_file():
                    try:
                        # 解析文件内容
                        content = parser_func(file_path)
                        
                        # 计算文件哈希
                        file_hash = self._get_file_hash(file_path)
                        
                        file_stats = file_path.stat()
                        file_data = {
                            'file_path': str(file_path.relative_to(PROJECT_ROOT)),
                            'absolute_path': str(file_path),
                            'file_name': file_path.name,
                            'file_hash': file_hash,
                            'file_size': file_stats.st_size,
                            'last_modified': int(file_stats.st_mtime),
                            'scan_time': datetime.now().isoformat(),
                            'content': content,
                            'config_name': config_name
                        }
                        
                        results.append(file_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to process {file_path}: {e}")
                        continue
        
        logger.info(f"Scanned {len(results)} files for config '{sanitize_for_log(config_name)}'")
        return results
    
    def sync_config(self, config_name: str) -> Dict[str, int]:
        """同步指定配置的文件到数据库"""
        if config_name not in self._scan_configs:
            raise ValueError(f"Config '{config_name}' not found")
        
        config = self._scan_configs[config_name]
        table = self.db.table(config['table_name'])
        
        # 扫描文件
        scanned_files = self._scan_directory(config_name)
        
        stats = {'added': 0, 'updated': 0, 'deleted': 0, 'unchanged': 0}
        Query_obj = Query()
        
        # 获取已存在的文件记录
        existing_files = {record['file_path']: record for record in table.all()}
        current_files = set()
        
        # 处理扫描到的文件
        for file_data in scanned_files:
            file_path = file_data['file_path']
            current_files.add(file_path)
            
            if file_path in existing_files:
                # 检查文件是否有变化
                existing_record = existing_files[file_path]
                if (existing_record['file_hash'] != file_data['file_hash'] or 
                    'file_size' not in existing_record or existing_record.get('file_size') is None or
                    isinstance(existing_record.get('last_modified'), str) or
                    isinstance(existing_record.get('last_modified'), float)):
                    # 文件已修改或缺少文件大小信息，更新记录
                    table.update(file_data, Query_obj.file_path == file_path)
                    stats['updated'] += 1
                else:
                    stats['unchanged'] += 1
            else:
                # 新文件，插入记录
                table.insert(file_data)
                stats['added'] += 1
        
        # 删除不存在的文件记录
        for file_path in existing_files:
            if file_path not in current_files:
                table.remove(Query_obj.file_path == file_path)
                stats['deleted'] += 1
        
        # 更新同步元数据
        metadata = {
            'config_name': config_name,
            'last_sync': datetime.now().isoformat(),
            'total_files': len(current_files),
            'stats': stats
        }
        self.metadata_table.upsert(metadata, Query_obj.config_name == config_name)

        # 导出到JSON文件（如果启用）
        if self.enable_json_export and self.json_cache_service:
            try:
                # 获取更新后的缓存数据
                cache_data = self.get_cached_data(config_name)
                success = self.json_cache_service.export_cache_to_json(config_name, cache_data)
                if success:
                    logger.info(f"  📄 Exported {len(cache_data)} items to JSON: {config_name}.json")
                else:
                    logger.warning(f"  ⚠️ Failed to export JSON for config: {config_name}")
            except Exception as e:
                logger.error(f"  ❌ JSON export error for {config_name}: {e}")

        logger.info(f"Sync completed for '{sanitize_for_log(config_name)}': {stats}")
        return stats
    
    def sync_all(self) -> Dict[str, Dict[str, int]]:
        """同步所有配置"""
        results = {}
        for config_name in self._scan_configs:
            results[config_name] = self.sync_config(config_name)
        return results

    def full_refresh_config(self, config_name: str) -> Dict[str, int]:
        """完全刷新指定配置的数据（覆盖模式）"""
        if config_name not in self._scan_configs:
            raise ValueError(f"Config '{config_name}' not found")

        config = self._scan_configs[config_name]
        table = self.db.table(config['table_name'])

        logger.info(f"🔄 Starting full refresh for '{sanitize_for_log(config_name)}'...")

        # 1. 清空现有数据
        old_count = len(table.all())
        table.truncate()
        logger.info(f"  ✨ Cleared {old_count} existing records")

        # 2. 扫描所有文件
        scanned_files = self._scan_directory(config_name)
        logger.info(f"  📁 Scanned {len(scanned_files)} files from {config['path']}")

        # 3. 批量插入新数据
        if scanned_files:
            table.insert_multiple(scanned_files)
            logger.info(f"  ✅ Inserted {len(scanned_files)} new records")

        # 4. 更新同步元数据
        Query_obj = Query()
        metadata = {
            'config_name': config_name,
            'last_sync': datetime.now().isoformat(),
            'total_files': len(scanned_files),
            'sync_type': 'full_refresh',
            'stats': {
                'cleared': old_count,
                'inserted': len(scanned_files),
                'unchanged': 0,
                'updated': 0,
                'deleted': 0
            }
        }
        self.metadata_table.upsert(metadata, Query_obj.config_name == config_name)

        # 5. 导出到JSON文件（如果启用）
        if self.enable_json_export and self.json_cache_service and scanned_files:
            try:
                success = self.json_cache_service.export_cache_to_json(config_name, scanned_files)
                if success:
                    logger.info(f"  📄 Exported {len(scanned_files)} items to JSON: {config_name}.json")
                else:
                    logger.warning(f"  ⚠️ Failed to export JSON for config: {config_name}")
            except Exception as e:
                logger.error(f"  ❌ JSON export error for {config_name}: {e}")

        stats = metadata['stats']
        logger.info(f"✅ Full refresh completed for '{sanitize_for_log(config_name)}': cleared {old_count}, inserted {len(scanned_files)}")
        return stats

    def full_refresh_all(self) -> Dict[str, Dict[str, int]]:
        """完全刷新所有配置的数据（覆盖模式）"""
        logger.info("🚀 Starting full refresh of all resources...")

        results = {}
        total_configs = len(self._scan_configs)

        for i, config_name in enumerate(self._scan_configs, 1):
            logger.info(f"📋 Processing config {i}/{total_configs}: {sanitize_for_log(config_name)}")
            try:
                results[config_name] = self.full_refresh_config(config_name)
            except Exception as e:
                logger.error(f"❌ Failed to refresh config '{sanitize_for_log(config_name)}': {e}")
                results[config_name] = {'error': str(e)}

        # 计算总体统计
        total_cleared = sum(r.get('cleared', 0) for r in results.values() if 'error' not in r)
        total_inserted = sum(r.get('inserted', 0) for r in results.values() if 'error' not in r)

        logger.info(f"🎉 Full refresh completed! Total: cleared {total_cleared} records, inserted {total_inserted} records")
        return results
    
    def get_cached_data(self, config_name: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """从缓存获取数据"""
        if config_name not in self._scan_configs:
            raise ValueError(f"Config '{config_name}' not found")
        
        config = self._scan_configs[config_name]
        table = self.db.table(config['table_name'])
        
        if filters:
            Query_obj = Query()
            query_conditions = []
            
            for key, value in filters.items():
                if isinstance(value, str):
                    query_conditions.append(Query_obj[key] == value)
                elif isinstance(value, list):
                    query_conditions.append(Query_obj[key].one_of(value))
                elif isinstance(value, dict):
                    if 'contains' in value:
                        query_conditions.append(Query_obj[key].search(value['contains']))
            
            if query_conditions:
                final_query = query_conditions[0]
                for condition in query_conditions[1:]:
                    final_query &= condition
                return table.search(final_query)
        
        return table.all()
    
    def get_file_by_path(self, config_name: str, file_path: str) -> Optional[Dict[str, Any]]:
        """根据文件路径获取文件记录"""
        if config_name not in self._scan_configs:
            return None
        
        config = self._scan_configs[config_name]
        table = self.db.table(config['table_name'])
        Query_obj = Query()
        
        result = table.search(Query_obj.file_path == file_path)
        return result[0] if result else None
    
    class FileChangeHandler(FileSystemEventHandler):
        """文件变化监听器"""
        
        def __init__(self, db_service, config_name):
            self.db_service = db_service
            self.config_name = config_name
            self.config = db_service._scan_configs[config_name]
            
        def _should_process_file(self, file_path: Path) -> bool:
            """检查文件是否应该被处理"""
            for pattern in self.config['patterns']:
                if file_path.match(pattern):
                    return True
            return False
            
        def on_modified(self, event):
            if not event.is_directory:
                file_path = Path(event.src_path)
                if self._should_process_file(file_path):
                    self._sync_file(file_path)
        
        def on_created(self, event):
            if not event.is_directory:
                file_path = Path(event.src_path)
                if self._should_process_file(file_path):
                    self._sync_file(file_path)
        
        def on_deleted(self, event):
            if not event.is_directory:
                file_path = Path(event.src_path)
                if self._should_process_file(file_path):
                    self._remove_file(file_path)
        
        def _sync_file(self, file_path: Path):
            """同步单个文件"""
            try:
                # 在后台线程中执行同步
                threading.Thread(
                    target=self._sync_single_file, 
                    args=(file_path,),
                    daemon=True
                ).start()
            except Exception as e:
                logger.error(f"Failed to sync file {file_path}: {e}")
        
        def _sync_single_file(self, file_path: Path):
            """同步单个文件到数据库"""
            try:
                config = self.config
                table = self.db_service.db.table(config['table_name'])
                parser_func = config['parser_func']
                
                # 解析文件
                content = parser_func(file_path)
                file_hash = self.db_service._get_file_hash(file_path)
                
                file_data = {
                    'file_path': str(file_path.relative_to(PROJECT_ROOT)),
                    'absolute_path': str(file_path),
                    'file_name': file_path.name,
                    'file_hash': file_hash,
                    'last_modified': file_path.stat().st_mtime,
                    'scan_time': datetime.now().isoformat(),
                    'content': content,
                    'config_name': self.config_name
                }
                
                # 更新或插入记录
                Query_obj = Query()
                table.upsert(file_data, Query_obj.file_path == file_data['file_path'])
                
                logger.info(f"Synced file: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to sync single file {file_path}: {e}")
        
        def _remove_file(self, file_path: Path):
            """从数据库移除文件记录"""
            try:
                config = self.config
                table = self.db_service.db.table(config['table_name'])
                Query_obj = Query()
                
                relative_path = str(file_path.relative_to(PROJECT_ROOT))
                removed_count = table.remove(Query_obj.file_path == relative_path)
                
                if removed_count > 0:
                    logger.info(f"Removed file from cache: {file_path}")
                
            except Exception as e:
                logger.error(f"Failed to remove file {file_path}: {e}")
    
    def start_watching(self):
        """启动文件监听"""
        if self._running:
            logger.warning("File watching is already running")
            return
        
        self.observer = Observer()
        
        # 为每个配置添加监听器
        for config_name, config in self._scan_configs.items():
            if config['watch'] and config['path'].exists():
                handler = self.FileChangeHandler(self, config_name)
                self.observer.schedule(handler, str(config['path']), recursive=True)
                logger.info(f"Started watching: {config['path']} for config '{config_name}'")
        
        self.observer.start()
        self._running = True
        logger.info("File watching started")
    
    def stop_watching(self):
        """停止文件监听"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.observer = None
            self._running = False
            logger.info("File watching stopped")
    
    def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        status = {}
        Query_obj = Query()
        
        for config_name in self._scan_configs:
            metadata = self.metadata_table.search(Query_obj.config_name == config_name)
            if metadata:
                status[config_name] = metadata[0]
            else:
                status[config_name] = {'status': 'never_synced'}
        
        return status
    
    def add_cached_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """添加缓存数据到指定表"""
        try:
            table = self.db.table(table_name)
            table.insert(data)
            logger.info(f"Data added to table '{sanitize_for_log(table_name)}': {sanitize_for_log(data.get('name', 'unnamed'))}")
            return True
        except Exception as e:
            logger.error(f"Failed to add data to table '{table_name}': {e}")
            return False
    
    def update_cached_data(self, table_name: str, key: str, data: Dict[str, Any]) -> bool:
        """更新缓存数据"""
        try:
            table = self.db.table(table_name)
            Query_obj = Query()
            table.update(data, Query_obj.name == key)
            logger.info(f"Data updated in table '{sanitize_for_log(table_name)}': {sanitize_for_log(key)}")
            return True
        except Exception as e:
            logger.error(f"Failed to update data in table '{table_name}': {e}")
            return False
    
    def remove_cached_data(self, table_name: str, key: str) -> bool:
        """删除缓存数据"""
        try:
            table = self.db.table(table_name)
            Query_obj = Query()
            table.remove(Query_obj.name == key)
            logger.info(f"Data removed from table '{sanitize_for_log(table_name)}': {sanitize_for_log(key)}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove data from table '{table_name}': {e}")
            return False
    
    def get_cached_data_by_table(self, table_name: str) -> List[Dict[str, Any]]:
        """获取指定表的所有数据"""
        try:
            table = self.db.table(table_name)
            return table.all()
        except Exception as e:
            logger.error(f"Failed to get data from table '{table_name}': {e}")
            return []

    def export_all_to_json(self) -> Dict[str, bool]:
        """手动导出所有缓存数据到JSON文件

        Returns:
            Dict[str, bool]: 每个配置的导出结果
        """
        if not self.enable_json_export or not self.json_cache_service:
            logger.warning("JSON export is not enabled")
            return {}

        logger.info("🚀 Starting manual export of all caches to JSON...")
        return self.json_cache_service.export_all_caches_to_json(self)

    def get_json_cache_summary(self) -> Dict[str, Any]:
        """获取JSON缓存汇总信息

        Returns:
            Dict[str, Any]: JSON缓存汇总信息
        """
        if not self.enable_json_export or not self.json_cache_service:
            return {"error": "JSON export is not enabled"}

        return self.json_cache_service.get_json_cache_summary()

    def import_json_to_database(self, config_name: str) -> Dict[str, Any]:
        """从JSON文件导入数据到数据库

        Args:
            config_name: 配置名称

        Returns:
            Dict[str, Any]: 导入结果
        """
        if not self.enable_json_export or not self.json_cache_service:
            return {
                "success": False,
                "message": "JSON export/import is not enabled",
                "imported_count": 0
            }

        return self.json_cache_service.import_json_to_database(config_name, self)

    def import_all_json_to_database(self) -> Dict[str, Dict[str, Any]]:
        """导入所有JSON缓存文件到数据库

        Returns:
            Dict[str, Dict[str, Any]]: 每个配置的导入结果
        """
        if not self.enable_json_export or not self.json_cache_service:
            logger.warning("JSON export/import is not enabled")
            return {}

        logger.info("🚀 Starting import of all JSON caches to database...")
        return self.json_cache_service.import_all_json_to_database(self)
    
    def close(self):
        """关闭数据库连接"""
        self.stop_watching()
        if not self.use_unified_db:
            # 只有非统一数据库模式才需要手动关闭
            self.db.close()


# 全局数据库服务实例
_db_service = None

def get_database_service(use_unified_db: bool = True, enable_json_export: bool = True) -> DatabaseService:
    """获取全局数据库服务实例"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService(use_unified_db=use_unified_db, enable_json_export=enable_json_export)
        
        # 添加默认的模型文件扫描配置
        models_dir = PROJECT_ROOT / "resources" / "models"
        if models_dir.exists():
            _db_service.add_scan_config(
                name="models",
                path=str(models_dir),
                patterns=['*.yaml', '*.yml'],
                watch=True
            )
        
        # 添加hooks扫描配置
        hooks_dir = PROJECT_ROOT / "resources" / "hooks"
        if hooks_dir.exists():
            _db_service.add_scan_config(
                name="hooks",
                path=str(hooks_dir),
                patterns=['*.md', '*.yaml', '*.yml'],
                watch=True
            )
        
        # 添加rules扫描配置
        rules_dir = PROJECT_ROOT / "resources"
        if rules_dir.exists():
            def rules_parser(file_path: Path) -> Dict[str, Any]:
                """Rules文件解析器"""
                if file_path.suffix.lower() in ['.yaml', '.yml']:
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return yaml.safe_load(f) or {}
                    except:
                        return {}
                elif file_path.suffix.lower() == '.md':
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            return {'content': f.read(), 'type': 'markdown'}
                    except:
                        return {}
                return {}
            
            _db_service.add_scan_config(
                name="rules",
                path=str(rules_dir),
                patterns=['rules*/**/*'],
                parser_func=rules_parser,
                watch=True
            )

        # 添加commands扫描配置
        commands_dir = PROJECT_ROOT / "resources" / "commands"
        if commands_dir.exists():
            _db_service.add_scan_config(
                name="commands",
                path=str(commands_dir),
                patterns=['*.yaml', '*.yml'],
                watch=True
            )

        # 添加roles扫描配置
        roles_dir = PROJECT_ROOT / "resources" / "roles"
        if roles_dir.exists():
            _db_service.add_scan_config(
                name="roles",
                path=str(roles_dir),
                patterns=['*.yaml', '*.yml'],
                watch=True
            )

    return _db_service

def init_database_service(use_unified_db: bool = True, enable_json_export: bool = True):
    """初始化数据库服务并执行首次同步"""
    logger.info("Initializing database service...")

    db_service = get_database_service(use_unified_db=use_unified_db, enable_json_export=enable_json_export)
    
    # 执行首次全量同步
    sync_results = db_service.sync_all()
    logger.info(f"Initial sync completed: {sync_results}")
    
    # 启动文件监听
    db_service.start_watching()
    
    logger.info(f"Database service initialized (unified_db: {use_unified_db})")
    return db_service