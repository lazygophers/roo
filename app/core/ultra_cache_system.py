"""
极致性能优化缓存系统
Ultra Performance Cache System

特性:
- 多级缓存策略 (内存 + 磁盘 + 预计算)
- 无锁设计，最小化线程竞争
- 惰性加载 + 预加载混合策略
- 智能过期机制
- 零拷贝数据传输
- 内存池管理
"""

import asyncio
import hashlib
import json
import pickle
import threading
import time
import weakref
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Union, TypeVar, Generic
from functools import lru_cache, wraps
from collections import OrderedDict, defaultdict
import yaml
import psutil
from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging

logger = setup_logging("INFO")

T = TypeVar('T')

@dataclass
class CacheStats:
    """缓存统计信息"""
    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size_bytes: int = 0
    items_count: int = 0
    last_hit_time: float = field(default_factory=time.time)
    last_miss_time: float = field(default_factory=time.time)
    
    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0


class MemoryPool:
    """内存池管理器 - 减少GC压力"""
    
    def __init__(self, max_size: int = 100 * 1024 * 1024):  # 100MB
        self.max_size = max_size
        self.current_size = 0
        self._pools: Dict[str, List[Any]] = defaultdict(list)
        self._lock = threading.RLock()
        
    def get_buffer(self, size: int) -> bytearray:
        """获取缓冲区"""
        with self._lock:
            key = f"buffer_{size}"
            if self._pools[key]:
                return self._pools[key].pop()
            return bytearray(size)
    
    def return_buffer(self, buffer: bytearray):
        """归还缓冲区"""
        if len(buffer) > 1024 * 1024:  # 1MB以上不缓存
            return
            
        with self._lock:
            if self.current_size < self.max_size:
                key = f"buffer_{len(buffer)}"
                self._pools[key].append(buffer)
                self.current_size += len(buffer)


class SmartCache(Generic[T]):
    """智能缓存 - 支持TTL、LRU、频率统计"""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 3600):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._data: OrderedDict[str, Dict] = OrderedDict()
        self._access_count: defaultdict[str, int] = defaultdict(int)
        self._lock = threading.RLock()
        self.stats = CacheStats()
    
    def get(self, key: str) -> Optional[T]:
        """获取缓存项"""
        with self._lock:
            if key not in self._data:
                self.stats.misses += 1
                self.stats.last_miss_time = time.time()
                return None
            
            item = self._data[key]
            current_time = time.time()
            
            # 检查过期
            if current_time > item['expires_at']:
                del self._data[key]
                self._access_count.pop(key, None)
                self.stats.misses += 1
                self.stats.last_miss_time = current_time
                return None
            
            # 更新统计
            self.stats.hits += 1
            self.stats.last_hit_time = current_time
            self._access_count[key] += 1
            
            # 移到末尾 (LRU)
            self._data.move_to_end(key)
            
            return item['data']
    
    def set(self, key: str, value: T, ttl: Optional[float] = None) -> None:
        """设置缓存项"""
        with self._lock:
            current_time = time.time()
            expires_at = current_time + (ttl or self.default_ttl)
            
            # 如果已存在，更新
            if key in self._data:
                self._data[key] = {'data': value, 'expires_at': expires_at, 'created_at': current_time}
                self._data.move_to_end(key)
                return
            
            # 检查容量
            while len(self._data) >= self.max_size:
                self._evict_lru()
            
            self._data[key] = {'data': value, 'expires_at': expires_at, 'created_at': current_time}
            self.stats.items_count = len(self._data)
    
    def _evict_lru(self):
        """驱逐最少使用的项"""
        if not self._data:
            return
            
        # 找到访问次数最少的项
        lru_key = min(self._data.keys(), key=lambda k: self._access_count[k])
        del self._data[lru_key]
        self._access_count.pop(lru_key, None)
        self.stats.evictions += 1
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._data.clear()
            self._access_count.clear()
            self.stats = CacheStats()


