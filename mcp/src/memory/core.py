# -*- coding: utf-8 -*-
"""
@author: luhx
@file: core.py
@time: 2024/7/15 22:21
@desc: 记忆库核心管理器
"""
from typing import Any, Dict, List, Optional


class MemoryManager:
    """
    记忆库管理器 (MemoryManager)

    作为记忆库的统一入口，提供对核心、知识、工作三种记忆的
    增、删、改、查 (CRUD) 基础方法。

    本实现采用内存字典作为初始的存储后端，以实现快速原型开发。
    """

    def __init__(self) -> None:
        """
        初始化三类记忆存储空间。
        """
        self._core_memory: Dict[str, Any] = {}
        self._knowledge_memory: Dict[str, Any] = {}
        self._working_memory: Dict[str, Any] = {}

    def _get_storage(self, memory_type: str) -> Dict[str, Any]:
        """
        根据记忆类型获取对应的存储字典。

        这是一个内部辅助方法，用于简化CRUD操作，避免代码重复。

        Args:
            memory_type (str): 记忆类型，可选值为 'core', 'knowledge', 'working'。

        Returns:
            Dict[str, Any]: 对应类型的记忆存储字典。

        Raises:
            ValueError: 如果传入了未知的记忆类型。
        """
        if memory_type == "core":
            return self._core_memory
        if memory_type == "knowledge":
            return self._knowledge_memory
        if memory_type == "working":
            return self._working_memory
        raise ValueError(f"未知的记忆类型: '{memory_type}'")

    def create(self, memory_type: str, key: str, value: Any) -> None:
        """
        在指定类型的记忆中创建一个新的条目。

        Args:
            memory_type (str): 记忆类型。
            key (str): 记忆条目的唯一标识键。
            value (Any): 需要存储的记忆内容。

        Raises:
            KeyError: 如果键已存在，为防止意外覆盖，将抛出此异常。
        """
        storage = self._get_storage(memory_type)
        if key in storage:
            raise KeyError(f"键 '{key}' 已存在于 '{memory_type}' 记忆中。")
        storage[key] = value

    def read(self, memory_type: str, key: str) -> Optional[Any]:
        """
        从指定类型的记忆中读取一个条目。

        Args:
            memory_type (str): 记忆类型。
            key (str): 希望读取的记忆条目的键。

        Returns:
            Optional[Any]: 如果找到，则返回记忆内容；否则返回 None。
        """
        storage = self._get_storage(memory_type)
        return storage.get(key)

    def update(self, memory_type: str, key: str, value: Any) -> None:
        """
        更新指定类型记忆中一个已存在的条目。

        Args:
            memory_type (str): 记忆类型。
            key (str): 希望更新的记忆条目的键。
            value (Any): 新的记忆内容。

        Raises:
            KeyError: 如果指定的键不存在，将无法进行更新。
        """
        storage = self._get_storage(memory_type)
        if key not in storage:
            raise KeyError(f"键 '{key}' 在 '{memory_type}' 记忆中不存在。")
        storage[key] = value

    def delete(self, memory_type: str, key: str) -> None:
        """
        从指定类型的记忆中删除一个条目。

        Args:
            memory_type (str): 记忆类型。
            key (str): 希望删除的记忆条目的键。

        Raises:
            KeyError: 如果指定的键不存在，将无法进行删除。
        """
        storage = self._get_storage(memory_type)
        if key not in storage:
            raise KeyError(f"键 '{key}' 在 '{memory_type}' 记忆中不存在。")
        del storage[key]

    def list_keys(self, memory_type: str) -> List[str]:
        """
        列出指定类型记忆中所有的键。

        Args:
            memory_type (str): 记忆类型。

        Returns:
            List[str]: 包含所有键的列表。
        """
        storage = self._get_storage(memory_type)
        return list(storage.keys())

    def clear(self, memory_type: str) -> None:
        """
        清空指定类型的所有记忆。

        Args:
            memory_type (str): 记忆类型。
        """
        storage = self._get_storage(memory_type)
        storage.clear()