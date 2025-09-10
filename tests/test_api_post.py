#!/usr/bin/env python3
"""
API 测试脚本 - POST 版本
"""
import httpx
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

async def test_api():
    """测试所有 API 接口（POST 版本）"""
    
    async with httpx.AsyncClient() as client:
        print("🧪 开始测试 Roo Models API (POST 版本)...")
        
        # 测试根路径
        print("\n1. 测试根路径...")
        response = await client.get(f"{BASE_URL}/")
        assert response.status_code == 200
        print(f"✅ 根路径正常: {response.json()}")
        
        # 测试健康检查
        print("\n2. 测试健康检查...")
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        print(f"✅ 健康检查正常: {response.json()}")
        
        # 测试获取所有模型 (POST)
        print("\n3. 测试获取所有模型 (POST)...")
        response = await client.post(f"{BASE_URL}/api/models", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["total"] > 0
        print(f"✅ 获取到 {data['total']} 个模型")
        
        # 验证字段过滤
        first_model = data["data"][0]
        assert "customInstructions" not in first_model
        expected_fields = {"slug", "name", "roleDefinition", "whenToUse", "description", "groups", "file_path"}
        actual_fields = set(first_model.keys())
        assert expected_fields == actual_fields
        print("✅ 字段过滤正确，已排除 customInstructions")
        
        # 测试分类过滤 - coder (POST)
        print("\n4. 测试 coder 分类过滤 (POST)...")
        response = await client.post(f"{BASE_URL}/api/models", json={"category": "coder"})
        assert response.status_code == 200
        coder_data = response.json()
        print(f"✅ Coder 模式数量: {coder_data['total']}")
        
        # 测试分类过滤 - core (POST)
        print("\n5. 测试 core 分类过滤 (POST)...")
        response = await client.post(f"{BASE_URL}/api/models", json={"category": "core"})
        assert response.status_code == 200
        core_data = response.json()
        print(f"✅ Core 模式数量: {core_data['total']}")
        
        # 测试单个模型获取 (POST)
        print("\n6. 测试获取单个模型 (POST)...")
        test_slug = "code-python-ai"
        response = await client.post(f"{BASE_URL}/api/models/by-slug", json={"slug": test_slug})
        assert response.status_code == 200
        model = response.json()
        assert model["slug"] == test_slug
        print(f"✅ 获取单个模型成功: {model['name']}")
        
        # 测试关键词搜索 (POST)
        print("\n7. 测试关键词搜索 (POST)...")
        response = await client.post(f"{BASE_URL}/api/models", json={"search": "Python"})
        assert response.status_code == 200
        search_data = response.json()
        print(f"✅ 搜索 'Python' 找到 {search_data['total']} 个模型")
        
        # 测试分类列表 (POST)
        print("\n8. 测试获取分类列表 (POST)...")
        response = await client.post(f"{BASE_URL}/api/models/categories/list")
        assert response.status_code == 200
        categories = response.json()
        stats = categories["data"]
        print(f"✅ 分类统计: Core={len(stats['core'])}, Coder={len(stats['coder'])}")
        
        # 测试不存在的模型 (POST)
        print("\n9. 测试不存在的模型 (POST)...")
        response = await client.post(f"{BASE_URL}/api/models/by-slug", json={"slug": "non-existent"})
        assert response.status_code == 404
        print("✅ 不存在的模型正确返回 404")
        
        # 测试 before hook (POST)
        print("\n10. 测试获取 before hook (POST)...")
        response = await client.post(f"{BASE_URL}/api/hooks/before")
        assert response.status_code == 200
        before_data = response.json()
        assert before_data["success"] is True
        assert before_data["data"]["name"] == "before"
        assert "content" in before_data["data"]
        print(f"✅ Before hook: {before_data['data']['title']}")
        
        # 测试 after hook (POST)
        print("\n11. 测试获取 after hook (POST)...")
        response = await client.post(f"{BASE_URL}/api/hooks/after")
        assert response.status_code == 200
        after_data = response.json()
        assert after_data["success"] is True
        assert after_data["data"]["name"] == "after"
        assert "content" in after_data["data"]
        print(f"✅ After hook: {after_data['data']['title']}")
        
        # 测试获取所有 hooks (POST)
        print("\n12. 测试获取所有 hooks (POST)...")
        response = await client.post(f"{BASE_URL}/api/hooks")
        assert response.status_code == 200
        hooks_data = response.json()
        assert hooks_data["success"] is True
        assert "before" in hooks_data["data"]
        assert "after" in hooks_data["data"]
        print("✅ 获取所有 hooks 成功")
        
        # 测试获取可用的 rules 目录 (POST)
        print("\n13. 测试获取可用的 rules 目录 (POST)...")
        response = await client.post(f"{BASE_URL}/api/rules")
        assert response.status_code == 200
        rules_dirs = response.json()
        assert rules_dirs["success"] is True
        assert rules_dirs["total"] > 0
        print(f"✅ 找到 {rules_dirs['total']} 个 rules 目录")
        
        # 测试 code-go 的 rules 查找 (POST)
        print("\n14. 测试 code-go 的 rules 查找 (POST)...")
        response = await client.post(f"{BASE_URL}/api/rules/by-slug", json={"slug": "code-go"})
        assert response.status_code == 200
        code_go_rules = response.json()
        assert code_go_rules["success"] is True
        assert code_go_rules["slug"] == "code-go"
        assert "rules-code-go" in code_go_rules["searched_directories"]
        assert "rules-code" in code_go_rules["searched_directories"]
        assert "rules" in code_go_rules["searched_directories"]
        print(f"✅ code-go 查找成功: 搜索了 {len(code_go_rules['searched_directories'])} 个目录，找到 {len(code_go_rules['found_directories'])} 个，获取 {code_go_rules['total']} 个文件")
        
        # 测试复杂 slug 的 rules 查找 (POST)
        print("\n15. 测试复杂 slug 的 rules 查找 (POST)...")
        response = await client.post(f"{BASE_URL}/api/rules/by-slug", json={"slug": "code-python-ai"})
        assert response.status_code == 200
        complex_rules = response.json()
        assert complex_rules["success"] is True
        assert complex_rules["slug"] == "code-python-ai"
        expected_search = ["rules-code-python-ai", "rules-code-python", "rules-code", "rules"]
        assert complex_rules["searched_directories"] == expected_search
        print(f"✅ 复杂 slug 查找成功: {complex_rules['total']} 个文件")
        
        # 验证文件 metadata 结构
        if complex_rules["data"]:
            first_file = complex_rules["data"][0]
            required_fields = {"file_path", "source_directory", "file_size", "last_modified"}
            actual_fields = set(first_file.keys())
            assert required_fields.issubset(actual_fields)
            print("✅ 文件 metadata 结构正确")
        
        print("\n🎉 所有 POST API 测试通过！")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_api())