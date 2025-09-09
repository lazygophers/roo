from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import API_PREFIX, DEBUG, LOG_LEVEL
from app.core.logging import setup_logging, log_error
from app.routers import api_router

# 设置日志
logger = setup_logging(LOG_LEVEL)

# 创建 FastAPI 应用
app = FastAPI(
    title="Roo Models API",
    description="API for accessing Roo model configurations",
    version="1.0.0",
    debug=DEBUG
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

@app.get("/")
async def root():
    return {"message": "Roo Models API is running", "docs": "/docs"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}