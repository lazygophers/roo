import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from tinydb import TinyDB, Query
from functools import lru_cache
import yaml
from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging
from app.core.unified_database import get_unified_database, TableNames

logger = setup_logging("INFO")

class LiteDatabaseService:
    """轻量级数据库服务
    
    性能优化特性:
    1. 无文件监控 - 移除watchdog依赖
    2. 按需检查 - 只在API调用时检查文件变化
    3. 内存缓存 - 减少磁盘I/O
    4. 简化数据结构 - 只存储必要数据
    """
    
    def __init__(self, use_unified_db: bool = True):
        """初始化轻量级数据库服务"""
        self.use_unified_db = use_unified_db
        
        if use_unified_db:
            self.unified_db = get_unified_database()
            self.db = self.unified_db.db
            self.db_path = self.unified_db.db_path
        else:
            # 兼容模式：使用独立数据库文件
            db_dir = PROJECT_ROOT / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "lite_cache.db")
            self.db_path = db_path
            self.db = TinyDB(db_path)
            self.unified_db = None
        
        self._memory_cache = {}
        self._cache_timestamps = {}
        self._cache_ttl = 300  # 5分钟缓存TTL
        
        # 使用统一表名
        self.models_table = self.db.table(TableNames.LITE_MODELS)
        self.metadata_table = self.db.table(TableNames.LITE_METADATA)
        
        logger.info(f"LiteDatabaseService initialized with unified db: {use_unified_db}")
    
    def _get_file_hash(self, file_path: Path) -> str:
        """快速计算文件哈希（只读取前1KB）"""
        try:
            with open(file_path, 'rb') as f:
                # 只读取文件开头，大幅提升性能
                content = f.read(1024)
                return hashlib.md5(content).hexdigest()[:16]  # 缩短哈希长度
        except Exception:
            return ""
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查内存缓存是否有效"""
        if cache_key not in self._memory_cache:
            return False
        
        timestamp = self._cache_timestamps.get(cache_key, 0)
        current_time = datetime.now().timestamp()
        
        return (current_time - timestamp) < self._cache_ttl
    
    def _set_cache(self, cache_key: str, data: Any):
        """设置内存缓存"""
        self._memory_cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now().timestamp()
        
        # 简单的缓存清理
        if len(self._memory_cache) > 100:
            oldest_key = min(self._cache_timestamps.keys(), 
                           key=lambda k: self._cache_timestamps[k])
            self._memory_cache.pop(oldest_key, None)
            self._cache_timestamps.pop(oldest_key, None)
    
    def _get_cache(self, cache_key: str) -> Optional[Any]:
        """获取内存缓存"""
        if self._is_cache_valid(cache_key):
            return self._memory_cache[cache_key]
        return None
    
    @lru_cache(maxsize=64)
    def _parse_yaml_file(self, file_path_str: str, file_mtime: float) -> Dict[str, Any]:
        """解析YAML文件（带LRU缓存）"""
        file_path = Path(file_path_str)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                # 只保留核心字段，减少内存使用
                if isinstance(data, dict):
                    core_data = {
                        'slug': data.get('slug', ''),
                        'name': data.get('name', ''),
                        'roleDefinition': data.get('roleDefinition', '')[:200],  # 截断长文本
                        'whenToUse': data.get('whenToUse', '')[:100],
                        'description': data.get('description', '')[:100],
                        'groups': data.get('groups', [])[:5]  # 限制数组长度
                    }
                    return core_data
                return {}
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return {}
    
    def get_models_data(self, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """获取模型数据（带缓存优化）"""
        cache_key = "all_models"
        
        # 检查内存缓存
        if not force_refresh:
            cached_data = self._get_cache(cache_key)
            if cached_data is not None:
                return cached_data
        
        models_dir = PROJECT_ROOT / "resources" / "models"
        if not models_dir.exists():
            return []
        
        models_data = []
        
        # 快速扫描文件
        for file_path in models_dir.rglob("*.yaml"):
            try:
                file_stats = file_path.stat()
                file_mtime = file_stats.st_mtime
                
                # 解析文件内容
                yaml_data = self._parse_yaml_file(str(file_path), file_mtime)
                if yaml_data and yaml_data.get('slug'):
                    # 添加文件信息
                    yaml_data['file_path'] = str(file_path.relative_to(PROJECT_ROOT))
                    yaml_data['file_size'] = file_stats.st_size
                    yaml_data['last_modified'] = int(file_mtime)
                    
                    models_data.append(yaml_data)
                    
            except Exception as e:
                logger.warning(f"Skipped {file_path}: {e}")
                continue
        
        # 排序
        models_data.sort(key=lambda x: x.get('slug', ''))
        
        # 更新缓存
        self._set_cache(cache_key, models_data)
        
        logger.info(f"Loaded {len(models_data)} models")
        return models_data
    
    def get_model_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """根据slug获取单个模型（优化查找）"""
        cache_key = f"model_{slug}"
        
        # 检查缓存
        cached_model = self._get_cache(cache_key)
        if cached_model is not None:
            return cached_model
        
        # 快速查找：先检查所有模型的缓存
        all_models = self.get_models_data()
        for model in all_models:
            if model.get('slug') == slug:
                self._set_cache(cache_key, model)
                return model
        
        return None
    
    def get_models_by_group(self, group: str) -> List[Dict[str, Any]]:
        """根据组获取模型"""
        cache_key = f"group_{group}"
        
        # 检查缓存
        cached_models = self._get_cache(cache_key)
        if cached_models is not None:
            return cached_models
        
        all_models = self.get_models_data()
        group_models = []
        
        for model in all_models:
            groups = model.get('groups', [])
            if isinstance(groups, list) and group in groups:
                group_models.append(model)
        
        self._set_cache(cache_key, group_models)
        return group_models
    
    def refresh_models_cache(self) -> Dict[str, int]:
        """刷新模型缓存"""
        # 清除相关缓存
        cache_keys_to_remove = [key for key in self._memory_cache.keys() 
                               if key.startswith(('all_models', 'model_', 'group_'))]
        
        for key in cache_keys_to_remove:
            self._memory_cache.pop(key, None)
            self._cache_timestamps.pop(key, None)
        
        # 清除LRU缓存
        self._parse_yaml_file.cache_clear()
        
        # 重新加载
        models_data = self.get_models_data(force_refresh=True)
        
        return {
            'total_models': len(models_data),
            'cache_cleared': len(cache_keys_to_remove)
        }
    
    def get_hooks_data(self) -> Dict[str, str]:
        """获取hooks数据（简化版本）"""
        cache_key = "hooks_data"
        
        cached_data = self._get_cache(cache_key)
        if cached_data is not None:
            return cached_data
        
        hooks_dir = PROJECT_ROOT / "resources" / "hooks"
        hooks_data = {}
        
        if hooks_dir.exists():
            for file_path in hooks_dir.glob("*.md"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        # 只存储文件名和内容，简化数据结构
                        hooks_data[file_path.stem] = content[:1000]  # 限制内容长度
                except Exception as e:
                    logger.warning(f"Failed to load hook {file_path}: {e}")
        
        self._set_cache(cache_key, hooks_data)
        return hooks_data
    
    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        cache_info = self._parse_yaml_file.cache_info()
        
        return {
            'service_type': 'LiteDatabaseService',
            'db_path': self.db_path,
            'memory_cache_size': len(self._memory_cache),
            'lru_cache_hits': cache_info.hits,
            'lru_cache_misses': cache_info.misses,
            'lru_cache_size': cache_info.currsize,
            'uptime': 'running'
        }
    
    def clear_all_cache(self):
        """清除所有缓存"""
        self._memory_cache.clear()
        self._cache_timestamps.clear()
        self._parse_yaml_file.cache_clear()
        logger.info("All caches cleared")
    
    def close(self):
        """关闭服务"""
        self.clear_all_cache()
        if not self.use_unified_db:
            # 只有非统一数据库模式才需要手动关闭
            self.db.close()
        logger.info("LiteDatabaseService closed")


# 全局轻量级数据库服务实例
_lite_db_service = None

def get_lite_database_service(use_unified_db: bool = True) -> LiteDatabaseService:
    """获取轻量级数据库服务实例"""
    global _lite_db_service
    if _lite_db_service is None:
        _lite_db_service = LiteDatabaseService(use_unified_db=use_unified_db)
    return _lite_db_service

def init_lite_database_service(use_unified_db: bool = True) -> LiteDatabaseService:
    """初始化轻量级数据库服务（快速启动）"""
    logger.info("Initializing lite database service...")
    
    db_service = get_lite_database_service(use_unified_db=use_unified_db)
    
    # 不执行全量同步，按需加载
    logger.info(f"Lite database service initialized (unified_db: {use_unified_db}, lazy loading enabled)")
    
    return db_service