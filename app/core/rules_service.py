import os
import yaml
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.models.schemas import FileMetadata
from app.core.config import PROJECT_ROOT


class RulesService:
    """Rules 文件处理服务"""
    
    @staticmethod
    def get_search_directories(slug: str) -> List[str]:
        """根据 slug 生成搜索目录列表"""
        search_dirs = []
        
        # 规则：slug = code-go -> [rules-code-go, rules-code, rules]
        if '-' in slug:
            parts = slug.split('-')
            # 逐步构建目录名
            for i in range(len(parts), 0, -1):
                dir_name = 'rules-' + '-'.join(parts[:i])
                search_dirs.append(dir_name)
        
        # 最后添加通用的 rules 目录
        search_dirs.append('rules')
        
        return search_dirs
    
    @staticmethod
    def parse_markdown_frontmatter(content: str) -> Tuple[Dict[str, Any], str]:
        """解析 Markdown 文件的 frontmatter 和内容"""
        # 匹配 frontmatter（YAML 格式）
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n(.*)'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if match:
            frontmatter_str = match.group(1)
            markdown_content = match.group(2)
            
            try:
                frontmatter = yaml.safe_load(frontmatter_str)
                return frontmatter or {}, markdown_content.strip()
            except yaml.YAMLError:
                return {}, content
        else:
            # 没有 frontmatter，整个内容都是 markdown
            return {}, content.strip()
    
    @staticmethod
    def extract_file_metadata(file_path: Path, source_directory: str) -> Optional[FileMetadata]:
        """提取单个文件的 metadata"""
        if not file_path.exists() or not file_path.is_file():
            return None
        
        try:
            # 获取文件统计信息
            file_stat = file_path.stat()
            file_size = file_stat.st_size
            last_modified = int(file_stat.st_mtime)
            
            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 frontmatter
            frontmatter, _ = RulesService.parse_markdown_frontmatter(content)
            
            # 创建 FileMetadata 对象
            metadata = FileMetadata(
                name=frontmatter.get('name'),
                title=frontmatter.get('title'),
                description=frontmatter.get('description'),
                category=frontmatter.get('category'),
                language=frontmatter.get('language'),
                priority=frontmatter.get('priority'),
                tags=frontmatter.get('tags'),
                sections=frontmatter.get('sections'),
                references=frontmatter.get('references'),
                file_path=str(file_path.relative_to(PROJECT_ROOT)),
                source_directory=source_directory,
                file_size=file_size,
                last_modified=last_modified
            )
            
            return metadata
            
        except Exception as e:
            print(f"Warning: Could not process {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def find_files_in_directory(directory_path: Path) -> List[Path]:
        """查找目录下的所有文件"""
        files = []
        
        if not directory_path.exists() or not directory_path.is_dir():
            return files
        
        # 递归查找所有文件
        for root, dirs, file_names in os.walk(directory_path):
            for file_name in file_names:
                # 只处理 markdown 文件和其他文本文件
                if file_name.endswith(('.md', '.txt', '.yaml', '.yml', '.json')):
                    file_path = Path(root) / file_name
                    files.append(file_path)
        
        return sorted(files)
    
    @classmethod
    def get_rules_by_slug(cls, slug: str) -> Tuple[List[str], List[str], List[FileMetadata]]:
        """根据 slug 获取 rules 文件的 metadata"""
        resources_dir = PROJECT_ROOT / "resources"
        search_directories = cls.get_search_directories(slug)
        found_directories = []
        all_metadata = []
        
        # 依次搜索目录
        for dir_name in search_directories:
            directory_path = resources_dir / dir_name
            
            if directory_path.exists() and directory_path.is_dir():
                found_directories.append(dir_name)
                
                # 查找目录下的所有文件
                files = cls.find_files_in_directory(directory_path)
                
                # 提取每个文件的 metadata
                for file_path in files:
                    metadata = cls.extract_file_metadata(file_path, dir_name)
                    if metadata:
                        all_metadata.append(metadata)
        
        return search_directories, found_directories, all_metadata