#!/usr/bin/env python3
"""
FastAPI Web 应用
支持命令行参数指定端口和热重载功能
"""

import argparse
import uvicorn
import json
import os
import yaml
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware


def create_app() -> FastAPI:
    """创建并配置 FastAPI 应用实例"""
    
    app = FastAPI(
        title="FastAPI Web 应用",
        description="支持端口参数和热重载的 Web 应用",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # 添加 CORS 中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 挂载静态文件目录
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # 配置 Jinja2 模板
    templates = Jinja2Templates(directory="templates")
    
    # 全局翻译字典
    translations = {}
    
    # 加载多语言文件
    def load_translations(lang: str):
        try:
            with open(f"locales/{lang}.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果找不到请求的语言文件，默认使用中文
            with open("locales/zh-CN.json", "r", encoding="utf-8") as f:
                return json.load(f)
    
    # 在应用启动时预加载所有语言文件
    @app.on_event("startup")
    async def startup_event():
        nonlocal translations
        # 支持的语言列表
        supported_languages = ["zh-CN", "en", "zh-TW", "ja", "fr", "ar", "ru", "es"]
        for lang in supported_languages:
            translations[lang] = load_translations(lang)
    
    @app.get("/", response_class=HTMLResponse)
    async def read_root(request: Request):
        """根路由 - 返回首页"""
        # 从查询参数或 cookie 中获取语言设置
        lang = request.query_params.get("lang", "zh-CN")
        if lang not in translations:
            lang = "zh-CN"
        
        # 获取翻译文本
        texts = translations.get(lang, translations["zh-CN"])
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "texts": texts,
                "current_lang": lang
            }
        )
    
    @app.get("/api/switch-language")
    async def switch_language(lang: str, request: Request):
        """切换语言的 API 端点"""
        if lang not in translations:
            return {"error": "Language not supported"}
        
        return {
            "success": True,
            "language": lang,
            "translations": translations[lang]
        }
    
    @app.get("/api/hello")
    async def hello_api():
        """示例 API 端点"""
        return {"message": "Hello, FastAPI!", "status": "success"}
    
    @app.get("/health")
    async def health_check():
        """健康检查端点"""
        return {"status": "healthy", "message": "服务正常运行"}
    
    def get_all_models():
        """获取所有可用模式"""
        models = []
        models_dir = Path("custom_models")
        
        # 递归遍历所有 YAML 文件
        for yaml_file in models_dir.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    if data and 'slug' in data and 'name' in data:
                        model_info = {
                            'slug': data['slug'],
                            'name': data['name'],
                            'roleDefinition': data.get('roleDefinition', ''),
                            'whenToUse': data.get('whenToUse', ''),
                            'description': data.get('description', ''),
                            'groups': data.get('groups', []),
                            'customInstructions': data.get('customInstructions', ''),
                            'source': data.get('source', ''),
                            'required': data['slug'] == 'orchestrator'
                        }
                        models.append(model_info)
            except Exception as e:
                print(f"Error loading model from {yaml_file}: {e}")
                continue
        
        # 按 slug 排序
        models.sort(key=lambda x: x['slug'])
        return models
    
    @app.get("/api/models")
    async def get_models():
        """获取所有可用模式的 API 端点"""
        models = get_all_models()
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
    
    @app.get("/mode-selector", response_class=HTMLResponse)
    async def mode_selector_page(request: Request, lang: str = "zh-CN"):
        """模式选择器页面"""
        try:
            # 从应用状态中获取翻译文本
            if not hasattr(app.state, 'translations'):
                # 如果翻译未加载，重新加载
                await startup_event()
            
            texts = app.state.translations.get(lang, app.state.translations["zh-CN"])
            return templates.TemplateResponse("mode_selector.html", {"request": request, "texts": texts, "current_lang": lang})
        except Exception as e:
            # 如果出错，使用默认的英文翻译
            default_texts = {
                "title": "AI Mode Selector",
                "select_modes": "Select AI Modes",
                "selected": "Selected",
                "required": "Required",
                "optional": "Optional",
                "copy_yaml": "Copy YAML",
                "copied": "Copied!",
                "clear_all": "Clear All",
                "search_placeholder": "Search modes...",
                "preview": "YAML Preview",
                "no_modes_selected": "No modes selected",
                "orchestrator_required": "Orchestrator mode is required"
            }
            return templates.TemplateResponse("mode_selector.html", {"request": request, "texts": default_texts, "current_lang": "en"})
    
    return app


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="FastAPI Web 应用")
    parser.add_argument(
        "--port", 
        type=int, 
        default=8080,
        help="指定端口号 (默认: 8080)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="127.0.0.1",
        help="指定主机地址 (默认: 127.0.0.1)"
    )
    parser.add_argument(
        "--reload", 
        action="store_true",
        help="启用热重载（开发模式）"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="启用调试模式"
    )
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    # 创建应用实例
    app = create_app()
    
    # 打印启动信息
    print(f"🚀 启动 FastAPI 应用...")
    print(f"📍 地址: http://{args.host}:{args.port}")
    print(f"📚 API 文档: http://{args.host}:{args.port}/docs")
    print(f"🔄 热重载: {'已启用' if args.reload else '已禁用'}")
    print(f"🐛 调试模式: {'已启用' if args.debug else '已禁用'}")
    print("-" * 50)
    
    # 启动服务器
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug else "info"
    )


if __name__ == "__main__":
    main()

# 创建全局 app 变量以支持 uvicorn 的直接导入
app = create_app()