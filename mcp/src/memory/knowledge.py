# -*- coding: utf-8 -*-
"""
@author: luhx
@file: knowledge.py
@time: 2024/7/15 22:45
@desc: 知识库管理器
"""
from typing import List, Optional

from src.memory.core import MemoryManager
from src.memory.models import Knowledge, Relation


class KnowledgeManager:
    """
    知识库管理器 (KnowledgeManager)

    基于 MemoryManager，实现针对知识库的特定高级功能。
    此类通过组合 MemoryManager 来操作底层数据，专注于知识的
    搜索、关联等高级逻辑。
    """

    def __init__(self, memory_manager: MemoryManager):
        """
        初始化知识库管理器。

        Args:
            memory_manager (MemoryManager): 一个 MemoryManager 实例，用于底层存储。
        """
        self._manager = memory_manager

    def add(self, knowledge: Knowledge) -> None:
        """
        向知识库中添加一条新知识。

        Args:
            knowledge (Knowledge): 要添加的知识对象。

        Raises:
            TypeError: 如果传入的对象不是 Knowledge 类型。
            KeyError: 如果知识ID已存在。
        """
        if not isinstance(knowledge, Knowledge):
            raise TypeError("添加的对象必须是 Knowledge 类型。")
        # 存储时，我们将Pydantic模型转换为字典
        self._manager.create("knowledge", knowledge.id, knowledge.model_dump())

    def get(self, knowledge_id: str) -> Optional[Knowledge]:
        """
        根据ID获取一条知识。

        Args:
            knowledge_id (str): 知识的唯一ID。

        Returns:
            Optional[Knowledge]: 如果找到，则返回知识对象；否则返回 None。
        """
        knowledge_data = self._manager.read("knowledge", knowledge_id)
        if knowledge_data:
            return Knowledge(**knowledge_data)
        return None

    def search(
        self, query: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[Knowledge]:
        """
        根据查询字符串和/或标签搜索知识。

        Args:
            query (Optional[str]): 用于在知识内容中进行模糊匹配的查询字符串。
            tags (Optional[List[str]]): 用于筛选知识的标签列表。

        Returns:
            List[Knowledge]: 符合搜索条件的知识对象列表。
        """
        results: List[Knowledge] = []
        all_knowledge_keys = self._manager.list_keys("knowledge")

        for key in all_knowledge_keys:
            knowledge_data = self._manager.read("knowledge", key)
            if not knowledge_data:
                continue

            knowledge = Knowledge(**knowledge_data)
            match = True

            # 标签匹配逻辑：必须包含所有指定的标签
            if tags:
                if not all(tag in knowledge.tags for tag in tags):
                    match = False

            # 查询字符串匹配逻辑：在内容中进行不区分大小写的包含性检查
            if query and match:
                if isinstance(knowledge.content, str):
                    if query.lower() not in knowledge.content.lower():
                        match = False
                # 如果内容是字典，则当前简单实现不支持搜索
                elif isinstance(knowledge.content, dict):
                    # 未来可以扩展为在字典的值中搜索
                    pass

            if match:
                results.append(knowledge)

        return results

    def relate(self, source_id: str, target_id: str, relation_type: str) -> None:
        """
        在两条知识之间建立关联。

        Args:
            source_id (str): 源知识的ID。
            target_id (str): 目标知识的ID。
            relation_type (str): 关联类型 (例如: 'extends', 'conflicts_with')。

        Raises:
            KeyError: 如果源知识或目标知识ID不存在。
        """
        source_knowledge = self.get(source_id)
        if not source_knowledge:
            raise KeyError(f"源知识ID '{source_id}' 不存在。")

        # 验证目标知识是否存在
        if not self.get(target_id):
            raise KeyError(f"目标知识ID '{target_id}' 不存在。")

        # 创建并添加新的关联关系
        new_relation = Relation(target_id=target_id, type=relation_type)
        
        # 避免重复关联
        if new_relation not in source_knowledge.relations:
            source_knowledge.relations.append(new_relation)
            self._manager.update(
                "knowledge", source_id, source_knowledge.model_dump()
            )