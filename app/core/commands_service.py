"""Commands 服务模块"""
from pathlib import Path
from typing import List
import os
from datetime import datetime
from app.core.config import PROJECT_ROOT
from app.models.schemas import FileMetadata


class CommandsService:
    """Commands 服务类"""
    
    COMMANDS_DIR = PROJECT_ROOT / "resources" / "commands"
    
    @staticmethod
    def get_commands_metadata() -> List[FileMetadata]:
        """获取 commands 目录下所有文件的 metadata 信息"""
        if not CommandsService.COMMANDS_DIR.exists():
            return []
        
        metadata_list = []
        
        # 遍历 commands 目录下的所有文件
        for file_path in CommandsService.COMMANDS_DIR.rglob("*"):
            if file_path.is_file():
                try:
                    # 获取文件统计信息
                    stat = file_path.stat()
                    
                    # 解析文件内容获取 frontmatter
                    frontmatter_data = CommandsService._parse_frontmatter(file_path)
                    
                    metadata = FileMetadata(
                        name=frontmatter_data.get("name", file_path.stem),
                        title=frontmatter_data.get("title"),
                        description=frontmatter_data.get("description"),
                        category=frontmatter_data.get("category"),
                        language=frontmatter_data.get("language"),
                        priority=frontmatter_data.get("priority"),
                        tags=frontmatter_data.get("tags", []),
                        sections=frontmatter_data.get("sections", []),
                        references=frontmatter_data.get("references", []),
                        file_path=str(file_path),
                        source_directory=str(CommandsService.COMMANDS_DIR),
                        file_size=stat.st_size,
                        last_modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
                    )
                    
                    metadata_list.append(metadata)
                    
                except Exception as e:
                    # 如果解析某个文件失败，跳过该文件
                    print(f"Warning: Failed to parse {file_path}: {e}")
                    continue
        
        # 按文件名排序
        metadata_list.sort(key=lambda x: x.file_path)
        
        return metadata_list
    
    @staticmethod
    def _parse_frontmatter(file_path: Path) -> dict:
        """解析文件的 frontmatter"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否有 frontmatter
            if not content.startswith('---'):
                return {}
            
            # 查找第二个 ---
            end_index = content.find('---', 3)
            if end_index == -1:
                return {}
            
            # 提取 frontmatter 部分
            frontmatter_text = content[3:end_index].strip()
            
            # 解析 YAML frontmatter
            import yaml
            try:
                frontmatter_data = yaml.safe_load(frontmatter_text) or {}
                return frontmatter_data
            except yaml.YAMLError:
                return {}
                
        except Exception:
            return {}