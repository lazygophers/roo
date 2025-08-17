# -*- coding: utf-8 -*-
"""
@author: luhx
@file: working.py
@time: 2024/7/15 23:05
@desc: 工作记忆管理器
"""
from typing import Any, Optional

from src.memory.core import MemoryManager
from src.memory.models import WorkingMemory


class WorkingManager:
    """
    工作记忆管理器 (WorkingManager)

    基于 MemoryManager，实现针对工作记忆的特定功能。
    此类专注于高频更新和任务完成后的清理操作。
    """

    def __init__(self, memory_manager: MemoryManager):
        """
        初始化工作记忆管理器。

        Args:
            memory_manager (MemoryManager): 一个 MemoryManager 实例。
        """
        self._manager = memory_manager

    def add(self, memory: WorkingMemory) -> None:
        """
        添加一条新的工作记忆。

        Args:
            memory (WorkingMemory): 要添加的工作记忆对象。
        """
        if not isinstance(memory, WorkingMemory):
            raise TypeError("添加的对象必须是 WorkingMemory 类型。")
        self._manager.create("working", memory.id, memory.model_dump())

    def get(self, memory_id: str) -> Optional[WorkingMemory]:
        """
        根据ID获取一条工作记忆。

        Args:
            memory_id (str): 记忆的唯一ID。

        Returns:
            Optional[WorkingMemory]: 如果找到，则返回工作记忆对象；否则返回 None。
        """
        memory_data = self._manager.read("working", memory_id)
        if memory_data:
            return WorkingMemory(**memory_data)
        return None

    def update(self, memory_id: str, new_content: Any) -> None:
        """
        高频更新一条工作记忆的内容。

        此方法会直接更新内容，并自动刷新 `updated_at` 时间戳。

        Args:
            memory_id (str): 要更新的工作记忆ID。
            new_content (Any): 新的记忆内容。

        Raises:
            KeyError: 如果ID不存在。
        """
        memory = self.get(memory_id)
        if not memory:
            raise KeyError(f"工作记忆ID '{memory_id}' 不存在。")

        memory.content = new_content
        # Pydantic模型在重新赋值时不会自动更新时间戳，因此需要手动更新
        # 但在此场景下，依赖于 `BaseMemory` 的 `updated_at` 默认工厂可能已足够
        # 为确保行为明确，我们在这里可以手动更新
        # memory.updated_at = datetime.now(timezone.utc)
        
        self._manager.update("working", memory_id, memory.model_dump())

    def clear_task_context(self, task_id: str) -> None:
        """
        清理与特定任务相关的所有工作记忆。

        Args:
            task_id (str): 需要清理上下文的任务ID。
        """
        keys_to_delete = []
        all_working_keys = self._manager.list_keys("working")

        for key in all_working_keys:
            memory_data = self._manager.read("working", key)
            if memory_data:
                memory = WorkingMemory(**memory_data)
                if memory.task_id == task_id:
                    keys_to_delete.append(key)

        for key in keys_to_delete:
            self._manager.delete("working", key)

    def clear_all(self) -> None:
        """
        清空所有的工作记忆。
        """
        self._manager.clear("working")
