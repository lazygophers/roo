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
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path

# 最小导入
from app.core.config import API_PREFIX, DEBUG, LOG_LEVEL, PROJECT_ROOT
from app.routers.api_models import router as models_router
from app.routers.mcp import router as mcp_router
from app.routers.api_rules import router as rules_router
from app.routers.api_configurations import router as configurations_router
from app.routers.api_deploy import router as deploy_router
from app.routers.api_commands import router as commands_router
from app.routers.api_hooks import router as hooks_router
from app.routers.api_database import router as database_router
from app.routers.api_roles import router as roles_router
from app.routers.api_file_security import router as file_security_router
from app.routers.api_recycle_bin import router as recycle_bin_router
from app.routers.api_time_tools import router as time_tools_router
from app.routers.api_cache_tools import router as cache_tools_router
from app.routers.api_cache import router as cache_router
from app.routers.api_mcp_config import router as mcp_config_router
from app.routers.api_web_scraping import router as web_scraping_router

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

def get_database_service():
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

        startup_message = f"""
{"="*60}
🚀 LazyAI Studio 启动成功！(极致优化版)
📋 LazyGophers 出品 - 让 AI 替你思考，让工具替你工作！
{"="*60}

📍 访问地址:
   🏠 本地访问:    http://localhost:8000
   📖 API 文档:    http://localhost:8000/docs (调试模式)
   💚 健康检查:    http://localhost:8000/api/health

⚡ 性能优化特性:
   🔋 内存使用:    {end_memory:.1f}MB (目标 < 15MB)
   🚀 零缓存:      按需读取，无内存缓存
   🌊 流式处理:    大文件分块加载
   ♻️  垃圾回收:    智能内存清理

🔗 功能入口:
   📊 模型管理:    http://localhost:8000/api/models
   📈 系统状态:    http://localhost:8000/api/status
   🧹 内存清理:    http://localhost:8000/api/system/gc

{"="*60}
🎉 Ready! 开始你的极致性能 AI 懒人之旅吧！
{"="*60}
"""

        print(startup_message, flush=True)

    except Exception as e:
        get_logger().error(f"Startup error: {e}")
        raise

    yield

    # 清理
    if _db_service:
        _db_service.close()
    gc.collect()
    print("✅ 极致优化服务已安全关闭\n", flush=True)

