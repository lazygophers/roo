"""
回收站管理 API 路由
提供软删除、恢复、永久删除等回收站相关操作接口
"""

from fastapi import APIRouter, HTTPException, Query as FastAPIQuery
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

from app.core.recycle_bin_service import (
    get_recycle_bin_service, 
    RecycleBinItemType, 
    RecycleBinItem
)
from app.core.recycle_bin_scheduler import (
    get_recycle_bin_scheduler,
    manual_cleanup_expired_items,
    get_cleanup_statistics
)
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging

logger = setup_logging("INFO")
router = APIRouter(prefix="/recycle-bin", tags=["Recycle Bin"])

# Pydantic 模型定义
class SoftDeleteRequest(BaseModel):
    """软删除请求模型"""
    table_name: str = Field(..., description="原始表名")
    item_id: str = Field(..., description="项目ID")
    item_type: RecycleBinItemType = Field(..., description="项目类型")
    deleted_by: str = Field(default="system", description="删除者")
    deleted_reason: str = Field(default="manual_delete", description="删除原因")
    retention_days: Optional[int] = Field(default=None, ge=1, le=30, description="保留天数(1-30天)")

class RecycleBinItemResponse(BaseModel):
    """回收站项目响应模型"""
    id: str
    original_id: str
    item_type: str
    original_table: str
    original_data: Dict[str, Any]
    deleted_by: str
    deleted_reason: str
    deleted_at: str
    expires_at: str
    is_expired: bool
    remaining_days: int
    metadata: Dict[str, Any] = {}

class RecycleBinStatsResponse(BaseModel):
    """回收站统计响应模型"""
    total_items: int
    by_type: Dict[str, int]
    expired_items: int
    expiring_soon: int
    oldest_item: Optional[str]
    newest_item: Optional[str]

class EmptyRecycleBinRequest(BaseModel):
    """清空回收站请求模型"""
    force: bool = Field(default=False, description="是否强制删除未过期项目")

# API 端点实现
@router.post("/soft-delete", response_model=Dict[str, Any])
async def soft_delete_item(request: SoftDeleteRequest):
    """软删除项目（移动到回收站）"""
    try:
        recycle_service = get_recycle_bin_service()
        success = recycle_service.soft_delete(
            table_name=request.table_name,
            item_id=request.item_id,
            item_type=request.item_type,
            deleted_by=request.deleted_by,
            deleted_reason=request.deleted_reason,
            retention_days=request.retention_days
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"项目未找到或删除失败: {request.item_id}")
        
        logger.info(f"Item soft deleted: {sanitize_for_log(request.item_id)}")
        
        return {
            "status": "success",
            "message": f"项目已移动到回收站",
            "item_id": request.item_id,
            "retention_days": request.retention_days or 3,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to soft delete item: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"软删除失败: {str(e)}")

@router.get("/items", response_model=List[RecycleBinItemResponse])
async def get_recycle_bin_items(
    item_type: Optional[RecycleBinItemType] = FastAPIQuery(None, description="按类型过滤"),
    include_expired: bool = FastAPIQuery(True, description="是否包含已过期项目"),
    limit: Optional[int] = FastAPIQuery(None, ge=1, le=1000, description="返回数量限制")
):
    """获取回收站项目列表"""
    try:
        recycle_service = get_recycle_bin_service()
        items = recycle_service.get_all_items(
            item_type=item_type,
            include_expired=include_expired,
            limit=limit
        )
        
        return [
            RecycleBinItemResponse(
                id=item["id"],
                original_id=item["original_id"],
                item_type=item["item_type"],
                original_table=item["original_table"],
                original_data=item["original_data"],
                deleted_by=item["deleted_by"],
                deleted_reason=item["deleted_reason"],
                deleted_at=item["deleted_at"],
                expires_at=item["expires_at"],
                is_expired=item["is_expired"],
                remaining_days=item["remaining_days"],
                metadata=item["metadata"]
            )
            for item in items
        ]
    except Exception as e:
        logger.error(f"Failed to get recycle bin items: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取回收站项目失败: {str(e)}")

