"""
函数式数据库服务

使用纯函数替代面向对象的数据库服务，提供文件扫描、解析和缓存功能
"""

from typing import Dict, List, Any, Optional, Callable, Tuple
from pathlib import Path
from datetime import datetime
import asyncio
import threading
from functools import partial
from tinydb import TinyDB, Query
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app.core.functional_base import (
    Result, safe, pipe, merge_dicts, create_file_parser,
    compute_file_hash, create_logger, group_by
)
from app.core.config import PROJECT_ROOT
from app.core.unified_database import get_unified_database, TableNames

# =============================================================================
# 数据库连接
# =============================================================================

def get_database_connection(use_unified: bool = True) -> TinyDB:
    """获取数据库连接"""
    if use_unified:
        unified_db = get_unified_database()
        return unified_db.db
    else:
        db_dir = PROJECT_ROOT / "data"
        db_dir.mkdir(exist_ok=True)
        db_path = str(db_dir / "cache.db")
        return TinyDB(db_path)

def get_table(db: TinyDB, table_name: str):
    """获取数据库表"""
    return db.table(table_name)

# =============================================================================
# 文件处理函数
# =============================================================================

def scan_directory(directory: Path, patterns: List[str]) -> List[Path]:
    """扫描目录中匹配模式的文件"""
    if not directory.exists():
        return []

    files = []
    for pattern in patterns:
        files.extend(directory.glob(pattern))

    return [f for f in files if f.is_file()]

def process_file(file_path: Path) -> Result:
    """处理单个文件，返回文件信息和解析结果"""
    try:
        # 获取文件基本信息
        stat = file_path.stat()
        file_info = {
            'path': str(file_path),
            'name': file_path.name,
            'size': stat.st_size,
            'modified_time': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'hash': compute_file_hash(file_path)
        }

        # 解析文件内容
        parse_result = create_file_parser(file_path)

        if parse_result.is_success:
            file_info['data'] = parse_result.value
            file_info['parse_error'] = None
        else:
            file_info['data'] = None
            file_info['parse_error'] = str(parse_result.error)

        return Result(value=file_info)

    except Exception as e:
        return Result(error=e)

def batch_process_files(file_paths: List[Path]) -> Dict[str, Any]:
    """批量处理文件"""
    results = []
    errors = []

    for file_path in file_paths:
        result = process_file(file_path)
        if result.is_success:
            results.append(result.value)
        else:
            errors.append({
                'path': str(file_path),
                'error': str(result.error)
            })

    return {
        'success_count': len(results),
        'error_count': len(errors),
        'results': results,
        'errors': errors
    }

# =============================================================================
# 缓存操作函数
# =============================================================================

def get_cached_file_info(db: TinyDB, file_path: str) -> Optional[Dict[str, Any]]:
    """获取缓存的文件信息"""
    files_table = get_table(db, TableNames.CACHE_FILES)
    query = Query()
    result = files_table.search(query.path == file_path)
    return result[0] if result else None

def is_file_changed(file_path: Path, cached_info: Optional[Dict[str, Any]]) -> bool:
    """检查文件是否已更改"""
    if not cached_info:
        return True

    current_hash = compute_file_hash(file_path)
    return current_hash != cached_info.get('hash')

def update_file_cache(db: TinyDB, file_info: Dict[str, Any]) -> bool:
    """更新文件缓存"""
    try:
        files_table = get_table(db, TableNames.CACHE_FILES)
        query = Query()

        # 删除旧记录
        files_table.remove(query.path == file_info['path'])

        # 插入新记录
        files_table.insert(file_info)
        return True
    except Exception as e:
        logger = create_logger(__name__)
        logger.error(f"Failed to update cache for {file_info['path']}: {e}")
        return False

def batch_update_cache(db: TinyDB, file_infos: List[Dict[str, Any]]) -> Dict[str, int]:
    """批量更新缓存"""
    success_count = 0
    error_count = 0

    for file_info in file_infos:
        if update_file_cache(db, file_info):
            success_count += 1
        else:
            error_count += 1

    return {
        'success_count': success_count,
        'error_count': error_count
    }

