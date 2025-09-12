from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Any, Optional
from app.core.database_service import get_database_service
from app.core.unified_database import get_unified_database
from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log

logger = setup_logging("INFO")

router = APIRouter(prefix="/database", tags=["database"])

@router.get("/status", response_model=Dict[str, Any])
async def get_database_status():
    """获取数据库同步状态"""
    try:
        db_service = get_database_service()
        unified_db = get_unified_database()
        
        status = db_service.get_sync_status()
        tables_info = unified_db.get_all_tables()
        
        return {
            "success": True,
            "data": {
                "sync_status": status,
                "unified_database": {
                    "db_path": unified_db.db_path,
                    "tables": tables_info,
                    "total_records": sum(tables_info.values())
                }
            },
            "message": "Database status retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Failed to get database status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sync/{config_name}")
async def sync_config(config_name: str):
    """手动同步指定配置"""
    try:
        db_service = get_database_service()
        
        if config_name == "all":
            results = db_service.sync_all()
            return {
                "success": True,
                "data": results,
                "message": "All configurations synced successfully"
            }
        else:
            result = db_service.sync_config(config_name)
            return {
                "success": True,
                "data": {config_name: result},
                "message": f"Configuration '{config_name}' synced successfully"
            }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to sync config '{sanitize_for_log(config_name)}': {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/{config_name}")
async def get_cached_data(
    config_name: str,
    slug: Optional[str] = Query(None, description="Filter by slug"),
    name: Optional[str] = Query(None, description="Filter by name"),
    file_name: Optional[str] = Query(None, description="Filter by file name")
):
    """从缓存获取数据"""
    try:
        db_service = get_database_service()
        
        # 构建过滤条件
        filters = {}
        if slug:
            filters['content.slug'] = slug
        if name:
            filters['content.name'] = {'contains': name}
        if file_name:
            filters['file_name'] = file_name
        
        data = db_service.get_cached_data(config_name, filters)
        
        return {
            "success": True,
            "data": data,
            "count": len(data),
            "message": f"Data retrieved from '{config_name}' cache"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get cached data for '{sanitize_for_log(config_name)}': {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/file/{config_name}")
async def get_file_by_path(config_name: str, file_path: str = Query(...)):
    """根据文件路径获取特定文件数据"""
    try:
        db_service = get_database_service()
        file_data = db_service.get_file_by_path(config_name, file_path)
        
        if not file_data:
            raise HTTPException(
                status_code=404, 
                detail=f"File '{file_path}' not found in '{config_name}' cache"
            )
        
        return {
            "success": True,
            "data": file_data,
            "message": f"File data retrieved successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get file '{sanitize_for_log(file_path)}' from '{sanitize_for_log(config_name)}': {sanitize_for_log(str(e))}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models/fast", response_model=Dict[str, Any])
async def get_models_from_cache():
    """从数据库缓存快速获取模型数据（替代直接扫描文件系统）"""
    try:
        db_service = get_database_service()
        
        # 从缓存获取所有模型数据
        cached_models = db_service.get_cached_data("models")
        
        # 转换为符合API响应格式的数据
        models_list = []
        for file_data in cached_models:
            content = file_data.get('content', {})
            if content and isinstance(content, dict):
                model_info = {
                    'slug': content.get('slug', ''),
                    'name': content.get('name', ''),
                    'roleDefinition': content.get('roleDefinition', ''),
                    'whenToUse': content.get('whenToUse', ''),
                    'description': content.get('description', ''),
                    'groups': content.get('groups', []),
                    'file_path': file_data.get('file_path', ''),
                    'last_modified': file_data.get('last_modified'),
                    'file_hash': file_data.get('file_hash')
                }
                models_list.append(model_info)
        
        # 按 slug 排序
        models_list.sort(key=lambda x: x['slug'])
        
        return {
            "success": True,
            "data": models_list,
            "count": len(models_list),
            "message": "Models retrieved from cache successfully",
            "source": "database_cache"
        }
    except Exception as e:
        logger.error(f"Failed to get models from cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hooks/fast", response_model=Dict[str, Any])
async def get_hooks_from_cache():
    """从数据库缓存快速获取hooks数据"""
    try:
        db_service = get_database_service()
        cached_hooks = db_service.get_cached_data("hooks")
        
        return {
            "success": True,
            "data": cached_hooks,
            "count": len(cached_hooks),
            "message": "Hooks retrieved from cache successfully",
            "source": "database_cache"
        }
    except Exception as e:
        logger.error(f"Failed to get hooks from cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rules/fast", response_model=Dict[str, Any])
async def get_rules_from_cache():
    """从数据库缓存快速获取rules数据"""
    try:
        db_service = get_database_service()
        cached_rules = db_service.get_cached_data("rules")
        
        return {
            "success": True,
            "data": cached_rules,
            "count": len(cached_rules),
            "message": "Rules retrieved from cache successfully",
            "source": "database_cache"
        }
    except Exception as e:
        logger.error(f"Failed to get rules from cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/migrate")
async def migrate_databases():
    """手动执行数据库迁移（从旧数据库文件迁移到统一数据库）"""
    try:
        unified_db = get_unified_database()
        migration_log = unified_db.migrate_from_old_databases()
        
        return {
            "success": True,
            "data": {
                "migration_log": migration_log,
                "tables_after_migration": unified_db.get_all_tables()
            },
            "message": f"Database migration completed with {len(migration_log)} operations"
        }
    except Exception as e:
        logger.error(f"Failed to migrate databases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tables")
async def get_all_tables():
    """获取统一数据库中的所有表及其记录数"""
    try:
        unified_db = get_unified_database()
        tables_info = unified_db.get_all_tables()
        
        return {
            "success": True,
            "data": {
                "db_path": unified_db.db_path,
                "tables": tables_info,
                "total_tables": len(tables_info),
                "total_records": sum(tables_info.values())
            },
            "message": "Tables information retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Failed to get tables info: {e}")
        raise HTTPException(status_code=500, detail=str(e))