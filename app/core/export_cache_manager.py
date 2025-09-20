"""
导出文件缓存管理器
负责缓存导出的配置文件，避免重复生成
"""

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Any
from app.core.secure_logging import sanitize_for_log
import logging

logger = logging.getLogger(__name__)


class ExportCacheManager:
    """导出文件缓存管理器"""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        初始化缓存管理器

        Args:
            cache_dir: 缓存目录，默认为项目根目录下的data/temp文件夹
        """
        if cache_dir is None:
            # 默认使用项目根目录下的data/temp文件夹
            project_root = Path(__file__).parent.parent.parent
            cache_dir = project_root / "data" / "temp"

        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)

        # 缓存信息存储：{cache_key: {'filename': str, 'expire_time': datetime, 'access_time': datetime}}
        self.cache_info: Dict[str, Dict[str, Any]] = {}
        self.cache_lock = threading.RLock()

        # 默认缓存时间：30分钟
        self.default_cache_duration = timedelta(minutes=30)
        # 延长缓存时间：5分钟
        self.extend_cache_duration = timedelta(minutes=5)

        # 启动清理线程
        self._start_cleanup_thread()

    def _generate_cache_key(self, config_data: Dict[str, Any]) -> str:
        """
        根据配置数据生成缓存键

        Args:
            config_data: 配置数据

        Returns:
            缓存键（MD5哈希）
        """
        # 创建一个标准化的配置字符串用于生成hash
        normalized_config = {
            'selected_models': sorted(config_data.get('selected_models', [])),
            'selected_commands': sorted(config_data.get('selected_commands', [])),
            'selected_rules': sorted(config_data.get('selected_rules', [])),
            'selected_role': config_data.get('selected_role'),
            'deploy_targets': sorted(config_data.get('deploy_targets', [])),
            'model_rule_bindings': config_data.get('model_rule_bindings', [])
        }

        # 转换为JSON字符串并生成MD5哈希
        config_str = json.dumps(normalized_config, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(config_str.encode('utf-8')).hexdigest()

    def get_cached_file(self, config_data: Dict[str, Any]) -> Optional[str]:
        """
        获取缓存的文件

        Args:
            config_data: 配置数据

        Returns:
            缓存的文件名，如果不存在或已过期则返回None
        """
        cache_key = self._generate_cache_key(config_data)

        with self.cache_lock:
            if cache_key not in self.cache_info:
                return None

            cache_entry = self.cache_info[cache_key]
            current_time = datetime.now()

            # 检查是否过期
            if current_time > cache_entry['expire_time']:
                logger.info(f"缓存文件已过期: {sanitize_for_log(cache_entry['filename'])}")
                self._remove_cache_entry(cache_key)
                return None

            # 检查文件是否仍然存在
            file_path = self.cache_dir / cache_entry['filename']
            if not file_path.exists():
                logger.warning(f"缓存文件不存在: {sanitize_for_log(cache_entry['filename'])}")
                self._remove_cache_entry(cache_key)
                return None

            # 延长缓存时间并更新访问时间
            cache_entry['expire_time'] = current_time + self.extend_cache_duration
            cache_entry['access_time'] = current_time

            logger.info(f"使用缓存文件: {sanitize_for_log(cache_entry['filename'])}")
            return cache_entry['filename']

    def cache_file(self, config_data: Dict[str, Any], filename: str) -> str:
        """
        缓存文件

        Args:
            config_data: 配置数据
            filename: 文件名

        Returns:
            缓存键
        """
        cache_key = self._generate_cache_key(config_data)
        current_time = datetime.now()

        with self.cache_lock:
            self.cache_info[cache_key] = {
                'filename': filename,
                'expire_time': current_time + self.default_cache_duration,
                'access_time': current_time,
                'created_time': current_time
            }

        logger.info(f"文件已缓存: {sanitize_for_log(filename)}, 缓存键: {sanitize_for_log(cache_key)}")
        return cache_key

    def _remove_cache_entry(self, cache_key: str) -> None:
        """
        移除缓存条目及其文件

        Args:
            cache_key: 缓存键
        """
        if cache_key in self.cache_info:
            cache_entry = self.cache_info[cache_key]
            filename = cache_entry['filename']

            # 删除文件
            file_path = self.cache_dir / filename
            try:
                if file_path.exists():
                    file_path.unlink()
                    logger.info(f"已删除缓存文件: {sanitize_for_log(filename)}")
            except Exception as e:
                logger.error(f"删除缓存文件失败: {sanitize_for_log(filename)}, 错误: {sanitize_for_log(str(e))}")

            # 从缓存信息中移除
            del self.cache_info[cache_key]

    def cleanup_expired_files(self) -> None:
        """清理过期的缓存文件"""
        current_time = datetime.now()
        expired_keys = []

        with self.cache_lock:
            for cache_key, cache_entry in self.cache_info.items():
                if current_time > cache_entry['expire_time']:
                    expired_keys.append(cache_key)

            for cache_key in expired_keys:
                self._remove_cache_entry(cache_key)

        if expired_keys:
            logger.info(f"已清理 {len(expired_keys)} 个过期缓存文件")

    def _start_cleanup_thread(self) -> None:
        """启动清理线程"""
        def cleanup_worker():
            while True:
                try:
                    # 每5分钟检查一次过期文件
                    time.sleep(300)
                    self.cleanup_expired_files()
                except Exception as e:
                    logger.error(f"清理线程异常: {sanitize_for_log(str(e))}")

        cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        cleanup_thread.start()
        logger.info("缓存清理线程已启动")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        获取缓存统计信息

        Returns:
            缓存统计信息
        """
        with self.cache_lock:
            current_time = datetime.now()
            total_files = len(self.cache_info)
            expired_files = sum(1 for entry in self.cache_info.values()
                              if current_time > entry['expire_time'])

            return {
                'total_cached_files': total_files,
                'expired_files': expired_files,
                'active_files': total_files - expired_files,
                'cache_directory': str(self.cache_dir)
            }


# 全局缓存管理器实例
_cache_manager = None
_cache_manager_lock = threading.Lock()


def get_export_cache_manager() -> ExportCacheManager:
    """获取全局缓存管理器实例"""
    global _cache_manager

    if _cache_manager is None:
        with _cache_manager_lock:
            if _cache_manager is None:
                _cache_manager = ExportCacheManager()

    return _cache_manager