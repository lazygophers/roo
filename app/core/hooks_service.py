import yaml
import re
from pathlib import Path
from typing import Dict, Any
from app.models.schemas import HookInfo
from app.core.config import HOOKS_DIR


class HooksService:
    """Hooks 文件处理服务"""
    
    @staticmethod
    def parse_markdown_frontmatter(content: str) -> tuple[Dict[str, Any], str]:
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
    def load_hook_file(hook_name: str) -> HookInfo:
        """加载指定的 hook 文件"""
        file_path = HOOKS_DIR / f"{hook_name}.md"
        
        if not file_path.exists():
            raise FileNotFoundError(f"Hook file {hook_name}.md not found")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析 frontmatter 和内容
            frontmatter, markdown_content = HooksService.parse_markdown_frontmatter(content)
            
            # 创建 HookInfo 对象
            hook_info = HookInfo(
                name=frontmatter.get('name', hook_name),
                title=frontmatter.get('title', ''),
                description=frontmatter.get('description', ''),
                category=frontmatter.get('category', ''),
                priority=frontmatter.get('priority', ''),
                tags=frontmatter.get('tags', []),
                examples=frontmatter.get('examples', []),
                content=markdown_content,
                file_path=str(file_path.relative_to(HOOKS_DIR.parent))
            )
            
            return hook_info
            
        except Exception as e:
            raise Exception(f"Failed to load hook file {hook_name}.md: {str(e)}")
    
    @classmethod
    def get_before_hook(cls) -> HookInfo:
        """获取 before hook"""
        return cls.load_hook_file("before")
    
    @classmethod
    def get_after_hook(cls) -> HookInfo:
        """获取 after hook"""
        return cls.load_hook_file("after")