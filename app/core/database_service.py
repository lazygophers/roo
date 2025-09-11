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

logger = setup_logging("INFO")

class DatabaseService:
    """数据库服务：自动扫描文件并生成数据库表"""
    
    def __init__(self, db_path: str = None):
        """初始化数据库服务
        
        Args:
            db_path: 数据库文件路径，默认为项目根目录下的 data/cache.db
        """
        if db_path is None:
            db_dir = PROJECT_ROOT / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "cache.db")
        
        self.db = TinyDB(db_path)
        self.file_monitor = None
        self.observer = None
        self._scan_configs = {}
        self._running = False
        
        # 初始化表
        self.files_table = self.db.table('files')
        self.metadata_table = self.db.table('metadata')
        
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
            
        self._scan_configs[name] = {
            'path': Path(path),
            'patterns': patterns,
            'parser_func': parser_func or self._default_yaml_parser,
            'watch': watch,
            'table_name': f'{name}_cache'
        }
        
        # 为每个配置创建独立的表
        table = self.db.table(f'{name}_cache')
        logger.info(f"Added scan config: {name} -> {path}")
        
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
        
        logger.info(f"Scanned {len(results)} files for config '{config_name}'")
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
        
        logger.info(f"Sync completed for '{config_name}': {stats}")
        return stats
    
    def sync_all(self) -> Dict[str, Dict[str, int]]:
        """同步所有配置"""
        results = {}
        for config_name in self._scan_configs:
            results[config_name] = self.sync_config(config_name)
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
    
    def close(self):
        """关闭数据库连接"""
        self.stop_watching()
        self.db.close()


# 全局数据库服务实例
_db_service = None

def get_database_service() -> DatabaseService:
    """获取全局数据库服务实例"""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
        
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
    
    return _db_service

def init_database_service():
    """初始化数据库服务并执行首次同步"""
    logger.info("Initializing database service...")
    
    db_service = get_database_service()
    
    # 执行首次全量同步
    sync_results = db_service.sync_all()
    logger.info(f"Initial sync completed: {sync_results}")
    
    # 启动文件监听
    db_service.start_watching()
    
    return db_service