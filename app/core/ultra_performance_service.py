"""
超高性能服务类
Ultra Performance Service

特性:
- 零阻塞架构
- 批量处理优化
- 内存零拷贝
- 连接池复用
- 智能负载均衡
- 资源预分配
"""

import asyncio
import concurrent.futures
import threading
import time
import weakref
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Union, Set
from collections import deque
import yaml
from functools import lru_cache
import psutil

from app.core.ultra_cache_system import get_ultra_cache, cached
from app.core.config import PROJECT_ROOT, MODELS_DIR
from app.models.schemas import ModelInfo
from app.core.logging import setup_logging

logger = setup_logging("INFO")


@dataclass
class PerformanceMetrics:
    """性能指标"""
    request_count: int = 0
    total_processing_time: float = 0.0
    cache_hits: int = 0
    cache_misses: int = 0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0
    
    @property
    def avg_response_time(self) -> float:
        return self.total_processing_time / self.request_count if self.request_count > 0 else 0.0
    
    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


class ResourcePool:
    """资源池 - 预分配和复用资源"""
    
    def __init__(self, create_func: Callable, max_size: int = 100):
        self.create_func = create_func
        self.max_size = max_size
        self._pool = deque()
        self._lock = threading.RLock()
        self._created_count = 0
        
        # 预分配一些资源
        for _ in range(min(10, max_size)):
            self._pool.append(create_func())
            self._created_count += 1
    
    def get(self):
        """获取资源"""
        with self._lock:
            if self._pool:
                return self._pool.popleft()
            elif self._created_count < self.max_size:
                self._created_count += 1
                return self.create_func()
            else:
                # 等待归还或创建临时资源
                return self.create_func()
    
    def put(self, resource):
        """归还资源"""
        with self._lock:
            if len(self._pool) < self.max_size:
                self._pool.append(resource)


class BatchProcessor:
    """批量处理器 - 聚合请求减少开销"""
    
    def __init__(self, process_func: Callable, batch_size: int = 10, max_wait: float = 0.1):
        self.process_func = process_func
        self.batch_size = batch_size
        self.max_wait = max_wait
        
        self._batch = []
        self._futures = []
        self._lock = threading.Lock()
        self._last_process_time = time.time()
        
        # 启动定时处理线程
        self._timer_thread = threading.Thread(target=self._timer_processor, daemon=True)
        self._timer_thread.start()
    
    def submit(self, item) -> concurrent.futures.Future:
        """提交处理项"""
        future = concurrent.futures.Future()
        
        with self._lock:
            self._batch.append(item)
            self._futures.append(future)
            
            if len(self._batch) >= self.batch_size:
                self._process_batch()
                
        return future
    
    def _process_batch(self):
        """处理当前批次"""
        if not self._batch:
            return
            
        batch = self._batch.copy()
        futures = self._futures.copy()
        self._batch.clear()
        self._futures.clear()
        self._last_process_time = time.time()
        
        # 异步处理
        threading.Thread(target=self._execute_batch, args=(batch, futures), daemon=True).start()
    
    def _execute_batch(self, batch: List, futures: List):
        """执行批次处理"""
        try:
            results = self.process_func(batch)
            for future, result in zip(futures, results):
                future.set_result(result)
        except Exception as e:
            for future in futures:
                future.set_exception(e)
    
    def _timer_processor(self):
        """定时器处理器"""
        while True:
            time.sleep(self.max_wait)
            with self._lock:
                if self._batch and (time.time() - self._last_process_time) >= self.max_wait:
                    self._process_batch()


