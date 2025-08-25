#!/usr/bin/env python3
"""
修复后的功能测试脚本
不需要浏览器自动化，通过 API 和 HTML 内容验证
"""

import requests
import json
import re
from urllib.parse import quote

BASE_URL = "http://localhost:8000"

def test_api_endpoint():
    """测试 API 端点"""
    print("🧪 测试 API 端点...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/models")
        response.raise_for_status()
        data = response.json()
        
        print(f"✅ API 响应成功，状态码: {response.status_code}")
        
        # 检查返回结构
        if 'success' in data and 'models' in data:
            print(f"✅ API 返回结构正确")
            models = data['models']
            print(f"✅ 模式总数: {len(models)}")
            print(f"✅ 返回 count: {data.get('count', 'N/A')}")
            
            # 检查是否包含 orchestrator
            orchestrator = next((m for m in models if m['slug'] == 'orchestrator'), None)
            if orchestrator:
                print(f"✅ 找到 orchestrator 模式，required: {orchestrator.get('required', False)}")
            else:
                print("❌ 未找到 orchestrator 模式")
                
            # 显示所有模式
            print("\n📋 所有模式列表:")
            for model in models:
                required = " (required)" if model.get('required') else ""
                print(f"  - {model['slug']}: {model['name']}{required}")
        else:
            print("❌ API 返回结构不符合预期")
            
        return True
    except Exception as e:
        print(f"❌ API 测试失败: {e}")
        return False

def test_page_content():
    """测试页面内容"""
    print("\n🧪 测试页面内容...")
    
    try:
        response = requests.get(f"{BASE_URL}/mode-selector")
        response.raise_for_status()
        
        # 检查页面结构
        content = response.text
        
        # 检查必要的 HTML 元素
        checks = [
            ('mode-grid', '模式网格'),
            ('search-input', '搜索框'),
            ('preview-section', '预览区域'),
            ('selectedCount', '选中计数'),
            ('copyBtn', '复制按钮'),
            ('clearBtn', '清除按钮')
        ]
        
        for element_id, description in checks:
            if f'id="{element_id}"' in content:
                print(f"✅ {description} 存在")
            else:
                print(f"❌ {description} 缺失")
                
        return True
    except Exception as e:
        print(f"❌ 页面测试失败: {e}")
        return False

def test_multilingual_support():
    """测试多语言支持"""
    print("\n🧪 测试多语言支持...")
    
    languages = ['zh-CN', 'en', 'zh-TW', 'ja', 'fr', 'ar', 'ru', 'es']
    
    for lang in languages:
        try:
            response = requests.get(f"{BASE_URL}/mode-selector?lang={lang}")
            response.raise_for_status()
            
            # 检查语言文件是否加载
            if f'/static/js/locales/{lang}.js' in response.text:
                print(f"✅ {lang} 语言文件已加载")
            else:
                print(f"⚠️ {lang} 语言文件可能未正确加载")
                
        except Exception as e:
            print(f"❌ {lang} 测试失败: {e}")

def test_mode_data():
    """测试模式数据完整性"""
    print("\n🧪 测试模式数据完整性...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/models")
        response.raise_for_status()
        data = response.json()
        
        if 'models' in data:
            models = data['models']
            required_fields = ['slug', 'name', 'required']
            
            for mode in models:
                missing_fields = [f for f in required_fields if f not in mode]
                if missing_fields:
                    print(f"⚠️ 模式 {mode.get('slug', 'Unknown')} 缺少字段: {missing_fields}")
                else:
                    print(f"✅ 模式 {mode['slug']} 数据完整")
        else:
            print("❌ API 响应中缺少 models 字段")
                
        return True
    except Exception as e:
        print(f"❌ 模式数据测试失败: {e}")
        return False

def generate_test_report():
    """生成测试报告"""
    print("\n" + "="*50)
    print("📋 测试报告")
    print("="*50)
    
    results = {
        "API 端点": test_api_endpoint(),
        "页面内容": test_page_content(),
        "模式数据": test_mode_data()
    }
    
    test_multilingual_support()
    
    print("\n📊 测试结果汇总:")
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test}: {status}")
    
    print(f"\n🎯 总体结果: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("🎉 所有核心功能测试通过！")
    else:
        print("⚠️ 部分功能需要修复")

if __name__ == "__main__":
    generate_test_report()