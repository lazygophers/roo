"""
FastAPI + Vue3 应用主模块

本模块作为整个应用的入口点，提供了以下核心功能：
1. HTTP 请求日志记录 - 记录所有请求的详细信息用于调试和监控
2. API 路由注册 - 将所有 API 端点挂载到 /api 路径下
3. 静态文件服务 - 为前端提供静态资源访问
4. 单页应用支持 - 处理 Vue Router 的 HTML5 History 模式
5. 开发服务器欢迎页面 - 提供友好的开发环境入口

主要特性：
- 结构化日志记录：使用 Python logging 模块记录所有 HTTP 请求，包含请求方法、路径、状态码等关键信息
- 智能路由优先级：按照 API 请求 > 静态文件 > SPA 前端路由的顺序处理请求
- 错误处理：为 404 错误提供自定义的 JSON 响应，符合 REST API 规范
- 开发友好：在开发模式下提供带有项目信息的欢迎页面

作者: Claude
创建日期: 2025-06-18
版本: 1.0.0
"""

from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from pathlib import Path
import os
import time
import json
from app.api.routes import router as api_router
from app.utils.logger import get_logger

# 初始化日志系统 - 获取当前模块的日志记录器实例
logger = get_logger(__name__)

# 初始化 FastAPI 应用实例
# 配置应用的基本信息，这些信息会显示在自动生成的 API 文档中
app = FastAPI(
    title="Python + Vue3 示例服务",
    description="一个使用 FastAPI + Vue3 + TypeScript 的示例应用",
    version="0.1.0"
)

