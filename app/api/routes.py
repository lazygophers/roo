from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

router = APIRouter()

# 模拟数据存储
items_db = [
    {"id": 1, "name": "项目1", "description": "这是第一个项目", "status": "active"},
    {"id": 2, "name": "项目2", "description": "这是第二个项目", "status": "completed"},
    {"id": 3, "name": "项目3", "description": "这是第三个项目", "status": "pending"},
]

@router.get("/hello")
async def hello():
    """简单的问候接口"""
    return {"message": "Hello from FastAPI!", "status": "success"}

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