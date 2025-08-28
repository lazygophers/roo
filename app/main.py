from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.api.routes import router as api_router

app = FastAPI(
    title="Python + Vue3 示例服务",
    description="一个使用 FastAPI + Vue3 + TypeScript 的示例应用",
    version="0.1.0"
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# 注册API路由
app.include_router(api_router, prefix="/api")

# 创建一个简单的API端点
@app.get("/api/hello")
async def hello(message: str | None = Query(default=None)):
    if message:
        return {"message": f"收到你的消息: {message}", "status": "success"}
    return {"message": "Hello from FastAPI!", "status": "success"}

@app.get("/api/data")
async def get_data():
    return {
        "items": [
            {"id": 1, "name": "项目1", "description": "这是第一个项目"},
            {"id": 2, "name": "项目2", "description": "这是第二个项目"},
            {"id": 3, "name": "项目3", "description": "这是第三个项目"}
        ]
    }

# 添加路由来服务前端页面
@app.get("/", response_class=HTMLResponse)
async def read_root():
    # 开发模式下重定向到前端开发服务器
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)