#!/usr/bin/env python3
"""
测试知识库功能
"""
import asyncio
import requests
import json
from pathlib import Path

API_BASE = "http://localhost:8000/api"

async def test_knowledge_base():
    """测试知识库功能"""
    print("🧪 开始测试知识库功能...")

    # 1. 测试知识库服务状态
    print("\n1. 测试知识库服务状态")
    try:
        response = requests.post(f"{API_BASE}/knowledge-base/test")
        result = response.json()
        if result.get("success"):
            print("✅ 知识库服务正常")
            print(f"   - 数据库路径: {result['data']['database_path']}")
            print(f"   - 服务已初始化: {result['data']['service_initialized']}")
            print(f"   - 模型已加载: {result['data']['model_loaded']}")
        else:
            print(f"❌ 知识库服务异常: {result}")
            return
    except Exception as e:
        print(f"❌ 无法连接到知识库服务: {e}")
        return

    # 2. 获取支持的文件格式
    print("\n2. 获取支持的文件格式")
    try:
        response = requests.get(f"{API_BASE}/knowledge-base/supported-formats")
        result = response.json()
        if result.get("success"):
            formats = result["data"]["formats"]
            descriptions = result["data"]["descriptions"]
            print("✅ 支持的文件格式:")
            for fmt in formats:
                desc = descriptions.get(fmt, "")
                print(f"   - {fmt}: {desc}")
        else:
            print(f"❌ 获取格式失败: {result}")
    except Exception as e:
        print(f"❌ 获取格式失败: {e}")

    # 3. 获取知识库统计
    print("\n3. 获取知识库统计")
    try:
        response = requests.get(f"{API_BASE}/knowledge-base/stats")
        result = response.json()
        if result.get("success"):
            stats = result["data"]
            print("✅ 知识库统计:")
            print(f"   - 总文档数: {stats['total_documents']}")
            print(f"   - 总文本块: {stats['total_chunks']}")
            print(f"   - 总大小: {stats['total_size_mb']:.2f} MB")
        else:
            print(f"❌ 获取统计失败: {result}")
    except Exception as e:
        print(f"❌ 获取统计失败: {e}")

    # 4. 创建测试文档
    print("\n4. 创建测试文档")
    test_file_path = Path("test_document.txt")
    test_content = """
    LazyAI Studio 知识库测试文档

    这是一个测试文档，用于验证知识库的文档处理和检索功能。

    主要功能包括：
    1. 文档上传和处理
    2. 文本向量化存储
    3. 智能检索和RAG查询
    4. 多种文件格式支持

    技术栈：
    - LanceDB: 向量数据库
    - SentenceTransformer: 文本嵌入模型
    - FastAPI: Web API框架
    - React: 前端界面

    这个文档包含了一些关键词，可以用来测试搜索功能。
    """

    try:
        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_content)
        print(f"✅ 创建测试文档: {test_file_path}")

        # 5. 添加文档到知识库
        print("\n5. 添加文档到知识库")
        response = requests.post(
            f"{API_BASE}/knowledge-base/documents/add",
            json={
                "file_path": str(test_file_path.absolute()),
                "metadata": {
                    "category": "测试文档",
                    "author": "系统测试",
                    "description": "用于测试知识库功能"
                }
            }
        )

        result = response.json()
        if result.get("success"):
            print("✅ 文档添加成功")
            print(f"   - 文件路径: {result['data']['file_path']}")
            print(f"   - 文本块数: {result['data']['chunks_count']}")
        else:
            print(f"❌ 文档添加失败: {result}")

    except Exception as e:
        print(f"❌ 文档操作失败: {e}")

    # 6. 测试搜索功能
    print("\n6. 测试搜索功能")
    search_queries = [
        "LazyAI Studio 功能",
        "技术栈",
        "向量数据库",
        "文档处理"
    ]

    for query in search_queries:
        try:
            response = requests.post(
                f"{API_BASE}/knowledge-base/search",
                json={
                    "query": query,
                    "limit": 3,
                    "threshold": 0.3
                }
            )

            result = response.json()
            if result.get("success"):
                results = result["data"]
                print(f"✅ 搜索 '{query}' 找到 {len(results)} 个结果")
                for i, res in enumerate(results[:2], 1):
                    score = res['score']
                    content_preview = res['content'][:100] + "..." if len(res['content']) > 100 else res['content']
                    print(f"   {i}. 相关度: {score:.3f}")
                    print(f"      内容: {content_preview}")
            else:
                print(f"❌ 搜索 '{query}' 失败: {result}")
        except Exception as e:
            print(f"❌ 搜索 '{query}' 失败: {e}")

    # 7. 获取文档列表
    print("\n7. 获取文档列表")
    try:
        response = requests.get(f"{API_BASE}/knowledge-base/documents")
        result = response.json()
        if result.get("success"):
            documents = result["data"]
            print(f"✅ 知识库包含 {len(documents)} 个文档")
            for doc in documents[:3]:  # 只显示前3个
                print(f"   - {doc['file_name']} ({doc['file_type']}) - {doc['chunks_count']} 块")
        else:
            print(f"❌ 获取文档列表失败: {result}")
    except Exception as e:
        print(f"❌ 获取文档列表失败: {e}")

    # 清理测试文件
    try:
        if test_file_path.exists():
            test_file_path.unlink()
            print(f"\n🗑️  清理测试文件: {test_file_path}")
    except Exception as e:
        print(f"⚠️  清理测试文件失败: {e}")

    print("\n🎉 知识库功能测试完成！")

if __name__ == "__main__":
    asyncio.run(test_knowledge_base())