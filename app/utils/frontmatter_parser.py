"""
YAML Frontmatter 解析工具模块
支持解析MD文件中的YAML frontmatter元数据
"""
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

class FrontmatterParser:
    """YAML Frontmatter 解析器"""
    
    # Frontmatter 正则表达式模式
    FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n(.*)$', re.DOTALL)
    
    @classmethod
    def parse(cls, content: str) -> Tuple[Dict[str, Any], str]:
        """
        解析包含YAML frontmatter的内容
        
        Args:
            content: 文件内容
            
        Returns:
            Tuple[metadata, content]: (元数据字典, 剩余内容)
        """
        match = cls.FRONTMATTER_PATTERN.match(content)
        
        if match:
            frontmatter_yaml = match.group(1)
            remaining_content = match.group(2)
            
            # 解析YAML
            try:
                metadata = yaml.safe_load(frontmatter_yaml) or {}
                return metadata, remaining_content
            except yaml.YAMLError as e:
                print(f"YAML解析错误: {e}")
                return {}, content
        else:
            # 没有找到frontmatter，返回空元数据和原内容
            return {}, content
    
    @classmethod
    def parse_file(cls, file_path: Path) -> Tuple[Dict[str, Any], str]:
        """
        解析文件中的YAML frontmatter
        
        Args:
            file_path: 文件路径
            
        Returns:
            Tuple[metadata, content]: (元数据字典, 剩余内容)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return cls.parse(content)
        except Exception as e:
            print(f"读取文件失败: {e}")
            return {}, ""
    
    @classmethod
    def has_frontmatter(cls, content: str) -> bool:
        """
        检查内容是否包含YAML frontmatter
        
        Args:
            content: 文件内容
            
        Returns:
            bool: 是否包含frontmatter
        """
        return bool(cls.FRONTMATTER_PATTERN.match(content))
    
    @classmethod
    def extract_metadata(cls, file_path: Path) -> Dict[str, Any]:
        """
        仅提取文件的元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            Dict[str, Any]: 元数据字典
        """
        metadata, _ = cls.parse_file(file_path)
        return metadata


def parse_markdown_with_frontmatter(file_path: Path) -> Dict[str, Any]:
    """
    解析Markdown文件，返回包含元数据和内容的完整信息
    
    Args:
        file_path: Markdown文件路径
        
    Returns:
        Dict[str, Any]: 包含元数据和内容的信息字典
    """
    metadata, content = FrontmatterParser.parse_file(file_path)
    
    return {
        'metadata': metadata,
        'content': content,
        'has_frontmatter': bool(metadata),
        'file_path': str(file_path)
    }