# 创建应用 - 最小配置
app = FastAPI(
    title="LazyAI Studio (Minimal)",
    description="LazyGophers 出品 - 极致资源优化版 AI 智能工作室 API",
    version="1.0.0-minimal",
    debug=DEBUG,
    lifespan=lifespan,
    # 完全禁用文档以节省内存
    docs_url="/docs" if DEBUG else None,
    redoc_url="/redoc" if DEBUG else None,
    openapi_url="/openapi.json" if DEBUG else None,
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
        db = get_database_service()
        models = db.get_models_data()
        return {"success": True, "data": models, "total": len(models)}
    except Exception as e:
        get_logger().error("Error in list_models: %s", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

@app.get("/api/models/{slug}")
async def get_model(slug: str):
    """获取单个模型"""
    try:
        db = get_database_service()
        model = db.get_model_by_slug(slug)
        if model:
            return {"success": True, "data": model}
        return JSONResponse({"error": "Not found"}, status_code=404)
    except Exception as e:
        get_logger().error("Error in get_model: %s", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

@app.get("/api/models/group/{group}")
async def get_group_models(group: str):
    """获取组模型"""
    try:
        db = get_database_service()
        models = db.get_models_by_group(group)
        return {"success": True, "data": models, "total": len(models)}
    except Exception as e:
        get_logger().error("Error in get_group_models: %s", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

@app.post("/api/models/refresh")
async def refresh_models():
    """刷新模型缓存"""
    try:
        db = get_database_service()
        result = db.refresh_models_cache()
        # 手动触发垃圾回收
        gc.collect()
        return {"success": True, "data": result}
    except Exception as e:
        get_logger().error("Error in refresh_models: %s", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

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
            "success": True,
            "data": {
                "collected": collected,
                "before_mb": round(before_mb, 2),
                "after_mb": round(after_mb, 2),
                "freed_mb": round(freed_mb, 2)
            }
        }
    except Exception as e:
        get_logger().error("Error in force_gc: %s", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

@app.get("/api/status")
async def get_status():
    """系统状态"""
    try:
        import psutil
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        cpu_percent = process.cpu_percent()

        db = get_database_service()
        db_status = db.get_status()

        return {
            "success": True,
            "data": {
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
        }
    except Exception as e:
        get_logger().error("Error in get_status: %s", str(e))
        return JSONResponse({"error": "Internal server error"}, status_code=500)

# 健康检查
@app.get("/health")
@app.get("/api/health")
async def health():
    return {"status": "ok", "mode": "minimal"}

# Include additional routers
app.include_router(models_router, prefix="/api", tags=["models"])
app.include_router(mcp_router, prefix="/api", tags=["mcp"])
app.include_router(rules_router, prefix="/api", tags=["rules"])
app.include_router(configurations_router, prefix="/api", tags=["configurations"])
app.include_router(deploy_router, prefix="/api/deploy", tags=["deploy"])
app.include_router(commands_router, prefix="/api", tags=["commands"])
app.include_router(hooks_router, prefix="/api", tags=["hooks"])
app.include_router(database_router, prefix="/api", tags=["database"])
app.include_router(roles_router, prefix="/api", tags=["roles"])
app.include_router(file_security_router, prefix="/api", tags=["file-security"])
app.include_router(recycle_bin_router, prefix="/api", tags=["recycle-bin"])
app.include_router(time_tools_router, prefix="/api", tags=["time-tools"])
app.include_router(cache_tools_router, prefix="/api", tags=["cache-tools"])
app.include_router(cache_router, prefix="/api", tags=["cache"])
app.include_router(mcp_config_router, prefix="/api", tags=["mcp-config"])
app.include_router(web_scraping_router, prefix="/api", tags=["web-scraping"])

# 静态文件配置
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "build"
FRONTEND_STATIC_DIR = FRONTEND_BUILD_DIR / "static"

# 挂载前端静态资源
if FRONTEND_BUILD_DIR.exists():
    # 挂载静态文件目录
    if FRONTEND_STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_STATIC_DIR)), name="static")

    # SPA 路由处理 - 添加回退路由
    from fastapi import HTTPException

    @app.exception_handler(404)
    async def spa_handler(request, exc):
        # 如果请求的是 API 路径，返回 404
        if request.url.path.startswith('/api'):
            return JSONResponse(
                status_code=404,
                content={"detail": "Not Found"}
            )
        # 否则返回 index.html，让前端路由处理
        return FileResponse(FRONTEND_BUILD_DIR / "index.html")

    # 挂载前端应用
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD_DIR)), name="frontend")
else:
    # 根路径
    @app.get("/")
    async def root():
        try:
            import psutil
            memory_mb = psutil.Process().memory_info().rss / 1024 / 1024
            return {
                "message": "LazyAI Studio (Minimal)",
                "organization": "LazyGophers",
                "motto": "让 AI 替你思考，让工具替你工作，让你做个聪明的懒人！",
                "version": "1.0.0-minimal",
                "memory_mb": round(memory_mb, 2),
                "features": ["ultra_low_memory", "zero_cache", "minimal_deps"],
                "frontend_status": "not_built",
                "build_command": "cd frontend && npm run build",
                "docs": "/docs" if DEBUG else "disabled",
                "endpoints": {
                    "models": "/api/models",
                    "status": "/api/status",
                    "gc": "/api/system/gc"
                }
            }
        except Exception as e:
            get_logger().error("Error in root endpoint: %s", str(e))
            return {"error": "Internal server error"}

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