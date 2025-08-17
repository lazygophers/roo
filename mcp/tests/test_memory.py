# -*- coding: utf-8 -*-
"""
@file: test_memory.py
@desc: 记忆库模块单元测试 (最终修复版)
"""
import pytest
from src.memory.core import MemoryManager
from src.memory.knowledge import KnowledgeManager
from src.memory.models import Knowledge, KnowledgeType, WorkingMemory
from src.memory.working import WorkingManager


@pytest.fixture
def memory_manager() -> MemoryManager:
    """提供一个干净的 MemoryManager 实例，并确保测试隔离"""
    return MemoryManager()


@pytest.fixture
def knowledge_manager(memory_manager: MemoryManager) -> KnowledgeManager:
    """提供一个基于干净 MemoryManager 的 KnowledgeManager 实例"""
    return KnowledgeManager(memory_manager)


@pytest.fixture
def working_manager(memory_manager: MemoryManager) -> WorkingManager:
    """提供一个基于干净 MemoryManager 的 WorkingManager 实例"""
    return WorkingManager(memory_manager)


class TestMemoryManager:
    """测试 MemoryManager 的基础 CRUD 功能"""

    def test_create_and_read(self, memory_manager: MemoryManager):
        """测试创建和读取功能"""
        memory_manager.create("core", "test_key", "test_value")
        assert memory_manager.read("core", "test_key") == "test_value"

    def test_create_duplicate_key_raises_error(self, memory_manager: MemoryManager):
        """测试创建重复键时应抛出 KeyError"""
        memory_manager.create("knowledge", "dup_key", "value1")
        with pytest.raises(KeyError, match="键 'dup_key' 已存在于 'knowledge' 记忆中"):
            memory_manager.create("knowledge", "dup_key", "value2")

    def test_read_nonexistent_key(self, memory_manager: MemoryManager):
        """测试读取不存在的键应返回 None"""
        assert memory_manager.read("working", "nonexistent") is None

    def test_update(self, memory_manager: MemoryManager):
        """测试更新功能"""
        memory_manager.create("core", "update_key", "initial_value")
        memory_manager.update("core", "update_key", "updated_value")
        assert memory_manager.read("core", "update_key") == "updated_value"

    def test_update_nonexistent_key_raises_error(self, memory_manager: MemoryManager):
        """测试更新不存在的键时应抛出 KeyError"""
        with pytest.raises(KeyError, match="键 'nonexistent' 在 'core' 记忆中不存在"):
            memory_manager.update("core", "nonexistent", "value")

    def test_delete(self, memory_manager: MemoryManager):
        """测试删除功能"""
        memory_manager.create("knowledge", "delete_key", "to_be_deleted")
        memory_manager.delete("knowledge", "delete_key")
        assert memory_manager.read("knowledge", "delete_key") is None

    def test_delete_nonexistent_key_raises_error(self, memory_manager: MemoryManager):
        """测试删除不存在的键时应抛出 KeyError"""
        with pytest.raises(KeyError, match="键 'nonexistent' 在 'knowledge' 记忆中不存在"):
            memory_manager.delete("knowledge", "nonexistent")


@pytest.fixture
def populated_knowledge_manager(knowledge_manager: KnowledgeManager) -> KnowledgeManager:
    """提供一个包含预置知识的 KnowledgeManager 实例"""
    knowledge_data = [
        Knowledge(
            content="SOLID principles are key to good design.",
            knowledge_type=KnowledgeType.PRINCIPLE,
            tags=["design-pattern", "oop"],
        ),
        Knowledge(
            content="Python's GIL can be a bottleneck for CPU-bound tasks.",
            knowledge_type=KnowledgeType.FACT,
            tags=["python", "performance"],
        ),
        Knowledge(
            content="Decorator pattern in Python simplifies code.",
            knowledge_type=KnowledgeType.PATTERN,
            tags=["python", "design-pattern"],
        ),
    ]
    for k in knowledge_data:
        knowledge_manager.add(k)
    return knowledge_manager