# =============================================================================
# 扫描配置管理
# =============================================================================

def create_scan_config(name: str, path: str, patterns: List[str],
                      parser_func: Optional[Callable] = None,
                      watch: bool = True) -> Dict[str, Any]:
    """创建扫描配置"""
    return {
        'name': name,
        'path': Path(path),
        'patterns': patterns,
        'parser_func': parser_func,
        'watch': watch,
        'created_at': datetime.now().isoformat()
    }

def validate_scan_config(config: Dict[str, Any]) -> Result:
    """验证扫描配置"""
    required_fields = ['name', 'path', 'patterns']

    for field in required_fields:
        if field not in config:
            return Result(error=ValueError(f"Missing required field: {field}"))

    if not isinstance(config['patterns'], list):
        return Result(error=ValueError("Patterns must be a list"))

    if not config['path'].exists():
        return Result(error=ValueError(f"Path does not exist: {config['path']}"))

    return Result(value=config)

# =============================================================================
# 数据查询函数
# =============================================================================

def get_all_cached_files(db: TinyDB) -> List[Dict[str, Any]]:
    """获取所有缓存文件"""
    files_table = get_table(db, TableNames.CACHE_FILES)
    return files_table.all()

def search_files_by_pattern(db: TinyDB, pattern: str) -> List[Dict[str, Any]]:
    """按模式搜索文件"""
    files_table = get_table(db, TableNames.CACHE_FILES)
    query = Query()
    return files_table.search(query.name.matches(pattern))

def get_files_by_extension(db: TinyDB, extension: str) -> List[Dict[str, Any]]:
    """按扩展名获取文件"""
    files_table = get_table(db, TableNames.CACHE_FILES)
    query = Query()
    return files_table.search(query.path.matches(f"*.{extension}"))

