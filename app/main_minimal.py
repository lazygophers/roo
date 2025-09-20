"""
LazyAI Studio - Minimal Resource Edition
极致资源优化版本 - 最低内存和CPU使用

目标:
- 内存使用 < 15MB
- CPU使用 < 5%
- 启动时间 < 200ms
- 零缓存架构
"""

import gc
import os
import sys
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

# 最小导入
from app.core.config import DEBUG, LOG_LEVEL

# 全局变量 - 延迟初始化
_db_service = None
_logger = None

def get_logger():
    """延迟日志初始化"""
    global _logger
    if _logger is None:
        from app.core.logging import setup_logging
        _logger = setup_logging(LOG_LEVEL)
    return _logger

def get_db_service():
    """延迟数据库服务初始化"""
    global _db_service
    if _db_service is None:
        from app.core.database_service_minimal import init_minimal_database_service
        _db_service = init_minimal_database_service()
    return _db_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    """最小化生命周期管理"""
    # 启动优化
    gc.disable()  # 暂时禁用GC加速启动

    try:
        import psutil
        process = psutil.Process()
        start_memory = process.memory_info().rss / 1024 / 1024

        print(f"🚀 LazyAI Studio (Minimal) - Starting with {start_memory:.1f}MB", flush=True)

        # 启动后重新启用GC并优化
        gc.enable()
        gc.collect()

        end_memory = process.memory_info().rss / 1024 / 1024
        print(f"✅ Ready! Memory: {end_memory:.1f}MB (http://localhost:8000)", flush=True)

    except Exception as e:
        get_logger().error(f"Startup error: {e}")
        raise

    yield

    # 清理
    if _db_service:
        _db_service.close()
    gc.collect()
    print("✅ Minimal service closed", flush=True)

# 创建应用 - 最小配置
app = FastAPI(
    title="LazyAI Studio (Minimal)",
    version="1.0.0-minimal",
    debug=DEBUG,
    lifespan=lifespan,
    # 完全禁用文档以节省内存
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

# 最简异常处理
@app.exception_handler(Exception)
async def handle_error(request: Request, exc: Exception):
    get_logger().error(f"Error: {exc}")
    return JSONResponse({"error": "Internal error"}, status_code=500)

# 核心API端点
@app.get("/api/models")
async def list_models():
    """获取模型列表"""
    try:
        db = get_db_service()
        models = db.get_models_data()
        return {"data": models, "total": len(models)}
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/api/models/{slug}")
async def get_model(slug: str):
    """获取单个模型"""
    try:
        db = get_db_service()
        model = db.get_model_by_slug(slug)
        if model:
            return {"data": model}
        return {"error": "Not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/api/models/group/{group}")
async def get_group_models(group: str):
    """获取组模型"""
    try:
        db = get_db_service()
        models = db.get_models_by_group(group)
        return {"data": models, "total": len(models)}
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/api/system/gc")
async def force_gc():
    """手动垃圾回收"""
    try:
        import psutil
        process = psutil.Process()
        before_mb = process.memory_info().rss / 1024 / 1024

        collected = gc.collect()

        after_mb = process.memory_info().rss / 1024 / 1024
        freed_mb = before_mb - after_mb

        return {
            "collected": collected,
            "before_mb": round(before_mb, 2),
            "after_mb": round(after_mb, 2),
            "freed_mb": round(freed_mb, 2)
        }
    except Exception as e:
        return {"error": str(e)}, 500

@app.get("/api/status")
async def get_status():
    """系统状态"""
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()

        db = get_db_service()
        db_status = db.get_status()

        return {
            "version": "1.0.0-minimal",
            "memory_mb": round(memory_mb, 2),
            "cpu_percent": cpu_percent,
            "database": db_status,
            "optimizations": [
                "zero_cache",
                "minimal_imports",
                "lazy_loading",
                "stream_processing",
                "gc_tuning"
            ]
        }
    except Exception as e:
        return {"error": str(e)}, 500

# 健康检查
@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok", "mode": "minimal"}

# 根路径
@app.get("/")
async def root():
    try:
        import psutil
        memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
        return {
            "message": "LazyAI Studio (Minimal)",
            "version": "1.0.0-minimal",
            "memory_mb": round(memory_mb, 2),
            "features": ["ultra_low_memory", "zero_cache", "minimal_deps"],
            "endpoints": {
                "models": "/api/models",
                "status": "/api/status",
                "gc": "/api/system/gc"
            }
        }
    except Exception as e:
        return {"error": str(e)}

# 进程优化
try:
    # 设置较低优先级
    if hasattr(os, 'nice'):
        os.nice(10)

    # 优化GC
    gc.set_threshold(1000, 15, 15)

    # 在Unix系统上降低内存使用
    if hasattr(os, 'setrlimit'):
        import resource
        # 限制内存使用到50MB
        resource.setrlimit(resource.RLIMIT_AS, (50 * 1024 * 1024, -1))

except Exception:
    pass  # 忽略优化失败

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main_minimal:app",
        host="0.0.0.0",
        port=8002,
        reload=False,
        access_log=False,
        workers=1
    )