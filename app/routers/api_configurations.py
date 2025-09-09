from typing import List, Dict, Any
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    SaveConfigurationRequest, 
    ConfigurationResponse, 
    ConfigurationListResponse,
    ConfigurationData
)
from app.core.database_service import get_database_service

router = APIRouter()

@router.post(
    "/config/save",
    response_model=ConfigurationResponse,
    summary="保存配置",
    description="保存用户选择的配置信息，支持覆盖保存"
)
async def save_configuration(request: SaveConfigurationRequest) -> ConfigurationResponse:
    """保存配置信息到数据库"""
    try:
        db_service = get_database_service()
        
        # 检查配置名称是否已存在
        existing_configs = db_service.get_cached_data_by_table("configurations")
        existing_config = None
        for config_data in existing_configs:
            if config_data.get('name') == request.name:
                existing_config = config_data
                break
        
        # 如果配置已存在且不允许覆盖，返回错误
        if existing_config and not request.overwrite:
            raise HTTPException(
                status_code=409,
                detail=f"配置 '{request.name}' 已存在，请启用覆盖选项或使用其他名称"
            )
        
        # 准备配置数据
        current_time = datetime.now().isoformat()
        config_data = {
            "name": request.name,
            "description": request.description,
            "selectedItems": [item.dict() for item in request.selectedItems],
            "modelRuleBindings": [binding.dict() for binding in request.modelRuleBindings],
            "modelRules": request.modelRules,
            "created_at": existing_config.get('created_at', current_time) if existing_config else current_time,
            "updated_at": current_time
        }
        
        # 保存到数据库
        if existing_config:
            # 更新现有配置
            db_service.update_cached_data("configurations", request.name, config_data)
            message = f"配置 '{request.name}' 已成功更新"
        else:
            # 创建新配置
            db_service.add_cached_data("configurations", config_data)
            message = f"配置 '{request.name}' 已成功保存"
        
        return ConfigurationResponse(
            success=True,
            message=message,
            data=ConfigurationData(**config_data)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"保存配置失败: {str(e)}"
        )


@router.post(
    "/config/list",
    response_model=ConfigurationListResponse,
    summary="获取配置列表",
    description="获取所有已保存的配置信息"
)
async def get_configurations() -> ConfigurationListResponse:
    """获取所有配置信息"""
    try:
        db_service = get_database_service()
        cached_configs = db_service.get_cached_data_by_table("configurations")
        
        # 转换为ConfigurationData对象
        configurations = []
        for config_data in cached_configs:
            config_obj = ConfigurationData(**config_data)
            configurations.append(config_obj)
        
        # 按更新时间倒序排序
        configurations.sort(key=lambda x: x.updated_at or x.created_at or "", reverse=True)
        
        return ConfigurationListResponse(
            success=True,
            message=f"成功获取 {len(configurations)} 个配置",
            data=configurations,
            total=len(configurations)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取配置列表失败: {str(e)}"
        )


@router.delete(
    "/config/{config_name}",
    response_model=ConfigurationResponse,
    summary="删除配置",
    description="删除指定名称的配置"
)
async def delete_configuration(config_name: str) -> ConfigurationResponse:
    """删除配置"""
    try:
        db_service = get_database_service()
        
        # 检查配置是否存在
        existing_configs = db_service.get_cached_data("configurations")
        config_exists = any(config.get('name') == config_name for config in existing_configs)
        
        if not config_exists:
            raise HTTPException(
                status_code=404,
                detail=f"配置 '{config_name}' 不存在"
            )
        
        # 删除配置
        db_service.remove_cached_data("configurations", config_name)
        
        return ConfigurationResponse(
            success=True,
            message=f"配置 '{config_name}' 已成功删除"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"删除配置失败: {str(e)}"
        )


@router.get(
    "/config/{config_name}",
    response_model=ConfigurationResponse,
    summary="获取单个配置",
    description="根据名称获取指定配置的详细信息"
)
async def get_configuration(config_name: str) -> ConfigurationResponse:
    """获取单个配置信息"""
    try:
        db_service = get_database_service()
        cached_configs = db_service.get_cached_data_by_table("configurations")
        
        # 查找指定配置
        target_config = None
        for config_data in cached_configs:
            if config_data.get('name') == config_name:
                target_config = config_data
                break
        
        if not target_config:
            raise HTTPException(
                status_code=404,
                detail=f"配置 '{config_name}' 不存在"
            )
        
        return ConfigurationResponse(
            success=True,
            message=f"成功获取配置 '{config_name}'",
            data=ConfigurationData(**target_config)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取配置失败: {str(e)}"
        )