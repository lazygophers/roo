import os
import yaml
from pathlib import Path
from typing import List, Dict, Any
from app.models.schemas import ModelInfo
from app.core.config import MODELS_DIR


class YAMLService:
    """YAML 文件处理服务"""
    
    @staticmethod
    def find_yaml_files(directory: Path) -> List[Path]:
        """递归查找所有 YAML 文件"""
        yaml_files = []
        
        # 遍历目录及其子目录
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.yaml', '.yml')):
                    yaml_files.append(Path(root) / file)
                    
        return yaml_files
    
    @staticmethod
    def load_yaml_file(file_path: Path) -> Dict[str, Any]:
        """加载单个 YAML 文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except Exception as e:
            raise Exception(f"Failed to load {file_path}: {str(e)}")
    
    @staticmethod
    def filter_yaml_data(data: Dict[str, Any], file_path: Path) -> ModelInfo:
        """过滤 YAML 数据，排除 customInstructions 字段"""
        filtered_data = {
            'slug': data.get('slug', ''),
            'name': data.get('name', ''),
            'roleDefinition': data.get('roleDefinition', ''),
            'whenToUse': data.get('whenToUse', ''),
            'description': data.get('description', ''),
            'groups': data.get('groups', []),
            'file_path': str(file_path.relative_to(MODELS_DIR.parent))
        }
        
        return ModelInfo(**filtered_data)
    
    @classmethod
    def load_all_models(cls) -> List[ModelInfo]:
        """加载所有模型数据"""
        models = []
        
        # 查找所有 YAML 文件
        yaml_files = cls.find_yaml_files(MODELS_DIR)
        
        for file_path in yaml_files:
            try:
                # 加载 YAML 数据
                yaml_data = cls.load_yaml_file(file_path)
                
                # 过滤数据并创建 ModelInfo 对象
                model_info = cls.filter_yaml_data(yaml_data, file_path)
                models.append(model_info)
                
            except Exception as e:
                # 记录错误但继续处理其他文件
                print(f"Warning: Could not process {file_path}: {str(e)}")
                continue
                
        # 按 slug 排序
        models.sort(key=lambda x: x.slug)
        return models