# HTTP请求日志中间件
# 这是一个FastAPI的HTTP中间件，用于记录所有传入请求的详细信息
# 包括请求开始、完成和错误情况，便于调试和监控
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    HTTP请求日志中间件
    
    该中间件拦截所有HTTP请求，记录请求和响应的详细信息，
    包括客户端IP、请求方法、URL、用户代理、处理时间和状态码。
    使用结构化日志格式，便于后续分析和监控。
    
    功能特性：
    - 记录请求开始时间和基本信息
    - 计算并记录请求处理耗时
    - 捕获并记录处理过程中的异常
    - 使用extra字段提供结构化日志数据
    
    Args:
        request (Request): FastAPI请求对象，包含HTTP请求的所有信息
        call_next (Callable): 调用下一个中间件或路由处理函数的可调用对象
        
    Returns:
        Response: HTTP响应对象，包含处理结果
        
    Raises:
        Exception: 重新抛出请求处理过程中的任何异常
    """
    # 记录请求开始时间 - 用于计算请求处理耗时
    start_time = time.time()
    
    # 提取请求基本信息
    # - client_ip: 客户端IP地址，如果无法获取则标记为"unknown"
    # - method: HTTP请求方法（GET、POST等）
    # - url: 完整的请求URL
    # - user_agent: 用户代理字符串，用于识别客户端类型
    client_ip = request.client.host if request.client else "unknown"
    method = request.method
    url = str(request.url)
    user_agent = request.headers.get("user-agent", "unknown")
    
    # 记录请求开始日志
    # 使用结构化日志格式，包含请求的所有关键信息
    # extra字段中的结构化数据可以被日志系统解析和查询
    logger.info(
        f"请求开始: {method} {url}",
        extra={
            "type": "request_start",        # 日志类型标识
            "client_ip": client_ip,         # 客户端IP
            "method": method,               # HTTP方法
            "url": url,                     # 请求URL
            "user_agent": user_agent,       # 用户代理
            "timestamp": start_time         # 时间戳
        }
    )
    
    try:
        # 调用下一个中间件或路由处理函数
        # 这是中间件链的标准处理方式
        response = await call_next(request)
        
        # 计算请求处理耗时
        # 从开始时间到当前时间的时间差
        process_time = time.time() - start_time
        
        # 记录请求完成日志
        # 包含响应状态码和处理时间
        logger.info(
            f"请求完成: {method} {url} - {response.status_code}",
            extra={
                "type": "request_end",          # 日志类型标识
                "client_ip": client_ip,        # 客户端IP
                "method": method,              # HTTP方法
                "url": url,                    # 请求URL
                "status_code": response.status_code,  # HTTP状态码
                "process_time": f"{process_time:.3f}s",  # 处理时间（保留3位小数）
                "timestamp": time.time()      # 完成时间戳
            }
        )
        
        return response
        
    except Exception as e:
        # 即使发生异常，也要计算处理时间
        process_time = time.time() - start_time
        
        # 记录错误日志
        # 包含异常信息和处理时间
        # exc_info=True会记录完整的异常堆栈跟踪
        logger.error(
            f"请求错误: {method} {url} - {str(e)}",
            extra={
                "type": "request_error",         # 日志类型标识
                "client_ip": client_ip,           # 客户端IP
                "method": method,                # HTTP方法
                "url": url,                      # 请求URL
                "error": str(e),                 # 错误信息
                "process_time": f"{process_time:.3f}s",  # 处理时间
                "timestamp": time.time()        # 错误发生时间
            },
            exc_info=True  # 记录异常堆栈信息
        )
        # 重新抛出异常，让FastAPI的错误处理机制继续处理
        raise

# 注册API路由模块
# 必须在catch-all路由之前注册，确保API请求能被正确路由到对应的处理函数
# prefix="/api" 表示所有API请求的URL路径都以/api开头
app.include_router(api_router, prefix="/api")

# 挂载静态文件服务
# 将/app/static目录挂载到/static路径，用于提供CSS、JavaScript、图片等静态资源
# 这样前端就可以通过/static/路径访问这些静态文件
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 检查前端构建文件是否存在
# 这里是为了支持Vue.js等前端框架的生产环境构建
# 如果存在构建好的dist目录，说明前端已经构建完成
frontend_build_path = Path("app/static/dist")
frontend_exists = frontend_build_path.exists()

# Catch-all 路由处理器 - 实现路由优先级：API > 静态文件 > 404
@app.get("/{path:path}", response_class=HTMLResponse)
async def catch_all(request: Request, path: str):
    """
    智能路由处理器：
    1. API路由已经通过上面的 include_router 注册，会优先匹配
    2. 尝试服务静态文件
    3. 如果是根路径或前端路由，返回 index.html
    4. 否则返回 404
    """
    
    # 如果路径为空或是根路径，返回首页
    if path == "" or path == "/":
        if frontend_exists:
            # 生产模式：返回前端构建的 index.html
            index_file = frontend_build_path / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
            else:
                return HTMLResponse(content="index.html not found", status_code=500)
        else:
            # 开发模式：返回开发服务器页面
            return """
            <!DOCTYPE html>
            <html lang="zh-CN">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Python + Vue3 示例</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        margin: 40px;
                        background-color: #0f172a;
                        color: #e2e8f0;
                    }
                    .container {
                        max-width: 800px;
                        margin: 0 auto;
                        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
                        padding: 30px;
                        border-radius: 16px;
                        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
                        border: 1px solid rgba(255,255,255,0.1);
                    }
                    h1 {
                        color: #60a5fa;
                        text-align: center;
                        margin-bottom: 30px;
                        font-size: 2.5em;
                        text-shadow: 0 0 20px rgba(96,165,250,0.5);
                    }
                    .message {
                        margin-top: 30px;
                        padding: 25px;
                        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
                        border-radius: 12px;
                        text-align: center;
                        border: 1px solid rgba(96,165,250,0.3);
                    }
                    .dev-info {
                        margin: 30px 0;
                        padding: 20px;
                        background: rgba(59,130,246,0.1);
                        border-radius: 8px;
                        border-left: 4px solid #60a5fa;
                    }
                    .dev-link {
                        display: inline-block;
                        margin: 15px 10px;
                        padding: 12px 30px;
                        background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 8px;
                        font-weight: bold;
                        transition: all 0.3s ease;
                        box-shadow: 0 4px 15px rgba(96,165,250,0.4);
                    }
                    .dev-link:hover {
                        transform: translateY(-2px);
                        box-shadow: 0 6px 20px rgba(96,165,250,0.6);
                    }
                    .api-link {
                        display: inline-block;
                        margin: 10px;
                        padding: 10px 20px;
                        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        transition: all 0.3s ease;
                    }
                    .api-link:hover {
                        transform: translateY(-1px);
                        box-shadow: 0 4px 12px rgba(16,185,129,0.4);
                    }
                    code {
                        background: rgba(0,0,0,0.3);
                        padding: 2px 6px;
                        border-radius: 4px;
                        color: #a78bfa;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 Python + Vue3 + TypeScript</h1>
                    <div class="message">
                        <p style="font-size: 1.2em; margin-bottom: 15px;">✨ 欢迎使用开发服务器！</p>
                        <p>后端已使用 FastAPI 框架成功启动 🎯</p>
                    </div>
                    
                    <div class="dev-info">
                        <h3>📱 前端开发服务器</h3>
                        <p>前端正在开发模式下运行，请访问以下链接：</p>
                        <div style="text-align: center; margin-top: 20px;">
                            <a href="http://localhost:3005" class="dev-link" target="_blank">
                                打开前端应用 (端口 3005)
                            </a>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px;">
                        <h3 style="color: #94a3b8; margin-bottom: 20px;">API 测试链接</h3>
                        <a href="/api/hello" class="api-link">Hello API</a>
                        <a href="/api/data" class="api-link">数据 API</a>
                        <a href="/docs" class="api-link">API 文档</a>
                    </div>
                </div>
            </body>
            </html>
            """
    
    # 如果是静态文件请求且前端构建文件存在
    if frontend_exists:
        # 尝试在构建目录中查找文件
        requested_file = frontend_build_path / path
        
        # 如果请求的文件存在，直接返回
        if requested_file.exists() and requested_file.is_file():
            return FileResponse(requested_file)
        
        # 如果是前端路由（没有扩展名），返回 index.html
        # 这支持了 Vue Router 的 history 模式
        if "." not in path:
            index_file = frontend_build_path / "index.html"
            if index_file.exists():
                return FileResponse(index_file)
    
    # 如果没有找到匹配的资源，返回 404
    return HTMLResponse(
        content="""
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - 页面未找到</title>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    text-align: center; 
                    padding: 50px;
                    background-color: #0f172a;
                    color: #e2e8f0;
                }
                h1 { 
                    color: #ef4444; 
                    font-size: 3em;
                    margin-bottom: 20px;
                }
                p {
                    font-size: 1.2em;
                    margin-bottom: 30px;
                }
                .home-link {
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #60a5fa 0%, #3b82f6 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 8px;
                    font-weight: bold;
                    transition: all 0.3s ease;
                }
                .home-link:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(96,165,250,0.6);
                }
            </style>
        </head>
        <body>
            <h1>404</h1>
            <p>抱歉，您访问的页面不存在</p>
            <a href="/" class="home-link">返回首页</a>
        </body>
        </html>
        """,
        status_code=404
    )

# 应用启动入口
# 当该模块被直接运行时（而不是被导入），执行以下代码
# 这是 Python 标准的模块执行模式检测
if __name__ == "__main__":
    # 导入 uvicorn ASGI 服务器
    # uvicorn 是一个轻量级的 ASGI 服务器，专门用于运行 FastAPI 等异步框架
    import uvicorn
    
    # 记录应用启动日志
    # 使用结构化日志格式，记录应用启动的关键信息
    # 这些信息可以用于监控应用的生命周期和排查启动问题
    logger.info(
        "应用启动",  # 日志消息
        extra={
            "type": "app_start",         # 日志类型：应用启动
            "host": "0.0.0.0",           # 监听地址：0.0.0.0 表示监听所有网络接口
            "port": 14001,                # 监听端口
            "reload": True                # 是否启用热重载（开发模式）
        }
    )
    
    try:
        # 启动 uvicorn 服务器
        # uvicorn.run() 会启动一个异步服务器来运行 FastAPI 应用
        # 参数说明：
        # - app: FastAPI 应用实例
        # - host: 监听的主机地址，0.0.0.0 表示可以从任何 IP 访问
        # - port: 监听的端口号
        # - reload: 开启热重载功能，代码修改后自动重启服务器（仅用于开发环境）
        uvicorn.run(app, host="0.0.0.0", port=14001, reload=True)
        
    except Exception as e:
        # 捕获并记录启动过程中的异常
        # 即使应用启动失败，也要记录详细的错误信息以便排查问题
        # exc_info=True 会记录完整的异常堆栈跟踪
        logger.error(
            "应用启动失败",  # 日志消息
            extra={
                "type": "app_start_error",  # 日志类型：应用启动失败
                "error": str(e)             # 错误信息
            },
            exc_info=True  # 记录异常堆栈信息
        )
        # 重新抛出异常，让调用者能够处理这个错误
        raise