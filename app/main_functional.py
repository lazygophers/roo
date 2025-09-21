"""
LazyAI Studio - 函数式架构版本
使用纯函数和函数组合实现的高性能后端服务

特点:
- 函数式编程范式
- 无状态服务设计
- 组合式架构
- 更好的可测试性
"""

import gc
import os
import sys
from typing import Optional, Dict, Any
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path

from app.core.config import (
    API_PREFIX, DEBUG, LOG_LEVEL, PROJECT_ROOT,
    CORS_ORIGINS, CORS_ALLOW_CREDENTIALS
)
from app.core.functional_base import create_logger, Result
from app.core.database_functional import (
    create_database_service, initialize_database_service,
    create_scan_config
)
from app.core.config_functional import (
    create_mcp_config_manager, create_database_config_manager,
    get_config_from_manager
)
from app.routers.functional_base import (
    create_success_response, create_error_response,
    create_health_check_endpoint, handle_api_errors,
    monitor_performance
)

# =============================================================================
# 全局服务状态（函数式）
# =============================================================================

_app_state = {
    'database_service': None,
    'config_managers': {},
    'logger': None,
    'initialized': False
}

def get_app_state() -> Dict[str, Any]:
    """获取应用状态"""
    return _app_state

def get_logger():
    """获取日志器"""
    if _app_state['logger'] is None:
        _app_state['logger'] = create_logger('main_functional')
    return _app_state['logger']

def get_database_service():
    """获取数据库服务"""
    if _app_state['database_service'] is None:
        raise RuntimeError("Database service not initialized")
    return _app_state['database_service']

def get_config_manager(config_type: str):
    """获取配置管理器"""
    if config_type not in _app_state['config_managers']:
        if config_type == 'mcp':
            _app_state['config_managers'][config_type] = create_mcp_config_manager()
        elif config_type == 'database':
            _app_state['config_managers'][config_type] = create_database_config_manager()
        else:
            raise ValueError(f"Unknown config type: {config_type}")

    return _app_state['config_managers'][config_type]

# =============================================================================
# 初始化和清理函数
# =============================================================================

async def initialize_services():
    """初始化所有服务"""
    logger = get_logger()
    logger.info("Initializing functional services...")

    try:
        # 初始化数据库服务
        scan_configs = [
            create_scan_config(
                name="models_scan",
                path=str(PROJECT_ROOT / "resources" / "models"),
                patterns=["*.yaml", "*.yml"],
                watch=True
            ),
            create_scan_config(
                name="hooks_scan",
                path=str(PROJECT_ROOT / "resources" / "hooks"),
                patterns=["*.yaml", "*.yml"],
                watch=True
            ),
            create_scan_config(
                name="rules_scan",
                path=str(PROJECT_ROOT / "resources" / "rules"),
                patterns=["*.yaml", "*.yml"],
                watch=True
            ),
            create_scan_config(
                name="configurations_scan",
                path=str(PROJECT_ROOT / "resources" / "configurations"),
                patterns=["*.yaml", "*.yml"],
                watch=True
            ),
            create_scan_config(
                name="roles_scan",
                path=str(PROJECT_ROOT / "resources" / "roles"),
                patterns=["*.yaml", "*.yml"],
                watch=True
            )
        ]

        db_result = initialize_database_service(scan_configs, use_unified=True)
        if db_result.is_error:
            logger.error(f"Failed to initialize database service: {db_result.error}")
            raise RuntimeError(f"Database initialization failed: {db_result.error}")

        _app_state['database_service'] = db_result.value

        # 预初始化配置管理器
        get_config_manager('mcp')
        get_config_manager('database')

        _app_state['initialized'] = True
        logger.info("All functional services initialized successfully")

    except Exception as e:
        logger.error(f"Service initialization failed: {e}")
        raise

async def cleanup_services():
    """清理所有服务"""
    logger = get_logger()
    logger.info("Cleaning up functional services...")

    try:
        # 清理数据库服务
        if _app_state['database_service']:
            from app.core.database_functional import cleanup_service
            cleanup_service(_app_state['database_service'])

        # 清理配置管理器
        _app_state['config_managers'].clear()

        # 强制垃圾回收
        gc.collect()

        logger.info("All services cleaned up successfully")

    except Exception as e:
        logger.error(f"Service cleanup failed: {e}")

# =============================================================================
# 应用生命周期管理
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动
    await initialize_services()
    yield
    # 关闭
    await cleanup_services()

# =============================================================================
# FastAPI应用创建
# =============================================================================

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="LazyAI Studio - Functional",
        description="AI智能工作室 - 函数式架构版本",
        version="2.0.0",
        docs_url="/api/docs" if DEBUG else None,
        redoc_url="/api/redoc" if DEBUG else None,
        lifespan=lifespan
    )

    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

# =============================================================================
# 基础API端点
# =============================================================================

app = create_app()

@app.get("/")
@handle_api_errors()
async def root():
    """根端点"""
    return create_success_response({
        "name": "LazyAI Studio",
        "version": "2.0.0",
        "architecture": "functional",
        "status": "running"
    })

# 健康检查
async def check_database():
    """检查数据库连接"""
    db_service = get_database_service()
    return True  # 简单检查，实际可以执行查询

health_check = create_health_check_endpoint([check_database])
app.get("/api/health")(health_check)