@router.get("/items/{recycle_bin_id}", response_model=RecycleBinItemResponse)
async def get_recycle_bin_item(recycle_bin_id: str):
    """获取单个回收站项目详情"""
    try:
        recycle_service = get_recycle_bin_service()
        items = recycle_service.get_all_items()
        
        item = next((item for item in items if item["id"] == recycle_bin_id), None)
        if not item:
            raise HTTPException(status_code=404, detail=f"回收站项目未找到: {recycle_bin_id}")
        
        return RecycleBinItemResponse(
            id=item["id"],
            original_id=item["original_id"],
            item_type=item["item_type"],
            original_table=item["original_table"],
            original_data=item["original_data"],
            deleted_by=item["deleted_by"],
            deleted_reason=item["deleted_reason"],
            deleted_at=item["deleted_at"],
            expires_at=item["expires_at"],
            is_expired=item["is_expired"],
            remaining_days=item["remaining_days"],
            metadata=item["metadata"]
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recycle bin item: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取回收站项目失败: {str(e)}")

@router.post("/items/{recycle_bin_id}/restore", response_model=Dict[str, Any])
async def restore_item(recycle_bin_id: str):
    """从回收站恢复项目"""
    try:
        recycle_service = get_recycle_bin_service()
        success = recycle_service.restore(recycle_bin_id)
        
        if not success:
            raise HTTPException(
                status_code=400, 
                detail="恢复失败：项目不存在、已过期或原始ID冲突"
            )
        
        logger.info(f"Item restored from recycle bin: {sanitize_for_log(recycle_bin_id)}")
        
        return {
            "status": "success",
            "message": "项目已成功恢复",
            "recycle_bin_id": recycle_bin_id,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to restore item: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"恢复项目失败: {str(e)}")

@router.delete("/items/{recycle_bin_id}", response_model=Dict[str, Any])
async def permanent_delete_item(recycle_bin_id: str):
    """永久删除回收站项目"""
    try:
        recycle_service = get_recycle_bin_service()
        success = recycle_service.permanent_delete(recycle_bin_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"回收站项目未找到: {recycle_bin_id}")
        
        logger.info(f"Item permanently deleted from recycle bin: {sanitize_for_log(recycle_bin_id)}")
        
        return {
            "status": "success",
            "message": "项目已永久删除",
            "recycle_bin_id": recycle_bin_id,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to permanently delete item: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"永久删除失败: {str(e)}")

@router.post("/cleanup", response_model=Dict[str, Any])
async def cleanup_expired_items():
    """清理过期的回收站项目"""
    try:
        recycle_service = get_recycle_bin_service()
        cleaned_count = recycle_service.cleanup_expired_items()
        
        logger.info(f"Cleaned up {cleaned_count} expired recycle bin items")
        
        return {
            "status": "success",
            "message": f"已清理 {cleaned_count} 个过期项目",
            "cleaned_count": cleaned_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to cleanup expired items: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"清理过期项目失败: {str(e)}")

@router.get("/statistics", response_model=RecycleBinStatsResponse)
async def get_recycle_bin_statistics():
    """获取回收站统计信息"""
    try:
        recycle_service = get_recycle_bin_service()
        stats = recycle_service.get_statistics()
        
        return RecycleBinStatsResponse(
            total_items=stats["total_items"],
            by_type=stats["by_type"],
            expired_items=stats["expired_items"],
            expiring_soon=stats["expiring_soon"],
            oldest_item=stats["oldest_item"],
            newest_item=stats["newest_item"]
        )
    except Exception as e:
        logger.error(f"Failed to get recycle bin statistics: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@router.post("/empty", response_model=Dict[str, Any])
async def empty_recycle_bin(request: EmptyRecycleBinRequest):
    """清空回收站"""
    try:
        recycle_service = get_recycle_bin_service()
        deleted_count, skipped_count = recycle_service.empty_recycle_bin(force=request.force)
        
        logger.info(f"Recycle bin emptied: deleted {deleted_count}, skipped {skipped_count}")
        
        return {
            "status": "success",
            "message": f"回收站已清空：删除 {deleted_count} 项，跳过 {skipped_count} 项",
            "deleted_count": deleted_count,
            "skipped_count": skipped_count,
            "forced": request.force,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to empty recycle bin: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"清空回收站失败: {str(e)}")

@router.post("/batch-restore", response_model=Dict[str, Any])
async def batch_restore_items(recycle_bin_ids: List[str]):
    """批量恢复回收站项目"""
    try:
        recycle_service = get_recycle_bin_service()
        
        results = {"success": [], "failed": []}
        
        for recycle_bin_id in recycle_bin_ids:
            try:
                success = recycle_service.restore(recycle_bin_id)
                if success:
                    results["success"].append(recycle_bin_id)
                    logger.info(f"Batch restore success: {sanitize_for_log(recycle_bin_id)}")
                else:
                    results["failed"].append({
                        "id": recycle_bin_id,
                        "reason": "恢复失败：项目不存在、已过期或ID冲突"
                    })
            except Exception as e:
                results["failed"].append({
                    "id": recycle_bin_id,
                    "reason": str(e)
                })
        
        return {
            "status": "completed",
            "message": f"批量恢复完成：成功 {len(results['success'])} 项，失败 {len(results['failed'])} 项",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to batch restore items: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"批量恢复失败: {str(e)}")

@router.post("/batch-delete", response_model=Dict[str, Any])
async def batch_permanent_delete_items(recycle_bin_ids: List[str]):
    """批量永久删除回收站项目"""
    try:
        recycle_service = get_recycle_bin_service()
        
        results = {"success": [], "failed": []}
        
        for recycle_bin_id in recycle_bin_ids:
            try:
                success = recycle_service.permanent_delete(recycle_bin_id)
                if success:
                    results["success"].append(recycle_bin_id)
                    logger.info(f"Batch delete success: {sanitize_for_log(recycle_bin_id)}")
                else:
                    results["failed"].append({
                        "id": recycle_bin_id,
                        "reason": "删除失败：项目不存在"
                    })
            except Exception as e:
                results["failed"].append({
                    "id": recycle_bin_id,
                    "reason": str(e)
                })
        
        return {
            "status": "completed",
            "message": f"批量删除完成：成功 {len(results['success'])} 项，失败 {len(results['failed'])} 项",
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to batch delete items: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"批量删除失败: {str(e)}")

# 调度器管理相关API
@router.get("/scheduler/status", response_model=Dict[str, Any])
async def get_scheduler_status():
    """获取回收站调度器状态"""
    try:
        scheduler = get_recycle_bin_scheduler()
        status = scheduler.get_status()
        
        return {
            "status": "success",
            "scheduler": status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler status: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取调度器状态失败: {str(e)}")

@router.post("/scheduler/manual-cleanup", response_model=Dict[str, Any])
async def trigger_manual_cleanup():
    """手动触发过期项目清理"""
    try:
        result = await manual_cleanup_expired_items()
        return result
    except Exception as e:
        logger.error(f"Failed to trigger manual cleanup: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"手动清理失败: {str(e)}")

@router.get("/scheduler/statistics", response_model=Dict[str, Any])
async def get_scheduler_statistics():
    """获取回收站和调度器统计信息"""
    try:
        stats = get_cleanup_statistics()
        return {
            "status": "success",
            "data": stats,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get scheduler statistics: {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")