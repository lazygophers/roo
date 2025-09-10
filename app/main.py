from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.core.config import API_PREFIX, DEBUG, LOG_LEVEL, PROJECT_ROOT
from app.core.logging import setup_logging, log_error
from app.core.database_service import init_database_service, get_database_service
from app.routers import api_router

# 设置日志
logger = setup_logging(LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理"""
    # 启动时初始化数据库服务
    logger.info("Initializing application...")
    try:
        db_service = init_database_service()
        logger.info("Database service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database service: {e}")
        raise
    
    yield
    
    # 关闭时清理资源
    logger.info("Shutting down application...")
    try:
        db_service = get_database_service()
        db_service.close()
        logger.info("Database service closed successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

# 创建 FastAPI 应用
app = FastAPI(
    title="LazyAI Studio API",
    description="LazyGophers 出品 - 懒人的 AI 智能工作室 API，提供模式、角色、命令和规则的智能管理",
    version="1.0.0",
    debug=DEBUG,
    lifespan=lifespan
)

# 全局异常处理器
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

# CORS 中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=API_PREFIX)

# 静态文件配置
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
            "message": "LazyAI Studio API is running", 
            "organization": "LazyGophers",
            "motto": "让 AI 替你思考，让工具替你工作，让你做个聪明的懒人！",
            "mode": "development",
            "frontend_status": "not_built",
            "build_command": "cd frontend && npm run build",
            "docs": "/docs"
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}