class TestKnowledgeManager:
    """测试 KnowledgeManager 的高级功能，采用更全面的测试策略"""

    def test_add_and_get_knowledge(self, knowledge_manager: KnowledgeManager):
        """测试添加和精确获取知识"""
        k = Knowledge(content="Python is dynamically typed", knowledge_type=KnowledgeType.FACT)
        knowledge_manager.add(k)
        retrieved_k = knowledge_manager.get(k.id)
        assert retrieved_k is not None
        assert retrieved_k.id == k.id
        assert retrieved_k.content == "Python is dynamically typed"

    def test_get_nonexistent_knowledge(self, knowledge_manager: KnowledgeManager):
        """测试获取不存在的知识应返回 None"""
        assert knowledge_manager.get("nonexistent-id") is None

    @pytest.mark.parametrize(
        "query, expected_count, expected_content_substring",
        [
            ("python", 2, "Python"),
            ("gil", 1, "GIL"),
            ("solid", 1, "SOLID"),
            ("nonexistent", 0, ""),
        ],
    )
    def test_search_by_query(
        self,
        populated_knowledge_manager: KnowledgeManager,
        query,
        expected_count,
        expected_content_substring,
    ):
        """测试按查询字符串搜索，覆盖多种情况"""
        results = populated_knowledge_manager.search(query=query)
        assert len(results) == expected_count
        if expected_count > 0:
            for res in results:
                assert expected_content_substring in res.content

    @pytest.mark.parametrize(
        "tags, expected_count, expected_contents",
        [
            (
                ["design-pattern"],
                2,
                {
                    "SOLID principles are key to good design.",
                    "Decorator pattern in Python simplifies code.",
                },
            ),
            (
                ["python"],
                2,
                {
                    "Python's GIL can be a bottleneck for CPU-bound tasks.",
                    "Decorator pattern in Python simplifies code.",
                },
            ),
            (["performance"], 1, {"Python's GIL can be a bottleneck for CPU-bound tasks."}),
            (["oop", "design-pattern"], 1, {"SOLID principles are key to good design."}),
            (["nonexistent-tag"], 0, set()),
        ],
    )
    def test_search_by_tags(
        self, populated_knowledge_manager: KnowledgeManager, tags, expected_count, expected_contents
    ):
        """测试按标签搜索，并验证返回结果的准确性"""
        results = populated_knowledge_manager.search(tags=tags)
        assert len(results) == expected_count
        result_contents = {res.content for res in results}
        assert result_contents == expected_contents

    def test_search_combined_query_and_tags(self, populated_knowledge_manager: KnowledgeManager):
        """测试查询和标签组合搜索"""
        results = populated_knowledge_manager.search(query="python", tags=["design-pattern"])
        assert len(results) == 1
        assert "Decorator pattern" in results[0].content

    def test_relate_knowledge_and_verify(self, knowledge_manager: KnowledgeManager):
        """测试知识关联功能并详细验证关联关系"""
        k1 = Knowledge(content="Parent class", knowledge_type=KnowledgeType.FACT, tags=["oop"])
        k2 = Knowledge(content="Child class", knowledge_type=KnowledgeType.FACT, tags=["oop"])
        knowledge_manager.add(k1)
        knowledge_manager.add(k2)

        knowledge_manager.relate(k2.id, k1.id, "extends")

        updated_k2 = knowledge_manager.get(k2.id)
        assert updated_k2 is not None
        assert len(updated_k2.relations) == 1
        relation = updated_k2.relations[0]
        assert relation.target_id == k1.id
        assert relation.type == "extends"

    def test_add_duplicate_relation(self, knowledge_manager: KnowledgeManager):
        """测试添加重复关联时应被忽略"""
        k1 = Knowledge(content="Concept A", knowledge_type=KnowledgeType.FACT)
        k2 = Knowledge(content="Concept B", knowledge_type=KnowledgeType.FACT)
        knowledge_manager.add(k1)
        knowledge_manager.add(k2)
        # 添加两次相同的关联
        knowledge_manager.relate(k1.id, k2.id, "related_to")
        knowledge_manager.relate(k1.id, k2.id, "related_to")

        updated_k1 = knowledge_manager.get(k1.id)
        assert len(updated_k1.relations) == 1, "重复的关联不应被添加"


class TestWorkingManager:
    """测试 WorkingManager 的特定功能"""

    def test_add_and_get_working_memory(self, working_manager: WorkingManager):
        """测试添加和获取工作记忆"""
        wm = WorkingMemory(content={"status": "in_progress"}, task_id="task-123")
        working_manager.add(wm)
        retrieved_wm = working_manager.get(wm.id)
        assert retrieved_wm is not None
        assert retrieved_wm.content["status"] == "in_progress"

    def test_update_working_memory(self, working_manager: WorkingManager):
        """测试更新工作记忆"""
        wm = WorkingMemory(content="initial state", task_id="task-abc")
        working_manager.add(wm)
        working_manager.update(wm.id, "updated state")
        updated_wm = working_manager.get(wm.id)
        assert updated_wm is not None
        assert updated_wm.content == "updated state"

    def test_clear_task_context(self, working_manager: WorkingManager):
        """测试清理特定任务的上下文"""
        wm1 = WorkingMemory(content="data for task 1", task_id="task-001")
        wm2 = WorkingMemory(content="more data for task 1", task_id="task-001")
        wm3 = WorkingMemory(content="data for task 2", task_id="task-002")
        working_manager.add(wm1)
        working_manager.add(wm2)
        working_manager.add(wm3)

        working_manager.clear_task_context("task-001")

        assert working_manager.get(wm1.id) is None
        assert working_manager.get(wm2.id) is None
        assert working_manager.get(wm3.id) is not None
