# -*- coding: utf-8 -*-
"""
@author: luhx
@file: knowledge.py
@time: 2024/7/15 22:45
@desc: 提供了知识库的高级管理功能，专注于知识的搜索、关联和生命周期管理。
"""
from typing import List, Optional

from src.memory.core import MemoryManager
from src.memory.models import Knowledge, Relation


class KnowledgeManager:
    """知识库管理器。

    基于 MemoryManager，实现针对知识库的特定高级功能。
    此类采用组合模式，通过持有一个 MemoryManager 实例来操作底层数据，
    自身则专注于实现知识的搜索、关联等面向业务的高级逻辑。

    Attributes:
        _manager: 一个 MemoryManager 实例，用于底层存储的增删改查。
    """

    def __init__(self, memory_manager: MemoryManager):
        """初始化知识库管理器。

        Args:
            memory_manager: 一个 MemoryManager 实例，用于底层存储。
        """
        self._manager = memory_manager

    def add(self, knowledge: Knowledge) -> None:
        """向知识库中添加一条新知识。

        在存储前，会将 Knowledge 对象序列化为字典。

        Args:
            knowledge: 要添加的知识对象，必须是 Knowledge 类型。

        Raises:
            TypeError: 如果传入的对象不是 Knowledge 类型。
            KeyError: 如果知识ID已存在，防止重复添加。
        """
        if not isinstance(knowledge, Knowledge):
            raise TypeError("添加的对象必须是 Knowledge 类型。")
        # 存储时，我们将Pydantic模型转换为字典以实现持久化
        self._manager.create("knowledge", knowledge.id, knowledge.model_dump())

    def get(self, knowledge_id: str) -> Optional[Knowledge]:
        """根据ID获取一条知识。

        从底层存储读取数据后，会将其反序列化为 Knowledge 对象。

        Args:
            knowledge_id: 知识的唯一ID。

        Returns:
            如果找到，则返回知识对象；否则返回 None。
        """
        knowledge_data = self._manager.read("knowledge", knowledge_id)
        if knowledge_data:
            # 将字典数据转换回 Pydantic 模型实例
            return Knowledge(**knowledge_data)
        return None

    def search(
        self, query: Optional[str] = None, tags: Optional[List[str]] = None
    ) -> List[Knowledge]:
        """根据查询字符串和/或标签搜索知识。

        这是一个简单的多条件搜索实现。标签搜索要求知识点
        包含所有指定的标签（AND逻辑）。查询字符串则在知识内容
        （仅限字符串类型）中进行不区分大小写的包含性检查。

        Args:
            query: 用于在知识内容中进行模糊匹配的查询字符串。
            tags: 用于筛选知识的标签列表。

        Returns:
            符合搜索条件的知识对象列表。
        """
        results: List[Knowledge] = []
        all_knowledge_keys = self._manager.list_keys("knowledge")

        for key in all_knowledge_keys:
            knowledge_data = self._manager.read("knowledge", key)
            if not knowledge_data:
                continue

            knowledge = Knowledge(**knowledge_data)
            match = True

            # 标签匹配逻辑：必须包含所有指定的标签 (AND condition)
            if tags:
                if not all(tag in knowledge.tags for tag in tags):
                    match = False

            # 查询字符串匹配逻辑：在内容中进行不区分大小写的包含性检查
            if query and match:
                if isinstance(knowledge.content, str):
                    if query.lower() not in knowledge.content.lower():
                        match = False
                # 当前实现暂不支持在结构化数据（字典）中搜索
                elif isinstance(knowledge.content, dict):
                    # TODO: 未来可以扩展为在字典的键或值中进行深度搜索
                    pass

            if match:
                results.append(knowledge)

        return results

    def relate(self, source_id: str, target_id: str, relation_type: str) -> None:
        """在两条知识之间建立关联。

        此方法会在源知识对象中添加一个指向目标知识的关联关系。

        Args:
            source_id: 源知识的ID。
            target_id: 目标知识的ID。
            relation_type: 关联类型 (例如: 'extends', 'conflicts_with')。

        Raises:
            KeyError: 如果源知识或目标知识ID不存在。
        """
        source_knowledge = self.get(source_id)
        if not source_knowledge:
            raise KeyError(f"源知识ID '{source_id}' 不存在。")

        # 验证目标知识是否存在，确保关联的有效性
        if not self.get(target_id):
            raise KeyError(f"目标知识ID '{target_id}' 不存在。")

        # 创建并添加新的关联关系
        new_relation = Relation(target_id=target_id, type=relation_type)

        # 为防止重复关联，添加前进行检查
        if new_relation not in source_knowledge.relations:
            source_knowledge.relations.append(new_relation)
            self._manager.update("knowledge", source_id, source_knowledge.model_dump())
