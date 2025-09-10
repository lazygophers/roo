#!/usr/bin/env python3
"""
LazyAI Studio 前后端集成测试脚本
测试后端是否能正确提供前端静态文件
"""

import requests
import time
from pathlib import Path

def test_integration():
    """测试前后端集成"""
    print("🚀 LazyAI Studio 前后端集成测试")
    print("=" * 50)
    
    # 检查前端构建文件是否存在
    build_dir = Path("frontend/build")
    index_file = build_dir / "index.html"
    
    print("📁 检查前端构建文件...")
    if not build_dir.exists():
        print("❌ 前端构建目录不存在，请运行: make frontend-build")
        return False
    
    if not index_file.exists():
        print("❌ index.html 不存在，请运行: make frontend-build")
        return False
    
    print("✅ 前端构建文件存在")
    
    # 测试后端静态文件服务
    print("\n🌐 测试后端静态文件服务...")
    
    try:
        # 测试根路径
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✅ 根路径访问成功 (200)")
            # 检查是否返回 HTML
            if "<!doctype html>" in response.text.lower() or "<html" in response.text.lower():
                print("✅ 成功返回 HTML 内容")
            else:
                print("⚠️  返回内容不是 HTML")
        else:
            print(f"❌ 根路径访问失败 ({response.status_code})")
            return False
            
        # 测试API路径
        api_response = requests.get("http://localhost:8000/api/health", timeout=5)
        if api_response.status_code == 200:
            print("✅ API 端点访问成功 (200)")
        else:
            print(f"⚠️  API 端点访问异常 ({api_response.status_code})")
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行:")
        print("   make backend-dev")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        return False
    
    print("\n🎉 集成测试完成！")
    print("\n📋 使用说明:")
    print("  1. 前端开发: make frontend-dev")
    print("  2. 后端开发: make backend-dev")
    print("  3. 完整构建: make build")
    print("  4. 生产部署: make deploy")
    print("\n🌐 访问地址:")
    print("  - 前端应用: http://localhost:8000/")
    print("  - API文档: http://localhost:8000/docs")
    print("  - 健康检查: http://localhost:8000/api/health")
    
    return True

if __name__ == "__main__":
    test_integration()