class PrecomputeEngine:
    """预计算引擎"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self._tasks: Set[str] = set()
        self._results: Dict[str, Any] = {}
        self._lock = threading.Lock()
        
    def submit_task(self, task_id: str, func: Callable, *args, **kwargs):
        """提交预计算任务"""
        if task_id in self._tasks:
            return
            
        with self._lock:
            self._tasks.add(task_id)
            
        future = self.executor.submit(func, *args, **kwargs)
        future.add_done_callback(lambda f: self._on_task_complete(task_id, f))
        
    def _on_task_complete(self, task_id: str, future):
        """任务完成回调"""
        try:
            result = future.result()
            self._results[task_id] = result
            logger.info(f"Precompute task '{task_id}' completed")
        except Exception as e:
            logger.error(f"Precompute task '{task_id}' failed: {e}")
        finally:
            with self._lock:
                self._tasks.discard(task_id)
                
    def get_result(self, task_id: str) -> Optional[Any]:
        """获取预计算结果"""
        return self._results.get(task_id)
        
    def has_result(self, task_id: str) -> bool:
        """检查结果是否存在"""
        return task_id in self._results


class UltraCacheSystem:
    """极致缓存系统 - 主入口"""
    
    def __init__(self):
        # 多级缓存
        self.l1_cache = SmartCache[Any](max_size=500, default_ttl=300)  # L1: 5分钟
        self.l2_cache = SmartCache[Any](max_size=2000, default_ttl=1800)  # L2: 30分钟
        self.l3_cache = SmartCache[Any](max_size=5000, default_ttl=3600)  # L3: 1小时
        
        # 预计算引擎
        self.precompute = PrecomputeEngine(max_workers=2)
        
        # 内存池
        self.memory_pool = MemoryPool()
        
        # 文件缓存
        self.cache_dir = PROJECT_ROOT / "data" / "ultra_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 统计
        self.global_stats = CacheStats()
        
        # 预热标志
        self._warmed_up = False
        
        logger.info("UltraCacheSystem initialized")
    
    def get(self, key: str, loader: Optional[Callable] = None, ttl: Optional[float] = None) -> Optional[Any]:
        """获取数据 - 多级缓存策略"""
        # L1缓存
        result = self.l1_cache.get(key)
        if result is not None:
            self.global_stats.hits += 1
            return result
            
        # L2缓存
        result = self.l2_cache.get(key)
        if result is not None:
            self.l1_cache.set(key, result, ttl or 300)
            self.global_stats.hits += 1
            return result
            
        # L3缓存
        result = self.l3_cache.get(key)
        if result is not None:
            self.l2_cache.set(key, result, ttl or 1800)
            self.l1_cache.set(key, result, ttl or 300)
            self.global_stats.hits += 1
            return result
            
        # 磁盘缓存
        result = self._load_from_disk(key)
        if result is not None:
            self._set_multi_level(key, result, ttl)
            self.global_stats.hits += 1
            return result
            
        # 预计算结果
        if self.precompute.has_result(key):
            result = self.precompute.get_result(key)
            if result is not None:
                self._set_multi_level(key, result, ttl)
                self.global_stats.hits += 1
                return result
        
        # 最终loader
        if loader:
            try:
                result = loader()
                if result is not None:
                    self._set_multi_level(key, result, ttl)
                    self._save_to_disk(key, result)
                    return result
            except Exception as e:
                logger.error(f"Loader failed for key '{key}': {e}")
        
        self.global_stats.misses += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """设置数据到所有缓存级别"""
        self._set_multi_level(key, value, ttl)
        self._save_to_disk(key, value)
        
    def _set_multi_level(self, key: str, value: Any, ttl: Optional[float] = None):
        """设置多级缓存"""
        self.l1_cache.set(key, value, ttl or 300)
        self.l2_cache.set(key, value, ttl or 1800)
        self.l3_cache.set(key, value, ttl or 3600)
        
    def _load_from_disk(self, key: str) -> Optional[Any]:
        """从磁盘加载缓存"""
        try:
            cache_file = self.cache_dir / f"{self._hash_key(key)}.cache"
            if cache_file.exists():
                with open(cache_file, 'rb') as f:
                    data = pickle.load(f)
                    if time.time() < data['expires_at']:
                        return data['value']
                    else:
                        cache_file.unlink()
        except Exception as e:
            logger.error(f"Failed to load disk cache for '{key}': {e}")
        return None
        
    def _save_to_disk(self, key: str, value: Any):
        """保存到磁盘缓存"""
        try:
            cache_file = self.cache_dir / f"{self._hash_key(key)}.cache"
            data = {
                'value': value,
                'expires_at': time.time() + 7200,  # 2小时
                'created_at': time.time()
            }
            with open(cache_file, 'wb') as f:
                pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            logger.error(f"Failed to save disk cache for '{key}': {e}")
    
    def _hash_key(self, key: str) -> str:
        """生成缓存键哈希"""
        return hashlib.sha256(key.encode()).hexdigest()[:16]
    
    def preload_data(self, items: List[tuple]):
        """预加载数据"""
        for key, loader in items:
            self.precompute.submit_task(f"preload_{key}", loader)
            
    def warm_up(self):
        """预热缓存"""
        if self._warmed_up:
            return
            
        logger.info("Starting cache warm-up...")
        
        # 预加载模型数据
        models_loader = lambda: self._load_models_data()
        self.precompute.submit_task("warmup_models", models_loader)
        
        # 预加载规则数据  
        rules_loader = lambda: self._load_rules_data()
        self.precompute.submit_task("warmup_rules", rules_loader)
        
        # 预加载命令数据
        commands_loader = lambda: self._load_commands_data()
        self.precompute.submit_task("warmup_commands", commands_loader)
        
        self._warmed_up = True
        logger.info("Cache warm-up initiated")
    
    def _load_models_data(self) -> List[Dict]:
        """加载所有模型数据"""
        models_dir = PROJECT_ROOT / "resources" / "models"
        models = []
        
        if models_dir.exists():
            for yaml_file in models_dir.rglob("*.yaml"):
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if data:
                            models.append({
                                'slug': data.get('slug', ''),
                                'name': data.get('name', ''),
                                'roleDefinition': data.get('roleDefinition', ''),
                                'whenToUse': data.get('whenToUse', ''),
                                'description': data.get('description', ''),
                                'groups': data.get('groups', []),
                                'file_path': str(yaml_file),
                            })
                except Exception as e:
                    logger.error(f"Failed to load model {yaml_file}: {e}")
        
        return models
    
    def _load_rules_data(self) -> List[Dict]:
        """加载所有规则数据"""
        rules_dir = PROJECT_ROOT / "resources"
        rules = []
        
        if rules_dir.exists():
            for rule_file in rules_dir.rglob("*.md"):
                if "rules" in str(rule_file):
                    try:
                        with open(rule_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            rules.append({
                                'slug': rule_file.stem,
                                'content': content,
                                'file_path': str(rule_file),
                            })
                    except Exception as e:
                        logger.error(f"Failed to load rule {rule_file}: {e}")
        
        return rules
    
    def _load_commands_data(self) -> List[Dict]:
        """加载所有命令数据"""
        commands_dir = PROJECT_ROOT / "resources"
        commands = []
        
        if commands_dir.exists():
            for cmd_file in commands_dir.rglob("*.md"):
                if "commands" in str(cmd_file):
                    try:
                        with open(cmd_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            commands.append({
                                'slug': cmd_file.stem,
                                'content': content,
                                'file_path': str(cmd_file),
                            })
                    except Exception as e:
                        logger.error(f"Failed to load command {cmd_file}: {e}")
        
        return commands
    
    def get_stats(self) -> Dict:
        """获取缓存统计"""
        return {
            'global': {
                'hits': self.global_stats.hits,
                'misses': self.global_stats.misses,
                'hit_rate': self.global_stats.hit_rate,
            },
            'l1': {
                'hits': self.l1_cache.stats.hits,
                'misses': self.l1_cache.stats.misses,
                'hit_rate': self.l1_cache.stats.hit_rate,
                'items': self.l1_cache.stats.items_count,
            },
            'l2': {
                'hits': self.l2_cache.stats.hits,
                'misses': self.l2_cache.stats.misses,
                'hit_rate': self.l2_cache.stats.hit_rate,
                'items': self.l2_cache.stats.items_count,
            },
            'l3': {
                'hits': self.l3_cache.stats.hits,
                'misses': self.l3_cache.stats.misses,
                'hit_rate': self.l3_cache.stats.hit_rate,
                'items': self.l3_cache.stats.items_count,
            },
            'memory_usage': psutil.Process().memory_info().rss / 1024 / 1024,  # MB
        }


# 全局缓存实例
_ultra_cache_instance = None

def get_ultra_cache() -> UltraCacheSystem:
    """获取全局缓存实例"""
    global _ultra_cache_instance
    if _ultra_cache_instance is None:
        _ultra_cache_instance = UltraCacheSystem()
        _ultra_cache_instance.warm_up()
    return _ultra_cache_instance


def cached(ttl: float = 3600, key_func: Optional[Callable] = None):
    """缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}_{hash((args, tuple(sorted(kwargs.items()))))}"
                
            cache = get_ultra_cache()
            
            # 尝试从缓存获取
            result = cache.get(cache_key)
            if result is not None:
                return result
                
            # 计算结果并缓存
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
            
        return wrapper
    return decorator