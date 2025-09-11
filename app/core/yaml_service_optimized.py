import os
import yaml
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import lru_cache
from datetime import datetime, timedelta
from app.models.schemas import ModelInfo
from app.core.config import MODELS_DIR


class OptimizedYAMLService:
    """优化的YAML文件处理服务
    
    性能优化特性:
    1. 懒加载 - 按需加载文件
    2. LRU缓存 - 缓存最近使用的文件
    3. 文件修改时间检查 - 避免重复解析
    4. 批量操作 - 减少I/O次数
    """
    
    def __init__(self, cache_size: int = 128):
        """初始化服务
        
        Args:
            cache_size: LRU缓存大小
        """
        self._cache_size = cache_size
        self._file_cache = {}
        self._file_stats = {}
        self._last_scan_time = None
        self._scan_cache_duration = 60  # 秒
    
    def _get_file_modification_time(self, file_path: Path) -> float:
        """获取文件修改时间"""
        try:
            return file_path.stat().st_mtime
        except:
            return 0.0
    
    def _is_file_cached_and_valid(self, file_path: Path) -> bool:
        """检查文件是否已缓存且有效"""
        file_key = str(file_path)
        if file_key not in self._file_cache:
            return False
        
        current_mtime = self._get_file_modification_time(file_path)
        cached_mtime = self._file_stats.get(file_key, 0.0)
        
        return current_mtime <= cached_mtime
    
    @lru_cache(maxsize=128)
    def _load_yaml_file_cached(self, file_path_str: str, file_mtime: float) -> Dict[str, Any]:
        """使用LRU缓存加载YAML文件
        
        Args:
            file_path_str: 文件路径字符串
            file_mtime: 文件修改时间（用于缓存失效）
        """
        file_path = Path(file_path_str)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            raise Exception(f"Failed to load {file_path}: {str(e)}")
    
    def load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """加载单个YAML文件（带缓存优化）"""
        file_key = str(file_path)
        
        # 检查缓存是否有效
        if self._is_file_cached_and_valid(file_path):
            return self._file_cache[file_key]
        
        # 加载文件
        current_mtime = self._get_file_modification_time(file_path)
        data = self._load_yaml_file_cached(str(file_path), current_mtime)
        
        # 更新缓存
        self._file_cache[file_key] = data
        self._file_stats[file_key] = current_mtime
        
        # 限制缓存大小（简单的LRU实现）
        if len(self._file_cache) > self._cache_size:
            # 移除最旧的条目
            oldest_key = min(self._file_stats.keys(), key=lambda k: self._file_stats[k])
            self._file_cache.pop(oldest_key, None)
            self._file_stats.pop(oldest_key, None)
        
        return data
    
    def find_yaml_files(self, directory: Path, use_cache: bool = True) -> List[Path]:
        """查找YAML文件（带缓存优化）"""
        # 检查扫描缓存
        current_time = datetime.now()
        if (use_cache and self._last_scan_time and 
            current_time - self._last_scan_time < timedelta(seconds=self._scan_cache_duration)):
            # 使用缓存的扫描结果
            cache_key = f"scan_{directory}"
            if hasattr(self, f"_scan_cache_{cache_key}"):
                return getattr(self, f"_scan_cache_{cache_key}")
        
        yaml_files = []
        
        # 优化：使用 Path.rglob 代替 os.walk
        for pattern in ['*.yaml', '*.yml']:
            yaml_files.extend(directory.rglob(pattern))
        
        # 缓存扫描结果
        if use_cache:
            cache_key = f"scan_{directory}"
            setattr(self, f"_scan_cache_{cache_key}", yaml_files)
            self._last_scan_time = current_time
            
        return yaml_files
    
    def filter_yaml_data(self, data: Dict[str, Any], file_path: Path) -> ModelInfo:
        """过滤YAML数据（优化内存使用）"""
        # 只提取需要的字段，减少内存占用
        filtered_data = {
            'slug': data.get('slug', ''),
            'name': data.get('name', ''),
            'roleDefinition': data.get('roleDefinition', '')[:500],  # 限制长度
            'whenToUse': data.get('whenToUse', '')[:300],
            'description': data.get('description', '')[:200],
            'groups': data.get('groups', [])[:10],  # 限制数组长度
            'file_path': str(file_path.relative_to(MODELS_DIR.parent))
        }
        
        return ModelInfo(**filtered_data)
    
    def load_model_by_slug(self, slug: str) -> Optional[ModelInfo]:
        """按slug加载单个模型（按需加载）"""
        yaml_files = self.find_yaml_files(MODELS_DIR)
        
        for file_path in yaml_files:
            try:
                # 快速检查：先读取文件开头几行查找slug
                with open(file_path, 'r', encoding='utf-8') as f:
                    first_lines = f.read(200)  # 只读取前200个字符
                    if f'slug: {slug}' not in first_lines and f'slug: "{slug}"' not in first_lines:
                        continue
                
                # 找到可能的文件，完整加载
                yaml_data = self.load_yaml_file(file_path)
                if yaml_data.get('slug') == slug:
                    return self.filter_yaml_data(yaml_data, file_path)
                    
            except Exception as e:
                continue
                
        return None
    
    def load_models_batch(self, slugs: List[str]) -> List[ModelInfo]:
        """批量加载模型（优化I/O）"""
        models = []
        remaining_slugs = set(slugs)
        yaml_files = self.find_yaml_files(MODELS_DIR)
        
        for file_path in yaml_files:
            if not remaining_slugs:
                break
                
            try:
                yaml_data = self.load_yaml_file(file_path)
                file_slug = yaml_data.get('slug', '')
                
                if file_slug in remaining_slugs:
                    model_info = self.filter_yaml_data(yaml_data, file_path)
                    models.append(model_info)
                    remaining_slugs.discard(file_slug)
                    
            except Exception:
                continue
        
        return models
    
    def load_all_models(self) -> List[ModelInfo]:
        """加载所有模型数据（优化版本）"""
        models = []
        yaml_files = self.find_yaml_files(MODELS_DIR)
        
        # 批量处理文件
        for file_path in yaml_files:
            try:
                yaml_data = self.load_yaml_file(file_path)
                model_info = self.filter_yaml_data(yaml_data, file_path)
                models.append(model_info)
                
            except Exception as e:
                # 记录错误但继续处理
                print(f"Warning: Could not process {file_path}: {str(e)}")
                continue
        
        # 按slug排序
        models.sort(key=lambda x: x.slug)
        return models
    
    def clear_cache(self):
        """清除所有缓存"""
        self._file_cache.clear()
        self._file_stats.clear()
        self._load_yaml_file_cached.cache_clear()
        self._last_scan_time = None
        
        # 清除动态扫描缓存
        for attr in list(dir(self)):
            if attr.startswith('_scan_cache_'):
                delattr(self, attr)
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存统计信息"""
        cache_info = self._load_yaml_file_cached.cache_info()
        return {
            'lru_cache_hits': cache_info.hits,
            'lru_cache_misses': cache_info.misses,
            'lru_cache_size': cache_info.currsize,
            'lru_cache_maxsize': cache_info.maxsize,
            'file_cache_size': len(self._file_cache),
            'file_stats_size': len(self._file_stats)
        }


# 全局优化服务实例
_optimized_yaml_service = None

def get_optimized_yaml_service(cache_size: int = 128) -> OptimizedYAMLService:
    """获取优化的YAML服务单例"""
    global _optimized_yaml_service
    if _optimized_yaml_service is None:
        _optimized_yaml_service = OptimizedYAMLService(cache_size=cache_size)
    return _optimized_yaml_service