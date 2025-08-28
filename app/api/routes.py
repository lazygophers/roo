from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import StreamingResponse
from typing import List, Dict, Any, Optional
import os
import yaml
import json
from pathlib import Path
from datetime import datetime
from app.database import ConfigDatabase, Q
from app.utils.frontmatter_parser import parse_markdown_with_frontmatter

router = APIRouter()

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent.parent
RESOURCES_DIR = BASE_DIR / "resources"

@router.get("/hello")
async def hello(message: Optional[str] = Query(None, description="要显示的消息")):
    """简单的问候端点，支持前端调用"""
    # 如果没有提供消息参数，使用默认消息
    display_message = message if message else "Hello from FastAPI!"
    
    return {
        "message": display_message,
        "status": "success"
    }


# 辅助函数
def read_yaml_file(file_path: Path) -> Dict[str, Any]:
    """读取YAML文件并返回字典"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except Exception:
        return {}


def read_text_file(file_path: Path) -> str:
    """读取文本文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception:
        return ""


# 新的资源配置API端点

@router.get("/models", response_model=List[Dict[str, Any]])
async def get_models():
    """获取models目录及其子目录的所有文件信息（排除customInstructions字段）"""
    models_dir = RESOURCES_DIR / "models"
    result = []
    
    if models_dir.exists():
        # 递归遍历models目录
        for file_path in models_dir.rglob("*.yaml"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    # 排除customInstructions字段
                    if 'customInstructions' in data:
                        del data['customInstructions']
                    # 添加文件路径信息
                    data['_path'] = str(file_path.relative_to(RESOURCES_DIR))
                    result.append(data)
            except Exception:
                continue
    
    return result


@router.get("/models/{slug}", response_model=Dict[str, Any])
async def get_model_by_slug(slug: str):
    """根据slug获取models目录下具体文件的完整内容"""
    models_dir = RESOURCES_DIR / "models"
    
    # 查找匹配的文件
    for file_path in models_dir.rglob(f"{slug}.yaml"):
        data = read_yaml_file(file_path)
        if data:
            data['_path'] = str(file_path.relative_to(RESOURCES_DIR))
            return data
    
    return {}


@router.get("/hooks/before", response_model=Dict[str, Any])
async def get_hooks_before():
    """获取hooks/before.md文件的frontmatter元数据和内容"""
    file_path = RESOURCES_DIR / "hooks" / "before.md"
    result = parse_markdown_with_frontmatter(file_path)
    if not result:
        return {"metadata": {}, "content": read_text_file(file_path)}
    return result


@router.get("/hooks/after", response_model=Dict[str, Any])
async def get_hooks_after():
    """获取hooks/after.md文件的frontmatter元数据和内容"""
    file_path = RESOURCES_DIR / "hooks" / "after.md"
    result = parse_markdown_with_frontmatter(file_path)
    if not result:
        return {"metadata": {}, "content": read_text_file(file_path)}
    return result


@router.get("/rules/{slug}", response_model=Dict[str, Dict[str, Any]])
async def get_rules_by_slug(slug: str):
    """根据slug获取rules目录下的所有文件内容和frontmatter元数据"""
    result = {}
    
    # 搜索规则文件的顺序：rules/ -> rules-{slug} -> rules-{slug}-{subslug}
    search_paths = [
        RESOURCES_DIR / "rules",
        RESOURCES_DIR / f"rules-{slug}"
    ]
    
    # 处理包含连字符的slug（如 code-golang）
    if '-' in slug:
        parts = slug.split('-')
        for i in range(len(parts)):
            prefix = '-'.join(parts[:i+1])
            search_paths.append(RESOURCES_DIR / f"rules-{prefix}")
    
    # 在所有搜索路径中查找文件
    for search_path in search_paths:
        if search_path.exists():
            for file_path in search_path.glob("*.md"):
                file_name = file_path.stem
                # 使用frontmatter解析器
                parsed_content = parse_markdown_with_frontmatter(file_path)
                if parsed_content:
                    result[file_name] = parsed_content
                else:
                    # 如果没有frontmatter，返回原始内容
                    result[file_name] = {
                        "metadata": {},
                        "content": read_text_file(file_path)
                    }
    
    return result


@router.get("/commands", response_model=Dict[str, Dict[str, Any]])
async def get_commands():
    """获取commands目录下的所有文件内容和frontmatter元数据"""
    commands_dir = RESOURCES_DIR / "commands"
    result = {}
    
    if commands_dir.exists():
        for file_path in commands_dir.glob("*.md"):
            file_name = file_path.stem
            # 使用frontmatter解析器
            parsed_content = parse_markdown_with_frontmatter(file_path)
            if parsed_content:
                result[file_name] = parsed_content
            else:
                # 如果没有frontmatter，返回原始内容
                result[file_name] = {
                    "metadata": {},
                    "content": read_text_file(file_path)
                }
    
    return result


@router.get("/roles", response_model=Dict[str, Dict[str, Any]])
async def get_roles():
    """获取roles目录下的所有文件内容和frontmatter元数据"""
    roles_dir = RESOURCES_DIR / "roles"
    result = {}
    
    if roles_dir.exists():
        for file_path in roles_dir.glob("*.md"):
            file_name = file_path.stem
            # 使用frontmatter解析器
            parsed_content = parse_markdown_with_frontmatter(file_path)
            if parsed_content:
                result[file_name] = parsed_content
            else:
                # 如果没有frontmatter，返回原始内容
                result[file_name] = {
                    "metadata": {},
                    "content": read_text_file(file_path)
                }
    
    return result


# 配置管理API端点

@router.post("/configurations", response_model=Dict[str, Any], status_code=201)
async def save_configuration(config_data: Dict[str, Any]):
    """保存配置到数据库"""
    try:
        db = ConfigDatabase()
        config_id = db.save_configuration(config_data)
        return {
            "success": True,
            "message": "配置保存成功",
            "config_id": config_id,
            "data": config_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.get("/configurations", response_model=List[Dict[str, Any]])
async def get_configurations(user_id: Optional[str] = Query(None, description="用户ID，用于获取用户专属配置")):
    """获取所有配置或用户专属配置"""
    try:
        db = ConfigDatabase()
        if user_id:
            configs = db.get_user_configurations(user_id)
        else:
            configs = db.get_all_configurations()
        return configs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.get("/configurations/{config_id}", response_model=Dict[str, Any])
async def get_configuration(config_id: str):
    """根据ID获取单个配置"""
    try:
        db = ConfigDatabase()
        config = db.get_configuration(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        return config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取配置失败: {str(e)}")


@router.put("/configurations/{config_id}", response_model=Dict[str, Any])
async def update_configuration(config_id: str, config_data: Dict[str, Any]):
    """更新配置"""
    try:
        db = ConfigDatabase()
        updated_config = db.update_configuration(config_id, config_data)
        if not updated_config:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {
            "success": True,
            "message": "配置更新成功",
            "data": updated_config
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.delete("/configurations/{config_id}")
async def delete_configuration(config_id: str):
    """删除配置"""
    try:
        db = ConfigDatabase()
        success = db.delete_configuration(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="配置不存在")
        return {"success": True, "message": "配置删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")


@router.post("/configurations/{config_id}/export/yaml")
async def export_configuration_yaml(config_id: str):
    """导出配置为YAML文件"""
    try:
        db = ConfigDatabase()
        config = db.get_configuration(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 移除数据库字段
        export_data = {k: v for k, v in config.items() if k not in ['doc_id', 'created_at', 'updated_at']}
        
        yaml_content = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)
        
        # 创建响应
        from io import StringIO
        yaml_file = StringIO(yaml_content)
        yaml_file.seek(0)
        
        filename = f"configuration_{config_id}.yaml"
        return StreamingResponse(
            iter([yaml_file.getvalue().encode('utf-8')]),
            media_type="application/x-yaml",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出YAML失败: {str(e)}")


@router.post("/configurations/{config_id}/export/json")
async def export_configuration_json(config_id: str):
    """导出配置为JSON文件"""
    try:
        db = ConfigDatabase()
        config = db.get_configuration(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="配置不存在")
        
        # 移除数据库字段
        export_data = {k: v for k, v in config.items() if k not in ['doc_id', 'created_at', 'updated_at']}
        
        json_content = json.dumps(export_data, indent=2, ensure_ascii=False)
        
        # 创建响应
        from io import StringIO
        json_file = StringIO(json_content)
        json_file.seek(0)
        
        filename = f"configuration_{config_id}.json"
        return StreamingResponse(
            iter([json_file.getvalue().encode('utf-8')]),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出JSON失败: {str(e)}")


@router.post("/configurations/import/yaml", response_model=Dict[str, Any])
async def import_configuration_yaml(
    file: UploadFile = File(...),
    user_id: Optional[str] = Query(None, description="用户ID，用于关联配置")
):
    """从YAML文件导入配置"""
    try:
        # 读取文件内容
        content = await file.read()
        yaml_content = content.decode('utf-8')
        
        # 解析YAML
        config_data = yaml.safe_load(yaml_content)
        if not config_data:
            raise HTTPException(status_code=400, detail="无效的YAML文件")
        
        # 添加用户ID（如果提供）
        if user_id:
            config_data['user_id'] = user_id
        
        # 保存到数据库
        db = ConfigDatabase()
        config_id = db.save_configuration(config_data)
        
        return {
            "success": True,
            "message": "YAML配置导入成功",
            "config_id": config_id,
            "data": config_data
        }
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML解析错误: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入YAML配置失败: {str(e)}")


@router.post("/configurations/import/json", response_model=Dict[str, Any])
async def import_configuration_json(
    file: UploadFile = File(...),
    user_id: Optional[str] = Query(None, description="用户ID，用于关联配置")
):
    """从JSON文件导入配置"""
    try:
        # 读取文件内容
        content = await file.read()
        json_content = content.decode('utf-8')
        
        # 解析JSON
        config_data = json.loads(json_content)
        if not config_data:
            raise HTTPException(status_code=400, detail="无效的JSON文件")
        
        # 添加用户ID（如果提供）
        if user_id:
            config_data['user_id'] = user_id
        
        # 保存到数据库
        db = ConfigDatabase()
        config_id = db.save_configuration(config_data)
        
        return {
            "success": True,
            "message": "JSON配置导入成功",
            "config_id": config_id,
            "data": config_data
        }
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON解析错误: {str(e)}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导入JSON配置失败: {str(e)}")