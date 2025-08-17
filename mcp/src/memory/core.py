# -*- coding: utf-8 -*-
"""
@author: luhx
@file: core.py
@time: 2024/7/15 22:21
@desc: 提供了记忆库的核心管理功能，是与记忆交互的统一入口。
"""
from typing import Any, Dict, List, Literal, Optional


class MemoryManager:
    """记忆库管理器。

    作为记忆库的统一入口，提供对核心、知识、工作三种记忆的
    增、删、改、查 (CRUD) 基础方法。

    本实现采用内存字典作为初始的存储后端，以便快速原型开发。
    未来可以方便地替换为更持久化的存储方案，如数据库或文件系统，
    而无需更改外部接口。

    Attributes:
        _core_memory: 用于存储核心记忆的字典。
        _knowledge_memory: 用于存储知识库的字典。
        _working_memory: 用于存储工作记忆的字典。
    """

    def __init__(self) -> None:
        """初始化三类记忆的存储空间。"""
        self._core_memory: Dict[str, Any] = {}
        self._knowledge_memory: Dict[str, Any] = {}
        self._working_memory: Dict[str, Any] = {}

    def _get_storage(self, memory_type: Literal["core", "knowledge", "working"]) -> Dict[str, Any]:
        """根据记忆类型获取对应的存储字典。

        这是一个内部辅助方法，用于简化CRUD操作，避免代码重复。

        Args:
            memory_type: 记忆类型，可选值为 'core', 'knowledge', 'working'。

        Returns:
            对应类型的记忆存储字典。

        Raises:
            ValueError: 如果传入了未知的记忆类型。
        """
        if memory_type == "core":
            # 返回核心记忆的存储区
            return self._core_memory
        if memory_type == "knowledge":
            # 返回知识库的存储区
            return self._knowledge_memory
        if memory_type == "working":
            # 返回工作记忆的存储区
            return self._working_memory
        # 如果类型不匹配，则应引发错误，防止意外操作
        raise ValueError(f"未知的记忆类型: '{memory_type}'")

    def create(
        self, memory_type: Literal["core", "knowledge", "working"], key: str, value: Any
    ) -> None:
        """在指定类型的记忆中创建一个新的条目。

        Args:
            memory_type: 要操作的记忆类型。
            key: 记忆条目的唯一标识键。
            value: 需要存储的记忆内容。

        Raises:
            KeyError: 如果键已存在，为防止意外覆盖，将抛出此异常。
        """
        storage = self._get_storage(memory_type)
        if key in storage:
            raise KeyError(f"键 '{key}' 已存在于 '{memory_type}' 记忆中。")
        storage[key] = value

    def read(self, memory_type: Literal["core", "knowledge", "working"], key: str) -> Optional[Any]:
        """从指定类型的记忆中读取一个条目。

        Args:
            memory_type: 要读取的记忆类型。
            key: 希望读取的记忆条目的键。

        Returns:
            如果找到，则返回记忆内容；否则返回 None。
        """
        storage = self._get_storage(memory_type)
        return storage.get(key)

    def update(
        self, memory_type: Literal["core", "knowledge", "working"], key: str, value: Any
    ) -> None:
        """更新指定类型记忆中一个已存在的条目。

        Args:
            memory_type: 要更新的记忆类型。
            key: 希望更新的记忆条目的键。
            value: 新的记忆内容。

        Raises:
            KeyError: 如果指定的键不存在，将无法进行更新。
        """
        storage = self._get_storage(memory_type)
        if key not in storage:
            raise KeyError(f"键 '{key}' 在 '{memory_type}' 记忆中不存在。")
        storage[key] = value

    def delete(self, memory_type: Literal["core", "knowledge", "working"], key: str) -> None:
        """从指定类型的记忆中删除一个条目。

        Args:
            memory_type: 要删除的记忆类型。
            key: 希望删除的记忆条目的键。

        Raises:
            KeyError: 如果指定的键不存在，将无法进行删除。
        """
        storage = self._get_storage(memory_type)
        if key not in storage:
            raise KeyError(f"键 '{key}' 在 '{memory_type}' 记忆中不存在。")
        del storage[key]

    def list_keys(self, memory_type: Literal["core", "knowledge", "working"]) -> List[str]:
        """列出指定类型记忆中所有的键。

        Args:
            memory_type: 要列出键的记忆类型。

        Returns:
            一个包含所有键的列表。
        """
        storage = self._get_storage(memory_type)
        return list(storage.keys())

    def clear(self, memory_type: Literal["core", "knowledge", "working"]) -> None:
        """清空指定类型的所有记忆。

        Args:
            memory_type: 要清空的记忆类型。
        """
        storage = self._get_storage(memory_type)
        storage.clear()
