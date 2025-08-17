# -*- coding: utf-8 -*-
"""
@author: luhx
@file: working.py
@time: 2024/7/15 23:05
@desc: 提供了工作记忆的高级管理功能，专注于处理与当前任务相关的短期上下文。
"""
from datetime import datetime, timezone
from typing import Any, Optional

from src.memory.core import MemoryManager
from src.memory.models import WorkingMemory


class WorkingManager:
    """工作记忆管理器。

    基于 MemoryManager，实现针对工作记忆的特定功能。
    此类专注于处理生命周期短、高频更新的上下文数据，并提供了
    在任务完成后进行高效清理的机制。

    Attributes:
        _manager: 一个 MemoryManager 实例，用于底层存储。
    """

    def __init__(self, memory_manager: MemoryManager):
        """初始化工作记忆管理器。

        Args:
            memory_manager: 一个 MemoryManager 实例，用于底层存储。
        """
        self._manager = memory_manager

    def add(self, memory: WorkingMemory) -> None:
        """添加一条新的工作记忆。

        Args:
            memory: 要添加的工作记忆对象。

        Raises:
            TypeError: 如果传入的对象不是 WorkingMemory 类型。
            KeyError: 如果记忆ID已存在。
        """
        if not isinstance(memory, WorkingMemory):
            raise TypeError("添加的对象必须是 WorkingMemory 类型。")
        self._manager.create("working", memory.id, memory.model_dump())

    def get(self, memory_id: str) -> Optional[WorkingMemory]:
        """根据ID获取一条工作记忆。

        Args:
            memory_id: 记忆的唯一ID。

        Returns:
            如果找到，则返回工作记忆对象；否则返回 None。
        """
        memory_data = self._manager.read("working", memory_id)
        if memory_data:
            return WorkingMemory(**memory_data)
        return None

    def update(self, memory_id: str, new_content: Any) -> None:
        """高频更新一条工作记忆的内容。

        此方法会直接更新内容，并自动刷新 `updated_at` 时间戳，
        以准确反映最近的修改时间。

        Args:
            memory_id: 要更新的工作记忆ID。
            new_content: 新的记忆内容。

        Raises:
            KeyError: 如果ID不存在。
        """
        memory = self.get(memory_id)
        if not memory:
            raise KeyError(f"工作记忆ID '{memory_id}' 不存在。")

        memory.content = new_content
        # 必须手动更新时间戳。Pydantic模型的default_factory仅在创建时生效，
        # 在更新现有实例时不会自动重新触发。
        memory.updated_at = datetime.now(timezone.utc)

        self._manager.update("working", memory_id, memory.model_dump())

    def clear_task_context(self, task_id: str) -> None:
        """清理与特定任务相关的所有工作记忆。

        这是一个安全的操作，它会遍历所有工作记忆，找到匹配
        `task_id` 的条目，然后将它们全部删除。

        Args:
            task_id: 需要清理上下文的任务ID。
        """
        keys_to_delete = []
        all_working_keys = self._manager.list_keys("working")

        # 第一步：收集所有待删除记忆的键
        # 这是为了避免在迭代字典/列表时直接修改它，这可能导致不可预料的行为。
        for key in all_working_keys:
            memory_data = self._manager.read("working", key)
            if memory_data:
                memory = WorkingMemory(**memory_data)
                if memory.task_id == task_id:
                    keys_to_delete.append(key)

        # 第二步：执行删除操作
        for key in keys_to_delete:
            self._manager.delete("working", key)

    def clear_all(self) -> None:
        """清空所有的工作记忆。

        这是一个危险操作，会立即移除所有工作记忆。
        通常在会话结束或需要完全重置上下文时使用。
        """
        self._manager.clear("working")
