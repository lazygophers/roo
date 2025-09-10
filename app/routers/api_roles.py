from typing import List
import os
import re
from fastapi import APIRouter, HTTPException
from app.models.schemas import RoleInfo, RoleResponse

router = APIRouter()


def parse_role_metadata(file_path: str) -> RoleInfo:
    """解析角色文件的 YAML 前置数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取 YAML 前置数据
        yaml_match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
        if not yaml_match:
            raise ValueError(f"No YAML frontmatter found in {file_path}")
        
        yaml_content = yaml_match.group(1)
        metadata = {}
        
        # 简单解析 YAML（处理常见字段）
        for line in yaml_content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith(' '):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                
                if key in ['traits', 'features', 'restrictions']:
                    # 处理数组字段
                    if value.startswith('[') and value.endswith(']'):
                        # 简单数组格式 [item1, item2]
                        items = value[1:-1].split(',')
                        metadata[key] = [item.strip().strip('"\'') for item in items if item.strip()]
                    else:
                        metadata[key] = []
                else:
                    metadata[key] = value
        
        # 处理多行数组（features, restrictions等）
        lines = yaml_content.split('\n')
        current_key = None
        current_array = []
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped.endswith(':') and line_stripped.rstrip(':') in ['traits', 'features', 'restrictions']:
                if current_key and current_array:
                    metadata[current_key] = current_array
                current_key = line_stripped.rstrip(':')
                current_array = []
            elif current_key and line_stripped.startswith('- '):
                item = line_stripped[2:].strip().strip('"\'')
                current_array.append(item)
        
        # 处理最后一个数组
        if current_key and current_array:
            metadata[current_key] = current_array
        
        # 构建 RoleInfo 对象
        return RoleInfo(
            name=metadata.get('name', ''),
            title=metadata.get('title', ''),
            description=metadata.get('description', ''),
            category=metadata.get('category', 'role'),
            traits=metadata.get('traits', []),
            features=metadata.get('features', []),
            restrictions=metadata.get('restrictions'),
            file_path=file_path
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error parsing role file {file_path}: {str(e)}"
        )


@router.post(
    "/roles/list",
    response_model=RoleResponse,
    summary="获取角色列表",
    description="获取所有可用的角色元数据信息"
)
async def get_roles() -> RoleResponse:
    """获取角色列表"""
    try:
        roles_dir = "resources/roles"
        
        if not os.path.exists(roles_dir):
            return RoleResponse(
                success=True,
                message="角色目录不存在",
                data=[],
                total=0
            )
        
        roles = []
        
        # 扫描角色目录中的 .md 文件
        for filename in os.listdir(roles_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(roles_dir, filename)
                try:
                    role_info = parse_role_metadata(file_path)
                    roles.append(role_info)
                except Exception as e:
                    print(f"Warning: Failed to parse role file {filename}: {e}")
                    continue
        
        # 按名称排序
        roles.sort(key=lambda x: x.name)
        
        return RoleResponse(
            success=True,
            message=f"成功获取 {len(roles)} 个角色",
            data=roles,
            total=len(roles)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取角色列表失败: {str(e)}"
        )