def group_files_by_directory(files: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """按目录分组文件"""
    return group_by(lambda f: str(Path(f['path']).parent), files)

def filter_files_by_modification_time(files: List[Dict[str, Any]],
                                    since: datetime) -> List[Dict[str, Any]]:
    """按修改时间过滤文件"""
    since_str = since.isoformat()
    return [f for f in files if f.get('modified_time', '') > since_str]

# =============================================================================
# 文件监听
# =============================================================================

class FunctionalFileHandler(FileSystemEventHandler):
    """函数式文件事件处理器"""

    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

def create_file_watcher(directory: Path, callback: Callable[[str], None]) -> Observer:
    """创建文件监听器"""
    observer = Observer()
    handler = FunctionalFileHandler(callback)
    observer.schedule(handler, str(directory), recursive=True)
    return observer

def start_file_watcher(observer: Observer) -> bool:
    """启动文件监听器"""
    try:
        observer.start()
        return True
    except Exception as e:
        logger = create_logger(__name__)
        logger.error(f"Failed to start file watcher: {e}")
        return False

def stop_file_watcher(observer: Observer) -> bool:
    """停止文件监听器"""
    try:
        observer.stop()
        observer.join()
        return True
    except Exception as e:
        logger = create_logger(__name__)
        logger.error(f"Failed to stop file watcher: {e}")
        return False

# =============================================================================
# 高级扫描功能
# =============================================================================

def incremental_scan(db: TinyDB, directory: Path, patterns: List[str]) -> Dict[str, Any]:
    """增量扫描：只处理更改的文件"""
    files = scan_directory(directory, patterns)

    new_files = []
    changed_files = []
    unchanged_files = []

    for file_path in files:
        cached_info = get_cached_file_info(db, str(file_path))

        if not cached_info:
            new_files.append(file_path)
        elif is_file_changed(file_path, cached_info):
            changed_files.append(file_path)
        else:
            unchanged_files.append(file_path)

    # 处理新文件和更改的文件
    files_to_process = new_files + changed_files
    process_result = batch_process_files(files_to_process)

    # 更新缓存
    if process_result['results']:
        cache_result = batch_update_cache(db, process_result['results'])
    else:
        cache_result = {'success_count': 0, 'error_count': 0}

    return {
        'total_files': len(files),
        'new_files': len(new_files),
        'changed_files': len(changed_files),
        'unchanged_files': len(unchanged_files),
        'processed_files': process_result['success_count'],
        'process_errors': process_result['error_count'],
        'cache_updates': cache_result['success_count'],
        'cache_errors': cache_result['error_count']
    }

def full_scan(db: TinyDB, directory: Path, patterns: List[str]) -> Dict[str, Any]:
    """完整扫描：处理所有文件"""
    files = scan_directory(directory, patterns)
    process_result = batch_process_files(files)

    if process_result['results']:
        cache_result = batch_update_cache(db, process_result['results'])
    else:
        cache_result = {'success_count': 0, 'error_count': 0}

    return {
        'total_files': len(files),
        'processed_files': process_result['success_count'],
        'process_errors': process_result['error_count'],
        'cache_updates': cache_result['success_count'],
        'cache_errors': cache_result['error_count']
    }

# =============================================================================
# 数据库服务组合函数
# =============================================================================

def create_database_service(use_unified: bool = True) -> Dict[str, Any]:
    """创建数据库服务实例（函数式）"""
    db = get_database_connection(use_unified)

    return {
        'db': db,
        'scan_configs': {},
        'observers': {},
        'logger': create_logger('database_service')
    }

def add_scan_config_to_service(service: Dict[str, Any], config: Dict[str, Any]) -> Result:
    """向服务添加扫描配置"""
    validation_result = validate_scan_config(config)
    if validation_result.is_error:
        return validation_result

    service['scan_configs'][config['name']] = config

    # 如果启用监听，创建文件监听器
    if config.get('watch', False):
        def on_file_change(file_path: str):
            service['logger'].info(f"File changed: {file_path}")
            # 重新处理文件
            result = process_file(Path(file_path))
            if result.is_success:
                update_file_cache(service['db'], result.value)

        observer = create_file_watcher(config['path'], on_file_change)
        service['observers'][config['name']] = observer
        start_file_watcher(observer)

    return Result(value=service)

def scan_with_config(service: Dict[str, Any], config_name: str,
                    incremental: bool = True) -> Result:
    """使用配置执行扫描"""
    if config_name not in service['scan_configs']:
        return Result(error=ValueError(f"Scan config not found: {config_name}"))

    config = service['scan_configs'][config_name]

    try:
        if incremental:
            result = incremental_scan(service['db'], config['path'], config['patterns'])
        else:
            result = full_scan(service['db'], config['path'], config['patterns'])

        return Result(value=result)
    except Exception as e:
        return Result(error=e)

def cleanup_service(service: Dict[str, Any]) -> None:
    """清理服务资源"""
    for observer in service['observers'].values():
        stop_file_watcher(observer)
    service['observers'].clear()

# =============================================================================
# 导出的高级API
# =============================================================================

def initialize_database_service(configs: List[Dict[str, Any]],
                               use_unified: bool = True) -> Result:
    """初始化数据库服务"""
    service = create_database_service(use_unified)

    for config in configs:
        result = add_scan_config_to_service(service, config)
        if result.is_error:
            cleanup_service(service)
            return result

    return Result(value=service)

def execute_scan(service: Dict[str, Any], config_name: str,
                incremental: bool = True) -> Result:
    """执行扫描操作"""
    return scan_with_config(service, config_name, incremental)

def query_cached_data(service: Dict[str, Any],
                     filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """查询缓存数据"""
    files = get_all_cached_files(service['db'])

    if not filters:
        return files

    # 应用过滤器
    if 'extension' in filters:
        files = get_files_by_extension(service['db'], filters['extension'])

    if 'pattern' in filters:
        files = search_files_by_pattern(service['db'], filters['pattern'])

    if 'since' in filters:
        files = filter_files_by_modification_time(files, filters['since'])

    return files