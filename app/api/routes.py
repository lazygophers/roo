from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
import os
import yaml
from pathlib import Path

router = APIRouter()

# 基础路径配置
BASE_DIR = Path(__file__).parent.parent.parent
RESOURCES_DIR = BASE_DIR / "resources"

# 模拟数据存储
items_db = [
    {"id": 1, "name": "项目1", "description": "这是第一个项目", "status": "active"},
    {"id": 2, "name": "项目2", "description": "这是第二个项目", "status": "completed"},
    {"id": 3, "name": "项目3", "description": "这是第三个项目", "status": "pending"},
]


@router.get("/items", response_model=List[Dict[str, Any]])
async def get_items():
    """获取所有项目列表"""
    return items_db

@router.get("/items/{item_id}", response_model=Dict[str, Any])
async def get_item(item_id: int):
    """根据ID获取单个项目"""
    item = next((item for item in items_db if item["id"] == item_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="项目未找到")
    return item

@router.post("/items", response_model=Dict[str, Any], status_code=201)
async def create_item(item: Dict[str, Any]):
    """创建新项目"""
    # 简单验证
    if "name" not in item:
        raise HTTPException(status_code=400, detail="项目名称是必需的")
    
    # 生成新ID
    new_id = max([i["id"] for i in items_db]) + 1 if items_db else 1
    new_item = {
        "id": new_id,
        "name": item["name"],
        "description": item.get("description", ""),
        "status": item.get("status", "pending")
    }
    items_db.append(new_item)
    return new_item

@router.put("/items/{item_id}", response_model=Dict[str, Any])
async def update_item(item_id: int, updated_item: Dict[str, Any]):
    """更新项目信息"""
    item_index = next((i for i, item in enumerate(items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="项目未找到")
    
    # 更新字段
    items_db[item_index].update(updated_item)
    return items_db[item_index]

@router.delete("/items/{item_id}")
async def delete_item(item_id: int):
    """删除项目"""
    item_index = next((i for i, item in enumerate(items_db) if item["id"] == item_id), None)
    if item_index is None:
        raise HTTPException(status_code=404, detail="项目未找到")
    
    items_db.pop(item_index)
    return {"message": "项目已删除", "status": "success"}

@router.get("/stats")
async def get_stats():
    """获取项目统计信息"""
    total = len(items_db)
    active = sum(1 for item in items_db if item["status"] == "active")
    completed = sum(1 for item in items_db if item["status"] == "completed")
    pending = sum(1 for item in items_db if item["status"] == "pending")
    
    return {
        "total": total,
        "active": active,
        "completed": completed,
        "pending": pending
    }


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


@router.get("/hooks/before", response_model=str)
async def get_hooks_before():
    """获取hooks/before.md文件内容"""
    file_path = RESOURCES_DIR / "hooks" / "before.md"
    return read_text_file(file_path)


@router.get("/hooks/after", response_model=str)
async def get_hooks_after():
    """获取hooks/after.md文件内容"""
    file_path = RESOURCES_DIR / "hooks" / "after.md"
    return read_text_file(file_path)


@router.get("/rules/{slug}", response_model=Dict[str, str])
async def get_rules_by_slug(slug: str):
    """根据slug获取rules目录下的所有文件内容"""
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
                result[file_name] = read_text_file(file_path)
    
    return result


@router.get("/commands", response_model=Dict[str, str])
async def get_commands():
    """获取commands目录下的所有文件内容"""
    commands_dir = RESOURCES_DIR / "commands"
    result = {}
    
    if commands_dir.exists():
        for file_path in commands_dir.glob("*.md"):
            file_name = file_path.stem
            result[file_name] = read_text_file(file_path)
    
    return result


@router.get("/roles", response_model=Dict[str, str])
async def get_roles():
    """获取roles目录下的所有文件内容"""
    roles_dir = RESOURCES_DIR / "roles"
    result = {}
    
    if roles_dir.exists():
        for file_path in roles_dir.glob("*.md"):
            file_name = file_path.stem
            result[file_name] = read_text_file(file_path)
    
    return result