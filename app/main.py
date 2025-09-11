from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
from app.core.config import API_PREFIX, DEBUG, LOG_LEVEL, PROJECT_ROOT
from app.core.logging import setup_logging, log_error
from app.core.database_service import init_database_service, get_database_service
from app.core.mcp_tools_service import init_mcp_tools_service
from app.core.mcp_server import init_mcp_server
from app.routers import api_router

# 设置日志
logger = setup_logging(LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 生命周期管理"""
    # 启动时初始化服务
    logger.info("Initializing application...")
    try:
        # 初始化数据库服务
        db_service = init_database_service()
        logger.info("Database service initialized successfully")
        
        # 初始化MCP工具服务
        mcp_tools_service = init_mcp_tools_service()
        logger.info("MCP tools service initialized successfully")
        
        # 初始化MCP服务器
        mcp_server = init_mcp_server()
        logger.info("MCP server initialized successfully")
        
        # 打印启动信息和访问地址
        import socket
        import sys
        
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
        except Exception:
            local_ip = "127.0.0.1"
        
        startup_message = f"""
{"="*60}
🚀 LazyAI Studio 启动成功！
📋 LazyGophers 出品 - 让 AI 替你思考，让工具替你工作！
{"="*60}

📍 访问地址:
   🏠 本地访问:    http://localhost:8000
   🌐 局域网访问:  http://{local_ip}:8000
   📱 移动设备:    http://{local_ip}:8000

🔗 功能入口:
   📊 配置管理:    http://localhost:8000/
   📖 API 文档:    http://localhost:8000/docs
   💚 健康检查:    http://localhost:8000/api/health
   🔧 MCP 工具:    http://localhost:8000/api/mcp/tools
   📊 MCP 状态:    http://localhost:8000/api/mcp/status"""

        # 检查前端构建状态
        frontend_build = PROJECT_ROOT / "frontend" / "build"
        if frontend_build.exists():
            startup_message += "\n   ✅ 前端状态:    已构建 (集成模式)"
        else:
            startup_message += "\n   ⚠️  前端状态:    未构建 (API 模式)"
            startup_message += "\n   💡 构建提示:    运行 'make build' 构建前端"
        
        startup_message += f"""

🎯 快速开始:
   📚 查看帮助:    make help
   🏗️ 构建前端:    make build
   🧪 运行测试:    make test
   🧹 清理文件:    make clean

{"="*60}
🎉 Ready! 开始你的 AI 懒人之旅吧！
{"="*60}
"""
        
        print(startup_message, flush=True)
        sys.stdout.flush()
        
    except Exception as e:
        logger.error(f"Failed to initialize database service: {e}")
        raise
    
    yield
    
    # 关闭时清理资源
    logger.info("Shutting down application...")
    shutdown_message = """
👋 LazyAI Studio 正在关闭...
📋 LazyGophers - 感谢使用我们的懒人工具！
"""
    print(shutdown_message, flush=True)
    
    try:
        db_service = get_database_service()
        db_service.close()
        logger.info("Database service closed successfully")
        print("✅ 服务已安全关闭\n", flush=True)
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")
        print(f"⚠️ 关闭过程中出现错误: {e}\n", flush=True)

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

# 健康检查端点 - 必须在静态文件挂载之前定义
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy"}

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