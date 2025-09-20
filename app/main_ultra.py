"""
LazyAI Studio - Ultra Performance Edition
超高性能版本 - 极致优化内存和CPU使用

优化特性:
- 移除所有非必要服务和中间件
- 懒加载所有组件
- 最小化内存占用
- 减少CPU周期
- 优化启动时间
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from typing import Optional
import gc
import os
import psutil

# 只导入必要的配置
from app.core.config import API_PREFIX, DEBUG, LOG_LEVEL, ENVIRONMENT

# 延迟导入优化 - 只在需要时导入
_database_service = None
_logger = None

def get_logger():
    """延迟初始化日志"""
    global _logger
    if _logger is None:
        from app.core.logging import setup_logging
        _logger = setup_logging(LOG_LEVEL)
    return _logger

def get_database_service():
    """延迟初始化数据库服务"""
    global _database_service
    if _database_service is None:
        from app.core.database_service_lite import init_lite_database_service
        _database_service = init_lite_database_service(use_unified_db=True)
    return _database_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """超轻量级生命周期管理"""
    logger = get_logger()
    logger.info("Initializing ultra-optimized application...")

    try:
        # 强制垃圾回收，释放启动时的临时对象
        gc.collect()

        # 简化启动信息
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024

        startup_message = f"""
🚀 LazyAI Studio (Ultra) - Memory: {memory_mb:.1f}MB
⚡ 极致性能模式启动完成！
📍 http://localhost:8000
"""
        print(startup_message, flush=True)

    except Exception as e:
        logger.error(f"Startup error: {e}")
        raise

    yield

    # 清理资源
    logger = get_logger()
    logger.info("Shutting down ultra application...")

    if _database_service:
        _database_service.close()

    # 强制垃圾回收
    gc.collect()
    print("✅ Ultra service closed\n", flush=True)

# 创建最小化的 FastAPI 应用
app = FastAPI(
    title="LazyAI Studio (Ultra)",
    description="超高性能版 - 极致优化内存和CPU使用",
    version="1.2.0-ultra",
    debug=DEBUG,
    lifespan=lifespan,
    # 禁用自动文档生成以节省内存
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
)

# 简化的异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger = get_logger()
    logger.error(f"Error in {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"}
    )

# 最小化CORS配置
if ENVIRONMENT == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )
else:
    # 生产环境更严格的CORS配置
    from app.core.config import CORS_ORIGINS, CORS_ALLOW_CREDENTIALS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )

# 延迟加载路由
@app.get("/api/models")
async def get_models():
    """延迟加载模型数据"""
    db_service = get_database_service()
    models = db_service.get_models_data()
    return {"success": True, "data": models, "total": len(models)}

@app.get("/api/models/{slug}")
async def get_model(slug: str):
    """获取单个模型"""
    db_service = get_database_service()
    model = db_service.get_model_by_slug(slug)
    if model:
        return {"success": True, "data": model}
    return {"success": False, "message": "Model not found"}

@app.get("/api/models/group/{group}")
async def get_models_by_group(group: str):
    """按组获取模型"""
    db_service = get_database_service()
    models = db_service.get_models_by_group(group)
    return {"success": True, "data": models, "total": len(models)}

@app.post("/api/models/refresh")
async def refresh_models():
    """刷新模型缓存"""
    db_service = get_database_service()
    result = db_service.refresh_models_cache()

    # 手动触发垃圾回收
    gc.collect()

    return {"success": True, "data": result}

@app.get("/api/system/status")
async def system_status():
    """系统状态"""
    process = psutil.Process()
    memory_info = process.memory_info()

    db_service = get_database_service()
    db_status = db_service.get_status()

    return {
        "success": True,
        "data": {
            "version": "1.2.0-ultra",
            "mode": "ultra_performance",
            "memory_mb": round(memory_info.rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(),
            "database": db_status,
            "optimizations": [
                "lazy_loading",
                "minimal_imports",
                "gc_optimization",
                "memory_pooling",
                "no_file_watching",
                "simplified_middleware"
            ]
        }
    }

@app.post("/api/system/gc")
async def force_garbage_collection():
    """手动触发垃圾回收"""
    collected = gc.collect()
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024

    return {
        "success": True,
        "data": {
            "collected_objects": collected,
            "memory_mb": round(memory_mb, 2)
        }
    }

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy", "mode": "ultra"}

@app.get("/api/health")
async def api_health_check():
    return await health_check()

# 根路径信息
@app.get("/")
async def root():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024

    return {
        "message": "LazyAI Studio API (Ultra Performance)",
        "organization": "LazyGophers",
        "version": "1.2.0-ultra",
        "mode": "ultra_performance",
        "memory_mb": round(memory_mb, 2),
        "features": [
            "极致内存优化",
            "CPU使用最小化",
            "懒加载架构",
            "垃圾回收优化"
        ],
        "docs": "/docs" if DEBUG else "disabled"
    }

# 如果需要完整API，可以动态加载
@app.get("/api/load-full-features")
async def load_full_features():
    """动态加载完整功能（仅在需要时）"""
    try:
        # 动态导入完整路由
        from app.routers import api_router
        app.include_router(api_router, prefix=API_PREFIX)

        return {
            "success": True,
            "message": "Full features loaded",
            "warning": "Memory usage will increase"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to load full features: {e}"
        }

# 设置进程优先级（如果是Linux/Unix系统）
try:
    if hasattr(os, 'nice'):
        # 设置较低的进程优先级以减少CPU竞争
        os.nice(5)
except:
    pass

# 优化垃圾回收设置
gc.set_threshold(700, 10, 10)  # 更保守的GC设置