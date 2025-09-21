"""
函数式编程基础工具和组合子

提供函数组合、管道操作、错误处理等基础函数式编程工具
"""

from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from functools import partial, reduce, wraps
import asyncio
from pathlib import Path
import hashlib
import yaml
import json
import logging

T = TypeVar('T')
U = TypeVar('U')

# =============================================================================
# 函数组合工具
# =============================================================================

def pipe(*functions):
    """函数管道：从左到右执行函数序列"""
    return lambda x: reduce(lambda acc, func: func(acc), functions, x)

def compose(*functions):
    """函数组合：从右到左执行函数序列"""
    return lambda x: reduce(lambda acc, func: func(acc), reversed(functions), x)

def curry(func):
    """柯里化装饰器"""
    @wraps(func)
    def curried(*args, **kwargs):
        if len(args) + len(kwargs) >= func.__code__.co_argcount:
            return func(*args, **kwargs)
        return partial(func, *args, **kwargs)
    return curried

# =============================================================================
# 错误处理
# =============================================================================

class Result:
    """表示可能失败的计算结果"""

    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        self._is_success = error is None

    @property
    def is_success(self) -> bool:
        return self._is_success

    @property
    def is_error(self) -> bool:
        return not self._is_success

    def map(self, func: Callable[[T], U]) -> 'Result':
        """成功时应用函数，失败时传递错误"""
        if self.is_success:
            try:
                return Result(value=func(self.value))
            except Exception as e:
                return Result(error=e)
        return Result(error=self.error)

    def flat_map(self, func: Callable[[T], 'Result']) -> 'Result':
        """成功时应用返回Result的函数，失败时传递错误"""
        if self.is_success:
            try:
                return func(self.value)
            except Exception as e:
                return Result(error=e)
        return Result(error=self.error)

    def or_else(self, default_value: T) -> T:
        """失败时返回默认值"""
        return self.value if self.is_success else default_value

    def unwrap(self) -> T:
        """获取值，失败时抛出异常"""
        if self.is_success:
            return self.value
        raise self.error

def safe(func: Callable) -> Callable[..., Result]:
    """将可能抛出异常的函数包装为返回Result的函数"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return Result(value=result)
        except Exception as e:
            return Result(error=e)
    return wrapper

async def safe_async(func: Callable) -> Callable[..., Result]:
    """异步版本的safe包装器"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            result = await func(*args, **kwargs)
            return Result(value=result)
        except Exception as e:
            return Result(error=e)
    return wrapper

# =============================================================================
# 文件处理函数
# =============================================================================

def read_file_content(file_path: Path) -> str:
    """读取文件内容"""
    return file_path.read_text(encoding='utf-8')

def parse_yaml_content(content: str) -> Dict[str, Any]:
    """解析YAML内容"""
    return yaml.safe_load(content)

def parse_json_content(content: str) -> Dict[str, Any]:
    """解析JSON内容"""
    return json.loads(content)

def compute_file_hash(file_path: Path) -> str:
    """计算文件MD5哈希"""
    return hashlib.md5(file_path.read_bytes()).hexdigest()

def get_file_extension(file_path: Path) -> str:
    """获取文件扩展名"""
    return file_path.suffix.lower()

# 组合文件处理管道
safe_read_file = safe(read_file_content)
safe_parse_yaml = safe(parse_yaml_content)
safe_parse_json = safe(parse_json_content)
safe_compute_hash = safe(compute_file_hash)

def create_file_parser(file_path: Path) -> Result:
    """创建文件解析器管道"""
    extension = get_file_extension(file_path)

    if extension in ['.yaml', '.yml']:
        parser = pipe(safe_read_file, lambda r: r.flat_map(safe_parse_yaml))
    elif extension == '.json':
        parser = pipe(safe_read_file, lambda r: r.flat_map(safe_parse_json))
    else:
        return Result(error=ValueError(f"Unsupported file extension: {extension}"))

    return parser(file_path)

# =============================================================================
# 数据处理工具
# =============================================================================

def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个字典"""
    return reduce(lambda a, b: {**a, **b}, dicts, {})

def filter_dict(predicate: Callable, data: Dict[str, Any]) -> Dict[str, Any]:
    """过滤字典"""
    return {k: v for k, v in data.items() if predicate(k, v)}

def map_dict_values(func: Callable, data: Dict[str, Any]) -> Dict[str, Any]:
    """映射字典值"""
    return {k: func(v) for k, v in data.items()}

def group_by(key_func: Callable, items: List[T]) -> Dict[str, List[T]]:
    """按键函数分组"""
    result = {}
    for item in items:
        key = key_func(item)
        if key not in result:
            result[key] = []
        result[key].append(item)
    return result

# =============================================================================
# 缓存工具
# =============================================================================

def create_cache_key(*args, **kwargs) -> str:
    """创建缓存键"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend(f"{k}={v}" for k, v in sorted(kwargs.items()))
    return hashlib.md5("|".join(key_parts).encode()).hexdigest()

def memoize(func: Callable) -> Callable:
    """记忆化装饰器"""
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = create_cache_key(*args, **kwargs)
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    return wrapper

# =============================================================================
# 配置处理
# =============================================================================

def validate_config(schema: Dict[str, Any], config: Dict[str, Any]) -> Result:
    """验证配置"""
    try:
        # 简单的配置验证逻辑
        for key, value_type in schema.items():
            if key in config:
                if not isinstance(config[key], value_type):
                    return Result(error=ValueError(f"Invalid type for {key}: expected {value_type}"))
        return Result(value=config)
    except Exception as e:
        return Result(error=e)

def transform_config(transformers: List[Callable], config: Dict[str, Any]) -> Dict[str, Any]:
    """应用配置转换器列表"""
    return reduce(lambda acc, transformer: transformer(acc), transformers, config)

def set_default_values(defaults: Dict[str, Any]) -> Callable:
    """设置默认值的转换器"""
    return lambda config: merge_dicts(defaults, config)

def normalize_keys(key_transformer: Callable[[str], str]) -> Callable:
    """规范化键名的转换器"""
    return lambda config: {key_transformer(k): v for k, v in config.items()}

# =============================================================================
# 日志工具
# =============================================================================

def create_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """创建配置好的日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger

def log_result(logger: logging.Logger, operation: str) -> Callable:
    """记录操作结果的装饰器工厂"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                logger.info(f"{operation} succeeded")
                return result
            except Exception as e:
                logger.error(f"{operation} failed: {e}")
                raise
        return wrapper
    return decorator

# =============================================================================
# 异步工具
# =============================================================================

async def parallel_map(func: Callable, items: List[T]) -> List[U]:
    """并行映射异步函数"""
    tasks = [func(item) for item in items]
    return await asyncio.gather(*tasks)

async def safe_parallel_map(func: Callable, items: List[T]) -> List[Result]:
    """安全的并行映射，返回Result列表"""
    async def safe_func(item):
        try:
            result = await func(item)
            return Result(value=result)
        except Exception as e:
            return Result(error=e)

    tasks = [safe_func(item) for item in items]
    return await asyncio.gather(*tasks)