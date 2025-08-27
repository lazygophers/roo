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
    try:
        # 尝试读取构建好的前端文件
        with open("app/static/dist/index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        # 如果找不到构建文件，返回默认页面
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
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1 {
                    color: #333;
                    text-align: center;
                }
                .message {
                    margin-top: 30px;
                    padding: 20px;
                    background-color: #e3f2fd;
                    border-radius: 4px;
                    text-align: center;
                }
                .api-link {
                    display: inline-block;
                    margin: 10px;
                    padding: 10px 20px;
                    background-color: #2196F3;
                    color: white;
                    text-decoration: none;
                    border-radius: 4px;
                }
                .api-link:hover {
                    background-color: #1976D2;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Python + Vue3 + TypeScript 示例服务</h1>
                <div class="message">
                    <p>欢迎使用示例服务！</p>
                    <p>后端已使用 FastAPI 框架成功启动</p>
                    <p>前端需要先构建: <code>cd app/frontend && npm run build</code></p>
                </div>
                <div style="text-align: center; margin-top: 30px;">
                    <a href="/api/hello" class="api-link">访问 Hello API</a>
                    <a href="/api/data" class="api-link">访问数据 API</a>
                    <a href="/docs" class="api-link">查看 API 文档</a>
                </div>
            </div>
        </body>
        </html>
        """

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)