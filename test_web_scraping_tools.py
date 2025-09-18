#!/usr/bin/env python3
"""
网络抓取工具测试脚本
测试工具集功能和MCP配置集成
"""

import asyncio
import json
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.fetch_tools import (
    get_fetch_tools,
    http_request,
    fetch_webpage,
    api_call
)
from app.core.mcp_tools_service import init_mcp_config_service


async def test_basic_http_request():
    """测试基本HTTP请求功能"""
    print("🌐 测试基本HTTP请求...")

    try:
        result = await http_request("https://httpbin.org/get")
        if result["success"]:
            print(f"✅ HTTP请求成功: {result['status_code']}")
            print(f"   URL: {result['url']}")
            print(f"   用户代理: {result.get('content', {}).get('headers', {}).get('User-Agent', 'N/A')}")
        else:
            print(f"❌ HTTP请求失败: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ HTTP请求异常: {e}")


async def test_webpage_fetch():
    """测试网页抓取功能"""
    print("\n📄 测试网页抓取...")

    try:
        result = await fetch_webpage(
            "https://httpbin.org/html",
            extract_text=True,
            extract_links=False
        )
        if result["success"]:
            print(f"✅ 网页抓取成功: {result['status_code']}")
            print(f"   标题: {result.get('title', 'N/A')}")
            print(f"   内容长度: {len(result.get('text', ''))}")
        else:
            print(f"❌ 网页抓取失败: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ 网页抓取异常: {e}")


async def test_api_call():
    """测试API调用功能"""
    print("\n🔌 测试API调用...")

    try:
        result = await api_call("https://httpbin.org/json")
        if result["success"]:
            print(f"✅ API调用成功: {result['status_code']}")
            content = result.get('content', {})
            if isinstance(content, dict) and 'slideshow' in content:
                print(f"   JSON数据: {content['slideshow']['title']}")
        else:
            print(f"❌ API调用失败: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ API调用异常: {e}")


async def test_config_integration():
    """测试配置集成"""
    print("\n⚙️  测试配置集成...")

    try:
        # 初始化MCP配置服务
        config_service = init_mcp_config_service()
        print("✅ MCP配置服务初始化成功")

        # 获取网络抓取工具实例
        tools = get_fetch_tools()
        print(f"✅ 网络抓取工具实例获取成功")

        # 检查配置加载
        print(f"   工具状态: {'启用' if tools.config.enabled else '禁用'}")
        print(f"   用户代理: {tools.config.user_agent}")
        print(f"   超时时间: {tools.config.timeout}秒")
        print(f"   最大重试: {tools.config.max_retries}次")

        # 检查MCP全局配置
        if tools.mcp_config:
            print(f"   MCP配置加载: ✅")
            print(f"   代理启用: {'是' if tools.mcp_config.proxy.enabled else '否'}")
            print(f"   SSL验证: {'是' if tools.mcp_config.security.verify_ssl else '否'}")
        else:
            print(f"   MCP配置加载: ❌")

    except Exception as e:
        print(f"❌ 配置集成测试异常: {e}")


async def test_proxy_configuration():
    """测试代理配置"""
    print("\n🔒 测试代理配置...")

    try:
        tools = get_web_scraping_tools()
        proxy_url = tools._get_proxy_url()

        if proxy_url:
            print(f"✅ 代理配置已加载: {proxy_url}")
        else:
            print("ℹ️  未配置代理或代理未启用")

        # 测试带代理的请求（如果有代理）
        if proxy_url:
            print("   测试代理请求...")
            result = await http_request("https://httpbin.org/ip")
            if result["success"]:
                ip_info = result.get('content', {})
                print(f"   外部IP: {ip_info.get('origin', 'N/A')}")

    except Exception as e:
        print(f"❌ 代理配置测试异常: {e}")


async def test_error_handling():
    """测试错误处理"""
    print("\n❗ 测试错误处理...")

    try:
        # 测试无效URL
        result = await http_request("https://invalid-domain-that-does-not-exist-12345.com")
        if not result["success"]:
            print("✅ 无效域名错误处理正确")
        else:
            print("⚠️  无效域名请求意外成功")

        # 测试超时（使用一个很慢的服务）
        print("   测试请求超时...")
        result = await http_request("https://httpbin.org/delay/10")  # 10秒延迟
        if not result["success"]:
            print("✅ 超时错误处理正确")
        else:
            print("⚠️  超时请求意外成功")

    except Exception as e:
        print(f"❌ 错误处理测试异常: {e}")


async def main():
    """主测试函数"""
    print("🚀 开始网络抓取工具测试\n")

    await test_config_integration()
    await test_proxy_configuration()
    await test_basic_http_request()
    await test_webpage_fetch()
    await test_api_call()
    await test_error_handling()

    print("\n✨ 网络抓取工具测试完成")


if __name__ == "__main__":
    asyncio.run(main())