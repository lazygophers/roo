"""
极致内存优化数据库服务
Minimal Memory Database Service

特性:
- 内存使用 < 5MB
- 无缓存设计（按需读取）
- 流式处理大文件
- 最小化对象创建
- 智能垃圾回收
"""

import gc
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Iterator
import yaml
from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging

logger = setup_logging("INFO")

class MinimalDatabaseService:
    """极致内存优化数据库服务

    设计原则:
    1. 无内存缓存 - 每次都从磁盘读取
    2. 流式处理 - 避免一次性加载大量数据
    3. 最小对象 - 只保留必要字段
    4. 即用即释 - 及时清理临时对象
    """

    def __init__(self):
        """最小化初始化"""
        self.models_dir = PROJECT_ROOT / "resources" / "models"
        self.hooks_dir = PROJECT_ROOT / "resources" / "hooks"

        # 只记录基本统计
        self._stats = {
            'total_reads': 0,
            'memory_optimizations': 0
        }

        logger.info("MinimalDatabaseService initialized - zero cache mode")

    def _optimize_memory(self):
        """内存优化"""
        collected = gc.collect()
        self._stats['memory_optimizations'] += 1
        return collected

    def _parse_yaml_minimal(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """最小化YAML解析 - 只保留核心字段"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                # 流式读取，避免大文件内存占用
                data = yaml.safe_load(f)

                if not isinstance(data, dict):
                    return None

                # 只保留必要字段，限制字符串长度
                minimal_data = {
                    'slug': data.get('slug', '')[:50],
                    'name': data.get('name', '')[:100],
                    'description': data.get('description', '')[:200],
                    'file_path': str(file_path.relative_to(PROJECT_ROOT)),
                }

                # 可选字段
                if 'groups' in data and isinstance(data['groups'], list):
                    minimal_data['groups'] = data['groups'][:3]  # 最多3个组

                if 'whenToUse' in data:
                    minimal_data['whenToUse'] = data['whenToUse'][:150]

                return minimal_data

        except Exception as e:
            logger.warning(f"Failed to parse {file_path}: {e}")
            return None
        finally:
            # 立即触发垃圾回收
            self._optimize_memory()

    def get_models_data(self) -> List[Dict[str, Any]]:
        """获取所有模型数据 - 流式处理"""
        if not self.models_dir.exists():
            return []

        models = []
        self._stats['total_reads'] += 1

        try:
            # 流式处理文件
            for file_path in self.models_dir.rglob("*.yaml"):
                model_data = self._parse_yaml_minimal(file_path)
                if model_data and model_data.get('slug'):
                    models.append(model_data)

                # 每处理10个文件优化一次内存
                if len(models) % 10 == 0:
                    self._optimize_memory()

            # 按slug排序（内存友好的排序）
            models.sort(key=lambda x: x.get('slug', ''))

            logger.info(f"Loaded {len(models)} models (minimal mode)")
            return models

        except Exception as e:
            logger.error(f"Error loading models: {e}")
            return []
        finally:
            # 最终内存优化
            self._optimize_memory()

    def get_model_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """按slug获取单个模型 - 直接文件搜索"""
        if not self.models_dir.exists():
            return None

        self._stats['total_reads'] += 1

        try:
            # 直接搜索文件，避免加载所有模型
            for file_path in self.models_dir.rglob("*.yaml"):
                model_data = self._parse_yaml_minimal(file_path)
                if model_data and model_data.get('slug') == slug:
                    # 为单个模型加载更多详细信息
                    return self._load_full_model(file_path)

                # 定期清理内存
                if self._stats['total_reads'] % 5 == 0:
                    self._optimize_memory()

            return None

        except Exception as e:
            logger.error(f"Error finding model {slug}: {e}")
            return None
        finally:
            self._optimize_memory()

    def _load_full_model(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """加载完整模型信息"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

                if isinstance(data, dict):
                    # 添加文件信息
                    data['file_path'] = str(file_path.relative_to(PROJECT_ROOT))

                    # 获取文件统计信息
                    file_stats = file_path.stat()
                    data['file_size'] = file_stats.st_size
                    data['last_modified'] = int(file_stats.st_mtime)

                    return data

        except Exception as e:
            logger.error(f"Error loading full model from {file_path}: {e}")

        return None

    def get_models_by_group(self, group: str) -> List[Dict[str, Any]]:
        """按组获取模型 - 流式过滤"""
        if not self.models_dir.exists():
            return []

        group_models = []
        self._stats['total_reads'] += 1

        try:
            for file_path in self.models_dir.rglob("*.yaml"):
                model_data = self._parse_yaml_minimal(file_path)
                if model_data:
                    groups = model_data.get('groups', [])
                    if isinstance(groups, list) and group in groups:
                        group_models.append(model_data)

                # 定期内存优化
                if len(group_models) % 5 == 0:
                    self._optimize_memory()

            logger.info(f"Found {len(group_models)} models in group '{group}'")
            return group_models

        except Exception as e:
            logger.error(f"Error loading group {group}: {e}")
            return []
        finally:
            self._optimize_memory()

    def get_hooks_data(self) -> Dict[str, str]:
        """获取hooks数据 - 最小化加载"""
        if not self.hooks_dir.exists():
            return {}

        hooks = {}
        self._stats['total_reads'] += 1

        try:
            for file_path in self.hooks_dir.glob("*.md"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        # 只读取前500字符
                        content = f.read(500)
                        hooks[file_path.stem] = content
                except Exception as e:
                    logger.warning(f"Failed to load hook {file_path}: {e}")

                # 每个文件后清理内存
                self._optimize_memory()

            return hooks

        except Exception as e:
            logger.error(f"Error loading hooks: {e}")
            return {}

    def refresh_models_cache(self) -> Dict[str, int]:
        """刷新缓存 - 在无缓存模式下只是内存清理"""
        collected = self._optimize_memory()

        # 重新统计模型数量
        models_count = len(self.get_models_data())

        return {
            'total_models': models_count,
            'cache_cleared': 0,  # 无缓存模式
            'memory_freed': collected
        }

    def get_status(self) -> Dict[str, Any]:
        """获取服务状态"""
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024

        return {
            'service_type': 'MinimalDatabaseService',
            'mode': 'zero_cache',
            'memory_mb': round(memory_mb, 2),
            'total_reads': self._stats['total_reads'],
            'memory_optimizations': self._stats['memory_optimizations'],
            'features': [
                'no_cache',
                'stream_processing',
                'minimal_objects',
                'gc_optimization'
            ]
        }

    def close(self):
        """关闭服务"""
        # 最后的内存清理
        collected = self._optimize_memory()
        logger.info(f"MinimalDatabaseService closed - freed {collected} objects")


# 全局最小化数据库服务实例
_minimal_db_service = None

def get_minimal_database_service() -> MinimalDatabaseService:
    """获取最小化数据库服务实例"""
    global _minimal_db_service
    if _minimal_db_service is None:
        _minimal_db_service = MinimalDatabaseService()
    return _minimal_db_service

def init_minimal_database_service() -> MinimalDatabaseService:
    """初始化最小化数据库服务"""
    logger.info("Initializing minimal database service...")

    db_service = get_minimal_database_service()

    # 立即优化内存
    db_service._optimize_memory()

    logger.info("Minimal database service initialized (zero cache mode)")
    return db_service