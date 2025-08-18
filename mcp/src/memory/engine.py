# -*- coding: utf-8 -*-
"""
@author: lancelrq
@description: 智能引擎，负责将文档中的核心业务逻辑转化为具体的 Python 代码。
"""

import logging
import numpy as np
from typing import Optional, Dict, Any, Tuple, List

from src.memory.database import DatabaseService
from src.memory.models import BaseMemory, CoreMemory, KnowledgeMemory, WorkingMemory


class MemoryStatusException(Exception):
    """当记忆库状态不允许操作时抛出此异常。"""
    pass


class IntelligentEngine:
    """
    智能引擎类，封装了记忆的存储、检索和管理的核心业务逻辑。

    该引擎通过与 DatabaseService 交互，实现了层级化的记忆存储和
    上下文感知的记忆检索功能。
    """

    def __init__(self, database_service: Optional[DatabaseService] = None):
        """
        初始化智能引擎。

        :param database_service: 数据库服务实例。如果未提供，则会自动创建一个新的实例。
        """
        self.db_service = database_service if database_service else DatabaseService()
        logging.info("智能引擎初始化完成。")

    def _vectorize(self, text: str) -> np.ndarray:
        """
        将输入文本转化为向量表示。

        这是一个私有方法，用于将文本内容转换为固定维度的向量，以便进行
        相似度搜索。在当前版本中，此方法使用随机向量作为 mock 实现。

        :param text: 需要向量化的文本字符串。
        :return: 一个 numpy 数组，表示文本的向量。
        """
        # 注意: 这是一个 mock 实现，实际应用中需要替换为真实的 Embedding 模型。
        # 例如: return embedding_model.encode(text)
        logging.debug(f"正在为文本生成模拟向量: '{text[:30]}...'")
        return np.random.rand(768).astype(np.float32)

    def save_core_memory(self, name: str, description: str, confidence: int) -> CoreMemory:
        """
        保存一条新的核心层级记忆。

        :param name: 核心记忆名称。
        :param description: 核心记忆的详细描述。
        :param confidence: 该记忆的置信度 (0-100)。
        :return: 返回被创建和保存的 CoreMemory 实例。
        :raises MemoryStatusException: 如果记忆库状态不允许保存操作。
        """
        status = self.db_service.get_status()
        if status in ["OFF", "PAUSED", "MAINTENANCE"]:
            raise MemoryStatusException(f"无法保存记忆：记忆库当前状态为 '{status}'。")

        logging.info(f"准备保存核心记忆: '{name}'")
        embedding = self._vectorize(description)

        memory_instance = CoreMemory(
            name=name,
            description=description,
            embedding=embedding,
            confidence=confidence,
        )

        self.db_service.add(memory_instance)
        logging.info(f"成功保存核心记忆, ID: {memory_instance.id}")
        return memory_instance

    def save_knowledge_memory(self, objective: str, core_id: str, confidence: int) -> KnowledgeMemory:
        """
        保存一条新的知识层级记忆。

        :param objective: 知识记忆的目标描述。
        :param core_id: 所属核心记忆的 ID。
        :param confidence: 该记忆的置信度 (0-100)。
        :return: 返回被创建和保存的 KnowledgeMemory 实例。
        :raises MemoryStatusException: 如果记忆库状态不允许保存操作。
        """
        status = self.db_service.get_status()
        if status in ["OFF", "PAUSED", "MAINTENANCE"]:
            raise MemoryStatusException(f"无法保存记忆：记忆库当前状态为 '{status}'。")

        logging.info(f"准备保存知识记忆: '{objective[:30]}...'")
        embedding = self._vectorize(objective)

        memory_instance = KnowledgeMemory(
            core_id=core_id,
            objective=objective,
            embedding=embedding,
            confidence=confidence,
        )

        self.db_service.add(memory_instance)
        logging.info(f"成功保存知识记忆, ID: {memory_instance.id}")
        return memory_instance

    def save_working_memory(self, details: str, knowledge_id: str, confidence: int) -> WorkingMemory:
        """
        保存一条新的工作层级记忆。

        :param details: 工作记忆的详细信息。
        :param knowledge_id: 所属知识记忆的 ID。
        :param confidence: 该记忆的置信度 (0-100)。
        :return: 返回被创建和保存的 WorkingMemory 实例。
        :raises MemoryStatusException: 如果记忆库状态不允许保存操作。
        """
        status = self.db_service.get_status()
        if status in ["OFF", "PAUSED", "MAINTENANCE"]:
            raise MemoryStatusException(f"无法保存记忆：记忆库当前状态为 '{status}'。")

        logging.info(f"准备保存工作记忆: '{details[:30]}...'")
        embedding = self._vectorize(details)

        memory_instance = WorkingMemory(
            knowledge_id=knowledge_id,
            details=details,
            embedding=embedding,
            confidence=confidence,
        )

        self.db_service.add(memory_instance)
        logging.info(f"成功保存工作记忆, ID: {memory_instance.id}")
        return memory_instance

    def search_memory(
        self,
        query_text: str,
        context: Optional[Dict[str, Any]] = None,
        top_k: int = 5,
        levels: Optional[List[str]] = None
    ) -> list:
        """
        根据查询文本和上下文搜索相关记忆。

        此方法将查询文本向量化，并利用上下文信息构建过滤条件，
        在所有层级的记忆库中进行混合搜索。

        :param query_text: 用于搜索的查询字符串。
        :param context: (可选) 当前的上下文，用于构建预过滤条件。
        :param top_k: 返回的最相关结果数量。
        :param levels: (可选) 一个包含 "Core", "Knowledge", "Working" 的列表，用于限定搜索的表。
                       如果为 None 或为空，则搜索所有层级。
        :return: 一个包含搜索结果（Pydantic 模型实例）的列表。
        :raises MemoryStatusException: 如果记忆库状态不允许搜索操作。
        """
        status = self.db_service.get_status()
        if status in ["OFF", "MAINTENANCE"]:
            raise MemoryStatusException(f"无法搜索记忆：记忆库当前状态为 '{status}'。")

        context = context or {}
        query_vector = self._vectorize(query_text)
        
        # 在这个简化版本中，我们仅在所有表中执行基本的向量搜索，
        # 并未实现文档中描述的复杂预过滤和重排序逻辑。
        
        results = []
        
        # 根据 levels 参数确定要搜索的表
        tables_to_search = []
        level_map = {
            "Core": self.db_service.core_table,
            "Knowledge": self.db_service.knowledge_table,
            "Working": self.db_service.working_table,
        }

        if not levels:
            tables_to_search = list(level_map.values())
            logging.debug("未指定 'levels'，将搜索所有层级的记忆。")
        else:
            for level in levels:
                table = level_map.get(level)
                if table:
                    tables_to_search.append(table)
                else:
                    logging.warning(f"检测到无效的搜索层级: '{level}'，将被忽略。")
        
        # 搜索所有表
        for table in tables_to_search:
            try:
                search_result = table.search(query_vector).limit(top_k).to_pydantic()
                results.extend(search_result)
                logging.debug(f"在表 '{table.name}' 中找到 {len(search_result)} 条结果。")
            except Exception as e:
                logging.warning(f"在表 '{table.name}' 中搜索时出错: {e}")

        # 简单的基于相似度排序 (LanceDB 默认已排序)
        # 在更复杂的实现中，这里应该进行重排序 (re-ranking)
        sorted_results = sorted(results, key=lambda x: x._distance if hasattr(x, '_distance') else float('inf'))
        
        logging.info(f"查询 '{query_text[:30]}...' 完成，共返回 {len(sorted_results[:top_k])} 条结果。")
        return sorted_results[:top_k]
