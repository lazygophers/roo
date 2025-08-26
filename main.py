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
import logging
from pathlib import Path
from typing import List, Dict, Any
from fastapi import FastAPI, Request, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
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
    
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # 动态扫描 static/locales 目录获取所有语言文件
    def scan_available_languages() -> List[str]:
        """扫描 static/locales 目录，返回所有可用的语言代码"""
        locales_dir = Path("static/locales")
        if not locales_dir.exists():
            logger.warning("static/locales 目录不存在")
            return ["zh-CN"]  # 默认语言
        
        language_files = []
        try:
            for file_path in locales_dir.glob("*.json"):
                # 从文件名提取语言代码（去除 .json 扩展名）
                lang_code = file_path.stem
                language_files.append(lang_code)
            logger.info(f"发现语言文件: {language_files}")
        except Exception as e:
            logger.error(f"扫描语言文件时出错: {e}")
            return ["zh-CN"]  # 出错时返回默认语言
        
        return sorted(language_files)
    
    # 加载多语言文件
    def load_translations(lang: str) -> Dict[str, Any]:
        """加载指定语言的翻译文件"""
        try:
            file_path = Path(f"static/locales/{lang}.json")
            if not file_path.exists():
                logger.warning(f"语言文件不存在: {file_path}")
                # 如果找不到请求的语言文件，默认使用中文
                file_path = Path("static/locales/zh-CN.json")
                if not file_path.exists():
                    logger.error("默认中文语言文件也不存在")
                    return {}
            
            with open(file_path, "r", encoding="utf-8") as f:
                translations = json.load(f)
                logger.info(f"成功加载语言文件: {lang}")
                return translations
        except json.JSONDecodeError as e:
            logger.error(f"解析语言文件 {lang} 时出错: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载语言文件 {lang} 时出错: {e}")
            return {}
    
    # 全局翻译字典
    translations = {}
    
    # 在应用启动时预加载所有语言文件
    @app.on_event("startup")
    async def startup_event():
        nonlocal translations
        # 动态扫描获取所有可用语言
        available_languages = scan_available_languages()
        
        if not available_languages:
            logger.error("没有找到任何语言文件")
            available_languages = ["zh-CN"]  # 默认语言
        
        # 预加载所有语言文件
        for lang in available_languages:
            translations[lang] = load_translations(lang)
        
        # 将翻译和可用语言列表存储到 app.state 中
        app.state.translations = translations
        app.state.available_languages = available_languages
        logger.info(f"应用启动完成，已加载 {len(available_languages)} 种语言")
    
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
    
    @app.get("/api/languages")
    async def get_languages(request: Request):
        """获取所有可用语言的 API 端点"""
        try:
            # 如果 app.state 中没有可用语言列表，重新扫描
            if not hasattr(app.state, 'available_languages'):
                available_languages = scan_available_languages()
                app.state.available_languages = available_languages
            else:
                available_languages = app.state.available_languages
            
            # 获取每个语言的名称（从翻译文件中读取）
            languages_info = []
            for lang in available_languages:
                # 尝试从翻译文件中获取语言名称
                if lang in translations and translations[lang]:
                    # 优先从language_switcher部分获取语言名称
                    if "language_switcher" in translations[lang]:
                        # 根据语言代码映射到对应的语言名称
                        lang_map = {
                            "zh-CN": "chinese",
                            "en": "english",
                            "en-US": "english",
                            "ja": "japanese",
                            "fr": "french",
                            "ar": "arabic",
                            "ru": "russian",
                            "es": "spanish",
                            "zh-TW": "traditional_chinese"
                        }
                        lang_key = lang_map.get(lang, lang)
                        lang_name = translations[lang]["language_switcher"].get(lang_key, lang)
                    else:
                        # 如果没有language_switcher字段，使用语言代码
                        lang_name = lang
                else:
                    lang_name = lang
                
                languages_info.append({
                    "code": lang,
                    "name": lang_name
                })
            
            return JSONResponse(
                content={
                    "success": True,
                    "languages": languages_info,
                    "count": len(languages_info)
                }
            )
        except Exception as e:
            logger.error(f"获取语言列表时出错: {e}")
            raise HTTPException(status_code=500, detail="获取语言列表失败")
    
    @app.get("/api/switch-language")
    async def switch_language(lang: str, request: Request):
        """切换语言的 API 端点"""
        # 检查语言是否在可用列表中
        if not hasattr(app.state, 'available_languages'):
            available_languages = scan_available_languages()
            app.state.available_languages = available_languages
        else:
            available_languages = app.state.available_languages
        
        if lang not in available_languages:
            return {"error": f"Language '{lang}' is not supported"}
        
        return {
            "success": True,
            "language": lang,
            "translations": translations.get(lang, {})
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
        models_dir = Path("resources/models")
        
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
    
    @app.get("/api/modes/{mode_slug}")
    async def get_mode(mode_slug: str):
        """获取特定模式的详细信息"""
        try:
            models = get_all_models()
            mode = None
            for m in models:
                if m["slug"] == mode_slug:
                    mode = m
                    break
            
            if not mode:
                raise HTTPException(status_code=404, detail="Mode not found")
            
            return {"success": True, "data": mode}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.patch("/api/modes/{mode_slug}")
    async def update_mode(mode_slug: str, update_data: dict = Body(...)):
        """更新模式信息"""
        try:
            # 查找指定模式
            models = get_all_models()
            mode_index = -1
            for i, m in enumerate(models):
                if m["slug"] == mode_slug:
                    mode_index = i
                    break
            
            if mode_index == -1:
                raise HTTPException(status_code=404, detail="Mode not found")
            
            # 更新允许的字段
            allowed_fields = ["roleDefinition", "description", "whenToUse"]
            for field, value in update_data.items():
                if field in allowed_fields:
                    models[mode_index][field] = value
            
            return {"success": True, "data": models[mode_index]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/modes/{mode_slug}/permissions")
    async def add_permission(mode_slug: str, request: dict = Body(...)):
        """为模式添加权限"""
        try:
            # 查找指定模式
            models = get_all_models()
            mode_index = -1
            for i, m in enumerate(models):
                if m["slug"] == mode_slug:
                    mode_index = i
                    break
            
            if mode_index == -1:
                raise HTTPException(status_code=404, detail="Mode not found")
            
            # 添加新权限
            permission = request.get("permission", "")
            if permission and permission not in models[mode_index].get("groups", []):
                if "groups" not in models[mode_index]:
                    models[mode_index]["groups"] = []
                models[mode_index]["groups"].append(permission)
            
            return {"success": True, "data": models[mode_index]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.put("/api/modes/{mode_slug}/permissions")
    async def edit_permission(mode_slug: str, request: dict = Body(...)):
        """编辑模式的权限"""
        try:
            # 查找指定模式
            models = get_all_models()
            mode_index = -1
            for i, m in enumerate(models):
                if m["slug"] == mode_slug:
                    mode_index = i
                    break
            
            if mode_index == -1:
                raise HTTPException(status_code=404, detail="Mode not found")
            
            # 编辑权限
            old_permission = request.get("old_permission", "")
            new_permission = request.get("new_permission", "")
            
            if old_permission and new_permission and old_permission != new_permission:
                groups = models[mode_index].get("groups", [])
                if old_permission in groups:
                    index = groups.index(old_permission)
                    groups[index] = new_permission
            
            return {"success": True, "data": models[mode_index]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.delete("/api/modes/{mode_slug}/permissions")
    async def remove_permission(mode_slug: str, request: dict = Body(...)):
        """移除模式的权限"""
        try:
            # 查找指定模式
            models = get_all_models()
            mode_index = -1
            for i, m in enumerate(models):
                if m["slug"] == mode_slug:
                    mode_index = i
                    break
            
            if mode_index == -1:
                raise HTTPException(status_code=404, detail="Mode not found")
            
            # 移除权限
            permission = request.get("permission", "")
            if permission:
                groups = models[mode_index].get("groups", [])
                if permission in groups:
                    groups.remove(permission)
            
            return {"success": True, "data": models[mode_index]}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
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