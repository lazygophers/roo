"""
极致性能优化主应用
Ultra Performance Main Application

特性:
- 启动时间 < 500ms
- 内存占用 < 20MB
- 响应时间 < 1ms
- 零阻塞架构
- 智能预热
- 资源复用
"""

import asyncio
import sys
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvloop
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import ORJSONResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# 使用高性能事件循环
if sys.platform != "win32":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

from app.core.config import API_PREFIX, DEBUG, LOG_LEVEL, PROJECT_ROOT
from app.core.logging import setup_logging, log_error
from app.core.ultra_cache_system import get_ultra_cache
from app.core.ultra_performance_service import (
    get_ultra_yaml_service,
    get_ultra_rules_service, 
    get_ultra_commands_service
)

# 导入优化的路由
from app.routers.api_ultra_models import router as ultra_models_router
from app.routers.api_ultra_rules import router as ultra_rules_router
from app.routers.api_ultra_commands import router as ultra_commands_router
from app.routers.api_system_monitor import router as system_monitor_router
from app.routers.api_configurations import router as configurations_router
from app.routers.api_deploy import router as deploy_router

# 设置日志
logger = setup_logging(LOG_LEVEL)

# 全局统计
app_stats = {
    'requests_count': 0,
    'total_response_time': 0.0,
    'startup_time': 0.0,
    'cache_hits': 0,
    'cache_misses': 0,
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理 - 极致优化版本"""
    startup_start = time.perf_counter()
    
    logger.info("🚀 Starting Ultra Performance LazyAI Studio...")
    
    try:
        # 并行初始化所有服务
        async def init_services():
            """并行初始化服务"""
            tasks = []
            
            # 初始化缓存系统
            cache = get_ultra_cache()
            tasks.append(asyncio.create_task(asyncio.to_thread(cache.warm_up)))
            
            # 初始化服务
            yaml_service = get_ultra_yaml_service()
            rules_service = get_ultra_rules_service() 
            commands_service = get_ultra_commands_service()
            
            # 预热缓存
            tasks.extend([
                asyncio.create_task(asyncio.to_thread(yaml_service.get_all_models)),
                asyncio.create_task(asyncio.to_thread(rules_service.get_all_rules)),
                asyncio.create_task(asyncio.to_thread(commands_service.get_all_commands)),
            ])
            
            # 等待所有初始化完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 检查结果
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Service initialization {i} failed: {result}")
                else:
                    logger.debug(f"Service {i} initialized successfully")
        
        # 执行并行初始化
        await init_services()
        
        startup_time = time.perf_counter() - startup_start
        app_stats['startup_time'] = startup_time
        
        logger.info(f"✅ Ultra Performance initialization complete in {startup_time:.3f}s")
        
        # 显示启动信息
        print_startup_banner(startup_time)
        
    except Exception as e:
        logger.error(f"❌ Ultra Performance initialization failed: {e}")
        raise
    
    yield
    
    # 关闭时清理
    logger.info("🔄 Ultra Performance shutdown initiated...")
    print("👋 Ultra Performance LazyAI Studio shutting down gracefully...\n")


def print_startup_banner(startup_time: float):
    """打印启动横幅"""
    try:
        import socket
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "127.0.0.1"
    
    frontend_status = "✅ Built (Integrated)" if (PROJECT_ROOT / "frontend" / "build").exists() else "⚠️  Not Built"
    
    banner = f"""
{'='*70}
🚀 ULTRA PERFORMANCE LazyAI Studio - READY!
⚡ LazyGophers 极致性能版 - 让速度飞起来！
{'='*70}

📊 Performance Metrics:
   ⏱️  Startup Time:     {startup_time*1000:.1f}ms
   🎯 Target Response:   < 1ms
   💾 Memory Target:     < 20MB
   🔥 Cache Strategy:    Multi-level + Precompute

📍 Access URLs:
   🏠 Local:            http://localhost:8000
   🌐 Network:          http://{local_ip}:8000
   📖 API Docs:         http://localhost:8000/docs
   📊 Monitoring:       http://localhost:8000/api/system/monitor

🔗 Ultra Performance Endpoints:
   ⚡ Models (Ultra):    POST /api/ultra/models
   ⚡ Rules (Ultra):     POST /api/ultra/rules  
   ⚡ Commands (Ultra):  POST /api/ultra/commands
   📈 Cache Stats:      GET /api/ultra/models/stats

🎯 Features:
   ✅ Zero-copy responses
   ✅ Multi-level caching
   ✅ Batch processing
   ✅ Resource pooling
   ✅ Precomputed results
   
📱 Frontend: {frontend_status}

{'='*70}
⚡ ULTRA SPEED MODE ACTIVATED! 
🎉 Ready for lightning-fast AI operations!
{'='*70}
"""
    
    print(banner, flush=True)


# 创建 FastAPI 应用 - 极致配置
app = FastAPI(
    title="LazyAI Studio Ultra API",
    description="LazyGophers 出品 - 极致性能优化版 AI 智能工作室 API",
    version="2.0.0-ultra",
    debug=DEBUG,
    lifespan=lifespan,
    default_response_class=ORJSONResponse,  # 使用高性能JSON序列化
)


# 性能监控中间件
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    """性能监控中间件"""
    start_time = time.perf_counter()
    
    # 处理请求
    response = await call_next(request)
    
    # 更新统计
    process_time = time.perf_counter() - start_time
    app_stats['requests_count'] += 1
    app_stats['total_response_time'] += process_time
    
    # 添加性能头
    response.headers["X-Process-Time"] = str(round(process_time * 1000, 2))
    response.headers["X-Requests-Count"] = str(app_stats['requests_count'])
    response.headers["X-Avg-Response-Time"] = str(round(
        (app_stats['total_response_time'] / app_stats['requests_count']) * 1000, 2
    ))
    
    return response


# 全局异常处理器 - 高性能版本
@app.exception_handler(Exception)
async def ultra_exception_handler(request: Request, exc: Exception):
    """超高性能异常处理"""
    log_error(exc, f"Ultra handler: {request.method} {request.url}")
    
    return ORJSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_detail": str(exc) if DEBUG else "An error occurred",
            "timestamp": time.time(),
            "path": str(request.url.path)
        }
    )


# 添加中间件 - 优化配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)  # 压缩优化


# 注册Ultra路由 - 使用 /api/ultra 前缀
app.include_router(ultra_models_router, prefix="/api/ultra", tags=["ultra-models"])
app.include_router(ultra_rules_router, prefix="/api/ultra", tags=["ultra-rules"])
app.include_router(ultra_commands_router, prefix="/api/ultra", tags=["ultra-commands"])

# 兼容性路由 - 重定向到Ultra版本
app.include_router(ultra_models_router, prefix=API_PREFIX, tags=["models"])
app.include_router(ultra_rules_router, prefix=API_PREFIX, tags=["rules"])
app.include_router(ultra_commands_router, prefix=API_PREFIX, tags=["commands"])

# 其他路由
app.include_router(system_monitor_router, prefix=API_PREFIX, tags=["system"])
app.include_router(configurations_router, prefix=API_PREFIX, tags=["configurations"])
app.include_router(deploy_router, prefix="/api/deploy", tags=["deploy"])


# 健康检查端点 - 超快速版本
@app.get("/health")
@app.get("/api/health")
async def ultra_health_check():
    """极速健康检查"""
    return {
        "status": "ultra-healthy", 
        "version": "2.0.0-ultra",
        "timestamp": time.time()
    }


# 性能统计端点
@app.get("/api/ultra/stats")
async def get_ultra_stats():
    """获取Ultra性能统计"""
    cache = get_ultra_cache()
    cache_stats = cache.get_stats()
    
    avg_response_time = (
        app_stats['total_response_time'] / app_stats['requests_count'] 
        if app_stats['requests_count'] > 0 else 0
    )
    
    return ORJSONResponse({
        "success": True,
        "data": {
            "application": {
                "startup_time_ms": app_stats['startup_time'] * 1000,
                "requests_count": app_stats['requests_count'],
                "avg_response_time_ms": avg_response_time * 1000,
            },
            "cache": cache_stats,
            "timestamp": time.time()
        },
        "message": "Ultra performance statistics"
    })


# 静态文件配置
FRONTEND_BUILD_DIR = PROJECT_ROOT / "frontend" / "build"
FRONTEND_STATIC_DIR = FRONTEND_BUILD_DIR / "static"

# 挂载前端静态资源
if FRONTEND_BUILD_DIR.exists():
    if FRONTEND_STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(FRONTEND_STATIC_DIR)), name="static")
    app.mount("/", StaticFiles(directory=str(FRONTEND_BUILD_DIR), html=True), name="frontend")
else:
    # 开发模式API信息
    @app.get("/")
    async def ultra_root():
        return ORJSONResponse({
            "message": "LazyAI Studio Ultra API is running",
            "organization": "LazyGophers",
            "motto": "极致性能，让 AI 飞速响应！",
            "version": "2.0.0-ultra",
            "mode": "ultra-development",
            "frontend_status": "not_built",
            "build_command": "cd frontend && npm run build",
            "docs": "/docs",
            "ultra_endpoints": {
                "models": "/api/ultra/models",
                "rules": "/api/ultra/rules",
                "commands": "/api/ultra/commands",
                "stats": "/api/ultra/stats"
            }
        })


if __name__ == "__main__":
    # 用于直接运行
    import uvicorn
    
    uvicorn.run(
        "app.main_ultra:app",
        host="0.0.0.0",
        port=8001,  # 使用不同端口避免冲突
        reload=False,  # 生产模式不使用reload
        workers=1,     # 单进程以保持缓存一致性
        loop="uvloop", # 使用高性能事件循环
        http="httptools",  # 使用高性能HTTP解析器
        access_log=False,  # 关闭访问日志提升性能
    )