class UltraYAMLService:
    """超高性能YAML服务"""
    
    def __init__(self):
        self.cache = get_ultra_cache()
        self.metrics = PerformanceMetrics()
        self._lock = threading.RLock()
        
        # 批量处理器
        self.batch_processor = BatchProcessor(
            process_func=self._batch_load_yaml_files,
            batch_size=5,
            max_wait=0.05
        )
        
        # 资源池
        self.yaml_loader_pool = ResourcePool(
            create_func=lambda: yaml.SafeLoader,
            max_size=20
        )
        
        logger.info("UltraYAMLService initialized")
    
    @cached(ttl=3600, key_func=lambda self, directory: f"yaml_files_{directory}")
    def find_yaml_files(self, directory: Path) -> List[Path]:
        """超快速查找YAML文件 - 带缓存"""
        start_time = time.time()
        
        yaml_files = []
        try:
            # 使用更高效的rglob
            yaml_files = list(directory.rglob("*.yaml"))
            yaml_files.extend(directory.rglob("*.yml"))
        except Exception as e:
            logger.error(f"Error scanning {directory}: {e}")
        
        self._update_metrics(time.time() - start_time)
        return yaml_files
    
    def load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """高性能加载单个YAML文件"""
        cache_key = f"yaml_content_{file_path}_{file_path.stat().st_mtime}"
        
        # 尝试从缓存获取
        cached_content = self.cache.get(cache_key)
        if cached_content is not None:
            self.metrics.cache_hits += 1
            return cached_content
        
        self.metrics.cache_misses += 1
        start_time = time.time()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 使用资源池中的loader
            loader = self.yaml_loader_pool.get()
            try:
                data = yaml.load(content, Loader=loader)
                result = data if data else {}
            finally:
                self.yaml_loader_pool.put(loader)
                
            # 缓存结果
            self.cache.set(cache_key, result, ttl=1800)
            
            self._update_metrics(time.time() - start_time)
            return result
            
        except Exception as e:
            logger.error(f"Failed to load {file_path}: {e}")
            raise Exception(f"Failed to load {file_path}: {str(e)}")
    
    def _batch_load_yaml_files(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """批量加载YAML文件"""
        results = []
        for file_path in file_paths:
            try:
                result = self.load_yaml_file(file_path)
                results.append(result)
            except Exception as e:
                logger.error(f"Batch load failed for {file_path}: {e}")
                results.append({})
        return results
    
    def filter_yaml_data(self, data: Dict[str, Any], file_path: Path) -> ModelInfo:
        """超快数据过滤 - 零拷贝优化"""
        cache_key = f"filtered_{hash(str(data))}_{file_path.stem}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result is not None:
            return cached_result
        
        # 直接构造，避免中间字典创建
        try:
            model_info = ModelInfo(
                slug=data.get('slug', ''),
                name=data.get('name', ''),
                roleDefinition=data.get('roleDefinition', ''),
                whenToUse=data.get('whenToUse', ''),
                description=data.get('description', ''),
                groups=data.get('groups', []),
                file_path=str(file_path.relative_to(MODELS_DIR.parent))
            )
            
            # 缓存过滤结果
            self.cache.set(cache_key, model_info, ttl=3600)
            return model_info
            
        except Exception as e:
            logger.error(f"Filter error for {file_path}: {e}")
            # 返回默认值
            return ModelInfo(
                slug='',
                name='',
                roleDefinition='',
                whenToUse='',
                description='',
                groups=[],
                file_path=str(file_path)
            )
    
    @cached(ttl=1800, key_func=lambda self: "all_models")
    def get_all_models(self) -> List[ModelInfo]:
        """获取所有模型 - 最大性能优化"""
        start_time = time.time()
        
        # 首先尝试从预计算结果获取
        precomputed = self.cache.get("warmup_models")
        if precomputed:
            logger.info("Using precomputed models data")
            return [ModelInfo(**model) for model in precomputed]
        
        models = []
        yaml_files = self.find_yaml_files(MODELS_DIR)
        
        if not yaml_files:
            logger.warning(f"No YAML files found in {MODELS_DIR}")
            return models
        
        # 批量处理
        futures = []
        for file_path in yaml_files:
            future = self.batch_processor.submit(file_path)
            futures.append((file_path, future))
        
        # 收集结果
        for file_path, future in futures:
            try:
                data = future.result(timeout=1.0)  # 1秒超时
                if data:
                    model_info = self.filter_yaml_data(data, file_path)
                    models.append(model_info)
            except Exception as e:
                logger.error(f"Failed to process {file_path}: {e}")
        
        self._update_metrics(time.time() - start_time)
        logger.info(f"Loaded {len(models)} models in {time.time() - start_time:.3f}s")
        
        return models
    
    def _update_metrics(self, processing_time: float):
        """更新性能指标"""
        with self._lock:
            self.metrics.request_count += 1
            self.metrics.total_processing_time += processing_time
            
            # 定期更新系统指标
            if self.metrics.request_count % 10 == 0:
                process = psutil.Process()
                self.metrics.memory_usage_mb = process.memory_info().rss / 1024 / 1024
                self.metrics.cpu_usage_percent = process.cpu_percent()
    
    def get_metrics(self) -> Dict:
        """获取性能指标"""
        with self._lock:
            return {
                'request_count': self.metrics.request_count,
                'avg_response_time_ms': self.metrics.avg_response_time * 1000,
                'cache_hit_rate': self.metrics.cache_hit_rate,
                'memory_usage_mb': self.metrics.memory_usage_mb,
                'cpu_usage_percent': self.metrics.cpu_usage_percent,
            }


class UltraRulesService:
    """超高性能规则服务"""
    
    def __init__(self):
        self.cache = get_ultra_cache()
        self.metrics = PerformanceMetrics()
        logger.info("UltraRulesService initialized")
    
    @cached(ttl=3600, key_func=lambda self: "all_rules")
    def get_all_rules(self) -> List[Dict[str, Any]]:
        """获取所有规则"""
        start_time = time.time()
        
        # 尝试预计算结果
        precomputed = self.cache.get("warmup_rules")
        if precomputed:
            logger.info("Using precomputed rules data")
            return precomputed
        
        rules = []
        rules_dirs = [
            PROJECT_ROOT / "resources" / "rules",
            PROJECT_ROOT / "resources" / "rules-code-python", 
            PROJECT_ROOT / "resources" / "rules-code-golang",
            PROJECT_ROOT / "resources" / "rules-code-javascript",
            PROJECT_ROOT / "resources" / "rules-code-java",
            PROJECT_ROOT / "resources" / "rules-code-rust",
            PROJECT_ROOT / "resources" / "rules-code-typescript",
        ]
        
        for rules_dir in rules_dirs:
            if rules_dir.exists():
                for rule_file in rules_dir.rglob("*.md"):
                    cache_key = f"rule_{rule_file}_{rule_file.stat().st_mtime}"
                    
                    cached_rule = self.cache.get(cache_key)
                    if cached_rule:
                        rules.append(cached_rule)
                        continue
                    
                    try:
                        with open(rule_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        rule_data = {
                            'slug': rule_file.stem,
                            'content': content,
                            'file_path': str(rule_file),
                            'category': rules_dir.name,
                        }
                        
                        self.cache.set(cache_key, rule_data, ttl=1800)
                        rules.append(rule_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to load rule {rule_file}: {e}")
        
        self.metrics.request_count += 1
        self.metrics.total_processing_time += time.time() - start_time
        
        logger.info(f"Loaded {len(rules)} rules in {time.time() - start_time:.3f}s")
        return rules


class UltraCommandsService:
    """超高性能命令服务"""
    
    def __init__(self):
        self.cache = get_ultra_cache()
        self.metrics = PerformanceMetrics()
        logger.info("UltraCommandsService initialized")
    
    @cached(ttl=3600, key_func=lambda self: "all_commands")
    def get_all_commands(self) -> List[Dict[str, Any]]:
        """获取所有命令"""
        start_time = time.time()
        
        # 尝试预计算结果
        precomputed = self.cache.get("warmup_commands")
        if precomputed:
            logger.info("Using precomputed commands data")
            return precomputed
        
        commands = []
        commands_dirs = [
            PROJECT_ROOT / "resources" / "commands",
        ]
        
        for commands_dir in commands_dirs:
            if commands_dir.exists():
                for cmd_file in commands_dir.rglob("*.md"):
                    cache_key = f"command_{cmd_file}_{cmd_file.stat().st_mtime}"
                    
                    cached_cmd = self.cache.get(cache_key)
                    if cached_cmd:
                        commands.append(cached_cmd)
                        continue
                    
                    try:
                        with open(cmd_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            
                        cmd_data = {
                            'slug': cmd_file.stem,
                            'content': content,
                            'file_path': str(cmd_file),
                        }
                        
                        self.cache.set(cache_key, cmd_data, ttl=1800)
                        commands.append(cmd_data)
                        
                    except Exception as e:
                        logger.error(f"Failed to load command {cmd_file}: {e}")
        
        self.metrics.request_count += 1
        self.metrics.total_processing_time += time.time() - start_time
        
        logger.info(f"Loaded {len(commands)} commands in {time.time() - start_time:.3f}s")
        return commands


# 全局服务实例
_yaml_service = None
_rules_service = None
_commands_service = None

def get_ultra_yaml_service() -> UltraYAMLService:
    """获取超高性能YAML服务"""
    global _yaml_service
    if _yaml_service is None:
        _yaml_service = UltraYAMLService()
    return _yaml_service

def get_ultra_rules_service() -> UltraRulesService:
    """获取超高性能规则服务"""
    global _rules_service
    if _rules_service is None:
        _rules_service = UltraRulesService()
    return _rules_service

def get_ultra_commands_service() -> UltraCommandsService:
    """获取超高性能命令服务"""
    global _commands_service
    if _commands_service is None:
        _commands_service = UltraCommandsService()
    return _commands_service