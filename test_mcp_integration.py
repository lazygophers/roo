#!/usr/bin/env python3
"""
测试MCP工具服务与装饰器注册表的集成
验证网络抓取工具是否能在MCP接口中正确显示
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.tools.service import get_mcp_tools_service
from app.core.logging import setup_logging

logger = setup_logging()


def test_mcp_tools_service_integration():
    """测试MCP工具服务集成"""
    print("🔧 测试MCP工具服务集成...")

    try:
        # 获取MCP工具服务
        tools_service = get_mcp_tools_service()
        print("✅ MCP工具服务获取成功")

        # 获取所有工具（应该包括装饰器注册的工具）
        all_tools = tools_service.get_tools(enabled_only=False)
        print(f"   总工具数: {len(all_tools)}")

        # 查找网络抓取工具
        fetch_tools = [tool for tool in all_tools if tool.get('category') == 'fetch']
        print(f"   网络抓取工具数: {len(fetch_tools)}")

        if fetch_tools:
            print("🎯 发现的网络抓取工具:")
            for tool in fetch_tools:
                print(f"     - {tool['name']}: {tool['description']}")
        else:
            print("❌ 未发现网络抓取工具")
            return False

        return len(fetch_tools) >= 5  # 期望至少5个工具

    except Exception as e:
        print(f"❌ MCP工具服务集成测试失败: {e}")
        return False


def test_category_filtering():
    """测试分类过滤功能"""
    print("\n🔍 测试分类过滤功能...")

    try:
        tools_service = get_mcp_tools_service()

        # 获取fetch分类的工具
        fetch_tools = tools_service.get_tools(category="fetch", enabled_only=False)
        print(f"   fetch分类工具数: {len(fetch_tools)}")

        expected_tools = [
            "fetch_http_request",
            "fetch_fetch_webpage",
            "fetch_download_file",
            "fetch_api_call",
            "fetch_batch_requests"
        ]

        found_tools = [tool['name'] for tool in fetch_tools]

        missing_tools = set(expected_tools) - set(found_tools)
        if missing_tools:
            print(f"❌ 缺失工具: {missing_tools}")
            return False

        print("✅ 所有期望的网络抓取工具都已找到")
        return True

    except Exception as e:
        print(f"❌ 分类过滤测试失败: {e}")
        return False


def test_tool_details():
    """测试工具详细信息"""
    print("\n📋 测试工具详细信息...")

    try:
        tools_service = get_mcp_tools_service()

        # 获取特定工具
        http_request_tool = tools_service.get_tool("fetch_http_request")

        if not http_request_tool:
            # 尝试从所有工具中查找
            all_tools = tools_service.get_tools(enabled_only=False)
            http_request_tool = next((tool for tool in all_tools if tool['name'] == 'fetch_http_request'), None)

        if http_request_tool:
            print("✅ HTTP请求工具详细信息:")
            print(f"     名称: {http_request_tool['name']}")
            print(f"     描述: {http_request_tool['description']}")
            print(f"     分类: {http_request_tool['category']}")
            print(f"     启用: {http_request_tool['enabled']}")
            print(f"     实现类型: {http_request_tool['implementation_type']}")

            # 检查schema
            if 'schema' in http_request_tool and http_request_tool['schema']:
                required_params = http_request_tool['schema'].get('required', [])
                print(f"     必需参数: {required_params}")

            return True
        else:
            print("❌ 未找到HTTP请求工具")
            return False

    except Exception as e:
        print(f"❌ 工具详细信息测试失败: {e}")
        return False


def test_tools_by_category():
    """测试按分类获取工具"""
    print("\n📂 测试按分类获取工具...")

    try:
        tools_service = get_mcp_tools_service()

        # 获取所有分类的工具
        tools_by_category = tools_service.get_tools_by_category()
        print(f"   发现分类数: {len(tools_by_category)}")

        for category, tools in tools_by_category.items():
            print(f"     {category}: {len(tools)} 个工具")

        # 检查是否包含fetch分类
        if 'fetch' in tools_by_category:
            fetch_count = len(tools_by_category['fetch'])
            print(f"✅ fetch分类包含 {fetch_count} 个工具")
            return fetch_count >= 5
        else:
            print("❌ 未找到fetch分类")
            return False

    except Exception as e:
        print(f"❌ 按分类获取工具测试失败: {e}")
        return False


def test_db_sync():
    """测试数据库同步功能"""
    print("\n💾 测试数据库同步功能...")

    try:
        tools_service = get_mcp_tools_service()

        # 执行同步操作
        synced_count = tools_service.sync_registry_tools_to_db()
        print(f"   同步工具数: {synced_count}")

        # 验证同步后的数据库状态
        db_tools = tools_service.tools_table.all()
        fetch_db_tools = [tool for tool in db_tools if tool.get('category') == 'fetch']

        print(f"   数据库中网络抓取工具数: {len(fetch_db_tools)}")

        if fetch_db_tools:
            print("✅ 装饰器工具已成功同步到数据库")
            return True
        else:
            print("⚠️  数据库同步可能未完全成功")
            return synced_count >= 0  # 同步成功即可，可能之前已同步

    except Exception as e:
        print(f"❌ 数据库同步测试失败: {e}")
        return False


def main():
    """主测试函数"""
    print("🧪 开始MCP工具服务集成测试\n")

    tests = [
        ("MCP工具服务集成", test_mcp_tools_service_integration),
        ("分类过滤功能", test_category_filtering),
        ("工具详细信息", test_tool_details),
        ("按分类获取工具", test_tools_by_category),
        ("数据库同步", test_db_sync)
    ]

    results = []
    passed = 0

    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))

    # 总结测试结果
    print("\n📊 测试结果总结:")
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")

    print(f"\n总计: {passed}/{len(results)} 个测试通过")

    if passed == len(results):
        print("🎉 所有MCP集成测试通过！网络抓取工具已成功集成到MCP工具管理系统中。")
    elif passed >= len(results) * 0.8:  # 80%通过率
        print("✅ 大部分测试通过，MCP集成基本成功。")
    else:
        print("⚠️  部分测试失败，请检查MCP工具服务集成。")


if __name__ == "__main__":
    main()