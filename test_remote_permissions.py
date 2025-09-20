#!/usr/bin/env python3
"""
测试 remote 模式下的 MCP 工具权限控制
"""
import os
import sys
import subprocess
import time
import requests
import json

def test_local_mode():
    """测试local模式下的工具访问"""
    print("🔍 测试 local 模式下的工具访问...")

    # 设置环境变量为local
    os.environ["ENVIRONMENT"] = "local"

    # 刷新权限管理器以使环境变量生效
    refresh_permissions("local")

    # 测试权限端点
    response = requests.get("http://localhost:8000/api/mcp/permissions")
    data = response.json()

    print(f"✅ Environment: {data['data']['environment']}")
    print(f"✅ Allowed tools: {data['data']['permission_info']['allowed_tools']}")
    print(f"✅ Blocked tools: {data['data']['permission_info']['blocked_tools']}")
    print(f"✅ Restrictions active: {data['data']['restrictions_active']}")

    # 测试写入工具调用（应该成功）
    test_write_tool_call("cache_set")

    return data

def test_remote_mode():
    """测试remote模式下的工具访问"""
    print("\n🔍 测试 remote 模式下的工具访问...")

    # 设置环境变量为remote
    os.environ["ENVIRONMENT"] = "remote"

    # 刷新权限管理器以使环境变量生效
    refresh_permissions("remote")

    # 测试权限端点
    response = requests.get("http://localhost:8000/api/mcp/permissions")
    data = response.json()

    print(f"🔒 Environment: {data['data']['environment']}")
    print(f"🔒 Allowed tools: {data['data']['permission_info']['allowed_tools']}")
    print(f"🔒 Blocked tools: {data['data']['permission_info']['blocked_tools']}")
    print(f"🔒 Restrictions active: {data['data']['restrictions_active']}")

    # 测试只读工具调用（应该成功）
    test_read_tool_call("cache_get")

    # 测试写入工具调用（应该失败）
    test_write_tool_call("cache_set")

    return data

def test_read_tool_call(tool_name):
    """测试只读工具调用"""
    print(f"\n📖 测试只读工具调用: {tool_name}")

    payload = {
        "name": tool_name,
        "arguments": {"key": "test_key"}
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/mcp/call-tool",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        data = response.json()

        if data.get("success"):
            print(f"✅ {tool_name} 调用成功")
        else:
            print(f"❌ {tool_name} 调用失败: {data.get('message', 'Unknown error')}")
            if data.get("error_code") == "TOOL_PERMISSION_DENIED":
                print(f"🔒 权限拒绝: {data.get('data', {}).get('permission_level', 'Unknown')}")

        return data

    except Exception as e:
        print(f"💥 请求异常: {e}")
        return None

def test_write_tool_call(tool_name):
    """测试写入工具调用"""
    print(f"\n✏️ 测试写入工具调用: {tool_name}")

    payload = {
        "name": tool_name,
        "arguments": {"key": "test_key", "value": "test_value"}
    }

    try:
        response = requests.post(
            "http://localhost:8000/api/mcp/call-tool",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        data = response.json()

        if data.get("success"):
            print(f"✅ {tool_name} 调用成功")
        else:
            print(f"❌ {tool_name} 调用失败: {data.get('message', 'Unknown error')}")
            if data.get("error_code") == "TOOL_PERMISSION_DENIED":
                print(f"🔒 权限拒绝: {data.get('data', {}).get('permission_level', 'Unknown')}")

        return data

    except Exception as e:
        print(f"💥 请求异常: {e}")
        return None

def refresh_permissions(environment: str):
    """刷新权限管理器以使环境变量生效"""
    print(f"🔄 刷新权限管理器以使环境变量生效 - 切换到 {environment} 模式...")

    try:
        payload = {"environment": environment}
        response = requests.post(
            "http://localhost:8000/api/mcp/permissions/refresh",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ 权限管理器已刷新 - 环境: {data['data']['environment']}")
                return
            else:
                print(f"❌ 权限刷新失败: {data.get('message', 'Unknown error')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    except Exception as e:
        print(f"💥 刷新异常: {e}")
        print("⚠️ 请确保后端服务正在运行")

def print_summary(local_data, remote_data):
    """打印测试总结"""
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    print(f"Local模式:")
    print(f"  - 允许工具: {local_data['data']['permission_info']['allowed_tools']}")
    print(f"  - 阻止工具: {local_data['data']['permission_info']['blocked_tools']}")
    print(f"  - 限制激活: {local_data['data']['restrictions_active']}")

    print(f"\nRemote模式:")
    print(f"  - 允许工具: {remote_data['data']['permission_info']['allowed_tools']}")
    print(f"  - 阻止工具: {remote_data['data']['permission_info']['blocked_tools']}")
    print(f"  - 限制激活: {remote_data['data']['restrictions_active']}")

    print(f"\n权限控制效果:")
    local_allowed = local_data['data']['permission_info']['allowed_tools']
    remote_allowed = remote_data['data']['permission_info']['allowed_tools']
    blocked_count = local_allowed - remote_allowed

    print(f"  - Local模式允许的工具数: {local_allowed}")
    print(f"  - Remote模式允许的工具数: {remote_allowed}")
    print(f"  - Remote模式阻止的工具数: {blocked_count}")
    print(f"  - 权限控制生效: {'✅ 是' if blocked_count > 0 else '❌ 否'}")

if __name__ == "__main__":
    print("🚀 启动 MCP 工具权限控制测试")
    print("="*60)

    try:
        # 测试local模式
        local_data = test_local_mode()

        # 测试remote模式
        remote_data = test_remote_mode()

        # 打印总结
        print_summary(local_data, remote_data)

        print("\n✅ 测试完成！")

    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试异常: {e}")
    finally:
        # 恢复到local模式
        os.environ["ENVIRONMENT"] = "local"
        print("\n🔄 恢复环境为 local 模式")
        refresh_permissions("local")