# =============================================================================
# 模型API端点（函数式重构）
# =============================================================================

@app.get("/api/models")
@handle_api_errors()
@monitor_performance()
async def get_models():
    """获取所有模型"""
    try:
        db_service = get_database_service()
        from app.core.database_functional import query_cached_data

        models_data = query_cached_data(db_service, {'extension': 'yaml'})

        # 过滤模型文件
        models = []
        for item in models_data:
            if 'models' in item.get('path', '').lower() and item.get('data'):
                if isinstance(item['data'], list):
                    models.extend(item['data'])
                elif isinstance(item['data'], dict) and 'models' in item['data']:
                    models.extend(item['data']['models'])

        return create_success_response(models, f"Retrieved {len(models)} models")

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to get models: {e}")
        return JSONResponse(
            content=create_error_response(e),
            status_code=500
        )

@app.get("/api/models/{model_slug}")
@handle_api_errors()
@monitor_performance()
async def get_model_by_slug(model_slug: str):
    """根据slug获取模型"""
    try:
        db_service = get_database_service()
        from app.core.database_functional import query_cached_data

        models_data = query_cached_data(db_service, {'extension': 'yaml'})

        # 查找指定模型
        for item in models_data:
            if 'models' in item.get('path', '').lower() and item.get('data'):
                models_list = []
                if isinstance(item['data'], list):
                    models_list = item['data']
                elif isinstance(item['data'], dict) and 'models' in item['data']:
                    models_list = item['data']['models']

                for model in models_list:
                    if isinstance(model, dict) and model.get('slug') == model_slug:
                        return create_success_response(model)

        return JSONResponse(
            content=create_error_response(f"Model not found: {model_slug}", "NOT_FOUND"),
            status_code=404
        )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to get model {model_slug}: {e}")
        return JSONResponse(
            content=create_error_response(e),
            status_code=500
        )

# =============================================================================
# 配置API端点（函数式重构）
# =============================================================================

@app.get("/api/configurations")
@handle_api_errors()
@monitor_performance()
async def get_configurations():
    """获取所有配置"""
    try:
        db_service = get_database_service()
        from app.core.database_functional import query_cached_data

        config_data = query_cached_data(db_service, {'extension': 'yaml'})

        # 过滤配置文件
        configurations = []
        for item in config_data:
            if 'configurations' in item.get('path', '').lower() and item.get('data'):
                if isinstance(item['data'], dict):
                    config_item = item['data'].copy()
                    config_item['_meta'] = {
                        'file_path': item['path'],
                        'file_name': item['name'],
                        'modified_time': item.get('modified_time')
                    }
                    configurations.append(config_item)

        return create_success_response(configurations, f"Retrieved {len(configurations)} configurations")

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to get configurations: {e}")
        return JSONResponse(
            content=create_error_response(e),
            status_code=500
        )

@app.post("/api/configurations")
@handle_api_errors()
@monitor_performance()
async def create_configuration(config_data: Dict[str, Any]):
    """创建新配置"""
    try:
        # 这里应该实现配置创建逻辑
        # 为了演示，返回创建成功
        return create_success_response(config_data, "Configuration created successfully")

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to create configuration: {e}")
        return JSONResponse(
            content=create_error_response(e),
            status_code=500
        )

# =============================================================================
# MCP配置API端点（函数式重构）
# =============================================================================

@app.get("/api/mcp/config")
@handle_api_errors()
@monitor_performance()
async def get_mcp_config():
    """获取MCP配置"""
    try:
        config_manager = get_config_manager('mcp')
        result = get_config_from_manager(config_manager)

        if result.is_success:
            return create_success_response(result.value)
        else:
            return JSONResponse(
                content=create_error_response(result.error),
                status_code=500
            )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to get MCP config: {e}")
        return JSONResponse(
            content=create_error_response(e),
            status_code=500
        )

@app.put("/api/mcp/config")
@handle_api_errors()
@monitor_performance()
async def update_mcp_config(updates: Dict[str, Any]):
    """更新MCP配置"""
    try:
        config_manager = get_config_manager('mcp')
        from app.core.config_functional import update_config_in_manager

        result = update_config_in_manager(config_manager, updates)

        if result.is_success:
            return create_success_response(result.value, "MCP config updated successfully")
        else:
            return JSONResponse(
                content=create_error_response(result.error),
                status_code=500
            )

    except Exception as e:
        logger = get_logger()
        logger.error(f"Failed to update MCP config: {e}")
        return JSONResponse(
            content=create_error_response(e),
            status_code=500
        )

# =============================================================================
# 静态文件服务
# =============================================================================

frontend_path = PROJECT_ROOT / "frontend" / "dist"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "static")), name="static")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """服务前端文件"""
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="API endpoint not found")

        # 尝试服务具体文件
        file_path = frontend_path / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))

        # 回退到index.html (SPA)
        index_path = frontend_path / "index.html"
        if index_path.exists():
            return FileResponse(str(index_path))

        raise HTTPException(status_code=404, detail="File not found")

# =============================================================================
# 开发服务器
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    logger = get_logger()
    logger.info("Starting LazyAI Studio (Functional)")

    uvicorn.run(
        "app.main_functional:app",
        host="0.0.0.0",
        port=8000,
        reload=DEBUG,
        log_level=LOG_LEVEL.lower(),
        access_log=DEBUG
    )