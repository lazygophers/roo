"""
JSON 文件服务 - 替代数据库的纯文件存储系统
完全基于 JSON 文件，无需数据库依赖
"""

import json
import os
import yaml
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log

logger = setup_logging("INFO")

class JsonFileService:
    """JSON文件服务：完全基于JSON文件的数据管理系统"""

    def __init__(self, json_cache_dir: str = "data/roo"):
        """初始化JSON文件服务

        Args:
            json_cache_dir: JSON缓存目录，默认为 data/roo
        """
        self.json_cache_dir = PROJECT_ROOT / json_cache_dir
        self.json_cache_dir.mkdir(parents=True, exist_ok=True)

        # 扫描配置
        self._scan_configs = {}

        # 文件缓存
        self._file_cache = {}

        logger.info(f"JSON file service initialized with cache directory: {self.json_cache_dir}")

    def add_scan_config(self, config_name: str, directory: str, patterns: List[str], watch: bool = False):
        """添加扫描配置

        Args:
            config_name: 配置名称
            directory: 扫描目录
            patterns: 文件模式列表
            watch: 是否监听文件变化（暂不实现）
        """
        self._scan_configs[config_name] = {
            'directory': directory,
            'patterns': patterns,
            'watch': watch,
            'table_name': f"{config_name}_cache"
        }
        logger.info(f"Added scan config: {config_name} -> {directory}")

    def _get_json_file_path(self, config_name: str) -> Path:
        """获取配置对应的JSON文件路径"""
        return self.json_cache_dir / f"{config_name}.json"

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希值"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate hash for {file_path}: {e}")
            return ""

    def _scan_directory(self, config_name: str) -> List[Dict[str, Any]]:
        """扫描目录并生成缓存数据"""
        if config_name not in self._scan_configs:
            logger.warning(f"Config '{config_name}' not found")
            return []

        config = self._scan_configs[config_name]
        directory = Path(config['directory'])
        patterns = config['patterns']

        if not directory.exists():
            logger.warning(f"Directory not found: {directory}")
            return []

        cache_data = []

        # 扫描匹配的文件
        for pattern in patterns:
            for file_path in directory.rglob(pattern):
                if file_path.is_file():
                    try:
                        # 读取文件内容
                        content = self._parse_file_content(file_path)

                        # 生成缓存记录
                        relative_path = file_path.relative_to(PROJECT_ROOT)
                        cache_record = {
                            'file_path': str(relative_path),
                            'absolute_path': str(file_path),
                            'file_name': file_path.name,
                            'file_hash': self._calculate_file_hash(str(file_path)),
                            'file_size': file_path.stat().st_size,
                            'last_modified': int(file_path.stat().st_mtime),  # 转换为整数
                            'scan_time': datetime.now().isoformat(),
                            'content': content,
                            'config_name': config_name
                        }
                        cache_data.append(cache_record)

                    except Exception as e:
                        logger.error(f"Failed to process file {file_path}: {e}")
                        continue

        logger.info(f"Scanned {len(cache_data)} files for config '{config_name}'")
        return cache_data

    def _parse_file_content(self, file_path: Path) -> Dict[str, Any]:
        """解析文件内容"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 尝试解析YAML/YML文件
            if file_path.suffix.lower() in ['.yaml', '.yml']:
                try:
                    return yaml.safe_load(content)
                except yaml.YAMLError as e:
                    logger.error(f"YAML parse error in {file_path}: {e}")
                    return {"raw_content": content, "parse_error": str(e)}

            # 尝试解析JSON文件
            elif file_path.suffix.lower() == '.json':
                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error in {file_path}: {e}")
                    return {"raw_content": content, "parse_error": str(e)}

            # 处理Markdown文件，提取frontmatter
            elif file_path.suffix.lower() == '.md':
                return self._parse_markdown_content(content)
            # 其他文件类型作为原始内容
            else:
                return {"raw_content": content}

        except Exception as e:
            logger.error(f"Failed to read file {file_path}: {e}")
            return {"error": str(e)}

    def _parse_markdown_content(self, content: str) -> Dict[str, Any]:
        """解析Markdown文件，提取frontmatter和内容"""
        try:
            # 检查是否有frontmatter
            if content.startswith('---\n'):
                parts = content.split('\n---\n', 1)
                if len(parts) == 2:
                    frontmatter_text = parts[0][4:]  # 去掉开头的 '---\n'
                    markdown_content = parts[1]

                    try:
                        # 解析frontmatter YAML
                        frontmatter = yaml.safe_load(frontmatter_text)
                        return {
                            **frontmatter,  # 将frontmatter字段展开到顶层
                            "markdown_content": markdown_content.strip(),
                            "raw_content": content
                        }
                    except yaml.YAMLError as e:
                        logger.warning(f"Failed to parse frontmatter YAML: {e}")
                        return {"raw_content": content}

            # 没有frontmatter，直接返回原始内容
            return {"raw_content": content}

        except Exception as e:
            logger.error(f"Failed to parse markdown content: {e}")
            return {"raw_content": content}

    def _read_json_cache(self, config_name: str) -> Optional[Dict[str, Any]]:
        """从JSON文件读取缓存数据"""
        json_file = self._get_json_file_path(config_name)

        if not json_file.exists():
            return None

        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read JSON cache {json_file}: {e}")
            return None

    def _write_json_cache(self, config_name: str, cache_data: List[Dict[str, Any]]) -> bool:
        """写入JSON缓存文件"""
        json_file = self._get_json_file_path(config_name)

        export_data = {
            "metadata": {
                "config_name": config_name,
                "export_time": datetime.now().isoformat(),
                "total_items": len(cache_data),
                "version": "1.0"
            },
            "data": []
        }

        # 处理缓存数据
        for item in cache_data:
            processed_item = {
                "file_info": {
                    "file_path": item.get("file_path", ""),
                    "file_name": item.get("file_name", ""),
                    "last_modified": item.get("last_modified", ""),
                    "file_size": item.get("file_size", 0)
                },
                "content": item.get("content", {}),
                "config_name": item.get("config_name", config_name)
            }
            export_data["data"].append(processed_item)

        try:
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"Successfully wrote {len(cache_data)} items to {json_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to write JSON cache {json_file}: {e}")
            return False

    def sync_config(self, config_name: str) -> bool:
        """同步指定配置的数据"""
        try:
            # 扫描目录获取最新数据
            cache_data = self._scan_directory(config_name)

            # 写入JSON文件
            success = self._write_json_cache(config_name, cache_data)

            if success:
                # 更新内存缓存
                self._file_cache[config_name] = cache_data
                logger.info(f"Successfully synced config '{config_name}': {len(cache_data)} items")

            return success

        except Exception as e:
            logger.error(f"Failed to sync config '{sanitize_for_log(config_name)}': {e}")
            return False

    def sync_all_configs(self) -> Dict[str, bool]:
        """同步所有配置"""
        results = {}

        for config_name in self._scan_configs:
            results[config_name] = self.sync_config(config_name)

        return results

    def get_cached_data(self, config_name: str) -> List[Dict[str, Any]]:
        """获取缓存数据"""
        # 优先从内存缓存获取
        if config_name in self._file_cache:
            return self._file_cache[config_name]

        # 从JSON文件读取
        json_data = self._read_json_cache(config_name)
        if json_data:
            # 转换为标准格式
            cache_data = []
            for item in json_data.get("data", []):
                file_info = item.get("file_info", {})
                record = {
                    'file_path': file_info.get('file_path', ''),
                    'file_name': file_info.get('file_name', ''),
                    'last_modified': file_info.get('last_modified', ''),
                    'file_size': file_info.get('file_size', 0),
                    'content': item.get('content', {}),
                    'config_name': item.get('config_name', config_name)
                }
                cache_data.append(record)

            # 更新内存缓存
            self._file_cache[config_name] = cache_data
            return cache_data

        # 如果没有缓存，尝试同步
        if self.sync_config(config_name):
            return self._file_cache.get(config_name, [])

        return []

    def search_content(self, config_name: str, **filters) -> List[Dict[str, Any]]:
        """搜索内容"""
        cache_data = self.get_cached_data(config_name)

        if not filters:
            return cache_data

        results = []
        for item in cache_data:
            match = True
            for key, value in filters.items():
                if key in item and item[key] != value:
                    match = False
                    break
                elif key in item.get('content', {}) and item['content'][key] != value:
                    match = False
                    break

            if match:
                results.append(item)

        return results

    def get_config_stats(self, config_name: str) -> Dict[str, Any]:
        """获取配置统计信息"""
        cache_data = self.get_cached_data(config_name)

        return {
            'config_name': config_name,
            'total_items': len(cache_data),
            'last_sync': datetime.now().isoformat(),
            'directory': self._scan_configs.get(config_name, {}).get('directory', ''),
            'json_file': str(self._get_json_file_path(config_name))
        }

    def get_all_stats(self) -> Dict[str, Any]:
        """获取所有配置的统计信息"""
        stats = {
            'cache_directory': str(self.json_cache_dir),
            'total_configs': len(self._scan_configs),
            'configs': {}
        }

        for config_name in self._scan_configs:
            config_stats = self.get_config_stats(config_name)
            # 添加更多信息
            json_file = self._get_json_file_path(config_name)
            if json_file.exists():
                json_data = self._read_json_cache(config_name)
                if json_data:
                    metadata = json_data.get("metadata", {})
                    config_stats.update({
                        'export_time': metadata.get('export_time', ''),
                        'json_file_size': json_file.stat().st_size,
                        'file_exists': True
                    })
                else:
                    config_stats['file_exists'] = False
            else:
                config_stats['file_exists'] = False

            stats['configs'][config_name] = config_stats

        return stats

    def cleanup_old_caches(self, keep_days: int = 7) -> int:
        """清理过期的缓存文件（保留功能，但JSON文件通常不需要清理）"""
        # 由于我们现在主要依赖JSON文件，这个功能可能不需要
        # 但保留接口以保持兼容性
        logger.info(f"Cleanup requested, but JSON files are kept indefinitely")
        return 0

    # 兼容性方法 - 保持与原database_service相同的接口
    @property
    def scan_configs(self):
        """兼容性属性"""
        return self._scan_configs

    def get_sync_metadata(self, config_name: str) -> Optional[Dict[str, Any]]:
        """获取同步元数据（兼容性方法）"""
        return self.get_config_stats(config_name)


# 全局服务实例
_json_file_service = None

def get_json_file_service(json_cache_dir: str = "data/roo") -> JsonFileService:
    """获取全局JSON文件服务实例"""
    global _json_file_service
    if _json_file_service is None:
        _json_file_service = JsonFileService(json_cache_dir)
    return _json_file_service

# 兼容性函数 - 替代原来的get_database_service
def get_database_service():
    """兼容性函数：返回JSON文件服务实例"""
    return get_json_file_service()