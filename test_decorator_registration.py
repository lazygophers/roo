#!/usr/bin/env python3
"""
测试网络抓取工具装饰器注册功能
验证装饰器注册系统和工具发现功能
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.registry import (
    get_registered_tools,
    get_tools_by_category,
    get_registry_stats,
    auto_discover_tools
)


def test_decorator_registration():
    """测试装饰器注册功能"""
    print("🔧 测试装饰器注册功能...")

    # 导入网络抓取工具以触发装饰器注册
    try:
        from app.tools.fetch_tools import (
            http_request,
            fetch_webpage,
            download_file,
            api_call,
            batch_requests
        )
        print("✅ 网络抓取工具模块导入成功")
    except ImportError as e:
        print(f"❌ 网络抓取工具模块导入失败: {e}")
        return False

    # 检查注册表状态
    stats = get_registry_stats()
    print(f"   注册表统计:")
    print(f"   - 总工具数: {stats['total_tools']}")
    print(f"   - 分类数: {stats['categories']}")
    print(f"   - 分类详情: {stats['tools_by_category']}")

    # 检查fetch分类的工具
    fetch_tools = get_tools_by_category("fetch")
    print(f"\n📦 fetch分类工具:")

    expected_tools = [
        "fetch_http_request",
        "fetch_fetch_webpage",
        "fetch_download_file",
        "fetch_api_call",
        "fetch_batch_requests"
    ]

    found_tools = [tool.name for tool in fetch_tools]
    print(f"   已注册工具: {found_tools}")

    # 验证所有期望的工具都已注册
    missing_tools = set(expected_tools) - set(found_tools)
    if missing_tools:
        print(f"❌ 缺失工具: {missing_tools}")
        return False

    extra_tools = set(found_tools) - set(expected_tools)
    if extra_tools:
        print(f"⚠️  额外工具: {extra_tools}")

    # 检查工具详细信息
    print(f"\n🔍 工具详细信息:")
    for tool in fetch_tools:
        print(f"   {tool.name}:")
        print(f"     - 描述: {tool.description}")
        print(f"     - 分类: {tool.category}")
        print(f"     - 启用: {tool.enabled}")
        print(f"     - 必需参数: {tool.schema.get('required', [])}")
        print(f"     - 标签: {tool.metadata.get('tags', [])}")

    print("✅ 装饰器注册功能测试通过")
    return True


def test_auto_discovery():
    """测试自动发现功能"""
    print("\n🔎 测试自动发现功能...")

    try:
        # 发现项目中的工具
        discovered_count = auto_discover_tools([
            "/Users/luoxin/persons/knowledge/roo/app/tools/fetch_tools.py"
        ])

        print(f"✅ 自动发现了 {discovered_count} 个工具")

        # 再次检查注册表
        stats = get_registry_stats()
        print(f"   发现后注册表统计:")
        print(f"   - 总工具数: {stats['total_tools']}")
        print(f"   - 已注册工具: {stats['registered_tools']}")

        return True

    except Exception as e:
        print(f"❌ 自动发现功能测试失败: {e}")
        return False


def test_schema_validation():
    """测试Schema验证"""
    print("\n📋 测试Schema验证...")

    try:
        fetch_tools = get_tools_by_category("fetch")

        for tool in fetch_tools:
            # 检查schema基本结构
            schema = tool.schema
            if not isinstance(schema, dict):
                print(f"❌ {tool.name} schema不是字典类型")
                return False

            if "type" not in schema:
                print(f"❌ {tool.name} schema缺少type字段")
                return False

            if "properties" not in schema:
                print(f"❌ {tool.name} schema缺少properties字段")
                return False

            # 检查返回值schema
            if tool.returns:
                returns = tool.returns
                if not isinstance(returns, dict):
                    print(f"❌ {tool.name} returns不是字典类型")
                    return False

        print("✅ Schema验证测试通过")
        return True

    except Exception as e:
        print(f"❌ Schema验证测试失败: {e}")
        return False


async def test_function_calls():
    """测试函数调用是否正常"""
    print("\n🚀 测试装饰器函数调用...")

    try:
        from app.tools.fetch_tools import http_request

        # 测试一个简单的HTTP请求
        result = await http_request("https://httpbin.org/get")

        if result.get("success"):
            print("✅ 装饰器函数调用正常")
            print(f"   响应状态码: {result.get('status_code')}")
            return True
        else:
            print("❌ 装饰器函数调用失败")
            print(f"   错误信息: {result.get('error')}")
            return False

    except Exception as e:
        print(f"❌ 装饰器函数调用异常: {e}")
        return False


async def main():
    """主测试函数"""
    print("🧪 开始网络抓取工具装饰器注册测试\n")

    tests = [
        ("装饰器注册", test_decorator_registration),
        ("自动发现", test_auto_discovery),
        ("Schema验证", test_schema_validation),
        ("函数调用", test_function_calls)
    ]

    results = []

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))

    # 总结测试结果
    print("\n📊 测试结果总结:")
    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n总计: {passed}/{len(results)} 个测试通过")

    if passed == len(results):
        print("🎉 所有装饰器注册测试通过！")
    else:
        print("⚠️  部分测试失败，请检查相关功能")


if __name__ == "__main__":
    asyncio.run(main())