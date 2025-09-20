from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.core.config import API_PREFIX, DEBUG, LOG_LEVEL, PROJECT_ROOT, ENVIRONMENT, CORS_ORIGINS, CORS_ALLOW_CREDENTIALS
from app.core.logging import setup_logging, log_error
from app.core.database_service_lite import init_lite_database_service, get_lite_database_service
from app.routers import api_router

# 设置日志
logger = setup_logging(LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理（优化版本）"""
    # 启动时快速初始化
    logger.info("Initializing optimized application...")
    try:
        # 使用轻量级数据库服务
        db_service = init_lite_database_service()
        logger.info("Lite database service initialized successfully")
        
        # 简化启动信息
        import socket
        import sys
        
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "127.0.0.1"
        
        startup_message = f"""
{"="*60}
🚀 LazyAI Studio (Optimized) 启动成功！
📋 LazyGophers 出品 - 让 AI 替你思考，让工具替你工作！
{"="*60}

📍 访问地址:
   🏠 本地访问:    http://localhost:8000
   🌐 局域网访问:  http://{local_ip}:8000

🔗 功能入口:
   📊 配置管理:    http://localhost:8000/
   📖 API 文档:    http://localhost:8000/docs
   💚 健康检查:    http://localhost:8000/api/health

⚙️  环境配置:
   🌍 运行环境:    {ENVIRONMENT.upper()}
   🔧 调试模式:    {'启用' if DEBUG else '禁用'}
   📝 日志级别:    {LOG_LEVEL}"""

        # 快速检查前端构建状态
        frontend_build = PROJECT_ROOT / "frontend" / "build"
        if frontend_build.exists():
            startup_message += "\n   ✅ 前端状态:    已构建 (集成模式)"
        else:
            startup_message += "\n   ⚠️  前端状态:    未构建 (API 模式)"
        
        startup_message += f"""

🎯 性能优化特性:
   ⚡ 懒加载:      按需加载模型文件
   🧠 智能缓存:    LRU + 内存缓存
   🚀 快速启动:    移除文件监控
   📉 低内存:      优化数据结构

{"="*60}
🎉 Ready! 开始你的高性能 AI 懒人之旅吧！
{"="*60}
"""
        
        print(startup_message, flush=True)
        sys.stdout.flush()
        
    except Exception as e:
        logger.error(f"Failed to initialize lite database service: {e}")
        raise
    
    yield
    
    # 关闭时清理资源
    logger.info("Shutting down optimized application...")
    shutdown_message = """
👋 LazyAI Studio (Optimized) 正在关闭...
📋 LazyGophers - 感谢使用我们的高性能懒人工具！
"""
    print(shutdown_message, flush=True)
    
    try:
        db_service = get_lite_database_service()
        db_service.close()
        logger.info("Lite database service closed successfully")
        print("✅ 服务已安全关闭\n", flush=True)
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        print(f"⚠️ 关闭过程中出现错误: {e}\n", flush=True)

# 创建优化的 FastAPI 应用
app = FastAPI(
    title="LazyAI Studio API (Optimized)",
    description="LazyGophers 出品 - 懒人的 AI 智能工作室 API（性能优化版），提供高性能的模式、角色、命令和规则管理",
    version="1.1.0-optimized",
    debug=DEBUG,
    lifespan=lifespan
)

# 全局异常处理器（简化版本）
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_error(exc, f"Global handler for {request.method} {request.url}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_detail": str(exc) if DEBUG else "An error occurred"
        }
    )

# CORS 中间件配置（基于环境）
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # 基于环境的来源配置
    allow_credentials=CORS_ALLOW_CREDENTIALS,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 允许的HTTP方法
    allow_headers=["Content-Type", "Authorization"],  # 允许的请求头
)

# 注册路由
app.include_router(api_router, prefix=API_PREFIX)

# 健康检查端点（增强版本）
@app.get("/health")
async def health_check():
    try:
        db_service = get_lite_database_service()
        status = db_service.get_status()
        return {"status": "healthy", "service": status}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api/health")
async def api_health_check():
    return await health_check()

# 性能监控端点
@app.get("/api/performance")
async def performance_info():
    try:
        db_service = get_lite_database_service()
        status = db_service.get_status()
        return {
            "performance": "optimized",
            "features": [
                "lazy_loading",
                "lru_cache", 
                "memory_cache",
                "fast_startup",
                "no_file_watching"
            ],
            "cache_stats": {
                "memory_cache_size": status.get("memory_cache_size", 0),
                "lru_cache_hits": status.get("lru_cache_hits", 0),
                "lru_cache_misses": status.get("lru_cache_misses", 0)
            }
        }
    except Exception as e:
        return {"error": str(e)}

# 静态文件配置（保持不变）
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "build"
FRONTEND_STATIC_DIR = FRONTEND_BUILD_DIR / "static"

# 挂载前端静态资源
if FRONTEND_BUILD_DIR.exists():
    # 挂载静态文件目录
    if FRONTEND_STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_STATIC_DIR)), name="static")
    
    # 挂载前端应用
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD_DIR), html=True), name="frontend")
else:
    # 如果前端构建目录不存在，显示开发模式的 API 信息
    @app.get("/")
    async def root():
        return {
            "message": "LazyAI Studio API (Optimized) is running", 
            "organization": "LazyGophers",
            "motto": "让 AI 替你思考，让工具替你工作，让你做个聪明的懒人！",
            "version": "1.1.0-optimized",
            "mode": "development",
            "frontend_status": "not_built",
            "performance_features": [
                "lazy_loading",
                "lru_cache", 
                "memory_cache",
                "fast_startup",
                "no_file_watching"
            ],
            "build_command": "cd frontend && npm run build",
            "docs": "/docs"
        }