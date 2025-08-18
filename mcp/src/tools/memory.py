# -*- coding: utf-8 -*-
"""
@author: lancelrq
@description: 封装对记忆库核心服务的调用，并集成了缓存机制的 MCP 工具。
"""

import logging
from typing import Optional, Dict, Any, List

from src.cache import cached, get_global_cache
from src.memory.engine import IntelligentEngine, MemoryStatusException
from src.memory.models import CoreMemory, KnowledgeMemory, WorkingMemory, BaseMemory

# -- 单例模式实现 --
# 定义一个模块级别的私有变量来存储 IntelligentEngine 的单例实例。
# 这种方式可以确保在整个应用生命周期中，引擎只被实例化一次，
# 从而节省资源并保持状态的一致性。
_engine_instance: Optional[IntelligentEngine] = None


def get_engine() -> IntelligentEngine:
    """
    获取 IntelligentEngine 的单例实例。

    这是一个工厂函数，采用懒加载（Lazy Loading）的方式。
    只有在首次调用时，才会创建 IntelligentEngine 的实例。
    后续所有调用都将返回这个已创建的实例。

    :return: IntelligentEngine 的唯一实例。
    """
    global _engine_instance
    if _engine_instance is None:
        # 在首次调用时，实例化引擎并将其赋值给模块级变量
        _engine_instance = IntelligentEngine()
    return _engine_instance


# -- MCP 工具函数定义 --

def save_core_memory(
    name: str,
    description: str,
    confidence: int = 100
) -> Dict[str, Any]:
    """
    保存一条新的核心层级记忆。

    :param name: 核心记忆名称。
    :param description: 核心记忆的详细描述。
    :param confidence: 记忆的置信度。
    :return: 包含新记忆 ID 和层级的字典。
    """
    engine = get_engine()
    try:
        memory_instance = engine.save_core_memory(
            name=name,
            description=description,
            confidence=confidence
        )
        return {
            "id": memory_instance.id,
            "level": memory_instance.__class__.__name__
        }
    except MemoryStatusException as e:
        logging.warning(f"Memory operation blocked by status check: {e}")
        return {"error": "MemoryOperationBlocked", "message": str(e)}


def save_knowledge_memory(
    objective: str,
    core_id: str,
    confidence: int = 100
) -> Dict[str, Any]:
    """
    保存一条新的知识层级记忆。

    :param objective: 知识记忆的目标描述。
    :param core_id: 关联的核心记忆 ID。
    :param confidence: 记忆的置信度。
    :return: 包含新记忆 ID 和层级的字典。
    """
    engine = get_engine()
    try:
        memory_instance = engine.save_knowledge_memory(
            objective=objective,
            core_id=core_id,
            confidence=confidence
        )
        return {
            "id": memory_instance.id,
            "level": memory_instance.__class__.__name__
        }
    except MemoryStatusException as e:
        logging.warning(f"Memory operation blocked by status check: {e}")
        return {"error": "MemoryOperationBlocked", "message": str(e)}


def save_working_memory(
    details: str,
    knowledge_id: str,
    confidence: int = 100
) -> Dict[str, Any]:
    """
    保存一条新的工作层级记忆。

    :param details: 工作记忆的详细信息。
    :param knowledge_id: 关联的知识记忆 ID。
    :param confidence: 记忆的置信度。
    :return: 包含新记忆 ID 和层级的字典。
    """
    engine = get_engine()
    try:
        memory_instance = engine.save_working_memory(
            details=details,
            knowledge_id=knowledge_id,
            confidence=confidence
        )
        return {
            "id": memory_instance.id,
            "level": memory_instance.__class__.__name__
        }
    except MemoryStatusException as e:
        logging.warning(f"Memory operation blocked by status check: {e}")
        return {"error": "MemoryOperationBlocked", "message": str(e)}


@cached(ttl=3600, key_prefix="memory_search", cache_instance=get_global_cache())
def search_memory(
    query: str,
    context: Optional[Dict[str, Any]] = None,
    top_k: int = 5,
    levels: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    根据查询文本和上下文，从记忆库中检索最相关的记忆。

    此函数利用了 `@cached` 装饰器，将查询结果缓存起来。
    - `ttl=3600`: 缓存有效期为 1 小时。
    - `key_prefix="memory_search"`: 为缓存键添加前缀，避免与其他缓存冲突。
    - `cache_instance=get_global_cache()`: 使用全局共享的缓存实例。

    :param query: 用于搜索的查询字符串。
    :param context: (可选) 当前的上下文，用于辅助过滤和定位相关记忆。
    :param top_k: (可选) 需要返回的最相关结果的数量，默认为 5。
    :param levels: (可选) 指定要搜索的记忆层级列表 (例如 ["Core", "Knowledge", "Working"])。
    :return: 一个包含搜索结果的列表，每个结果都是一个包含记忆信息的字典。
    """
    engine = get_engine()
    try:
        results: List[BaseMemory] = engine.search_memory(
            query_text=query,
            context=context,
            top_k=top_k,
            levels=levels
        )

        # 将 Pydantic 模型转换为字典列表，方便序列化和使用
        output = []
        for res in results:
            item = {
                "id": res.id,
                "level": res.__class__.__name__,
                "content": getattr(res, 'name', getattr(res, 'objective', getattr(res, 'details', ''))),
                "similarity_score": 1 - getattr(res, '_distance', 1.0)  # 假设 _distance 是距离
            }
            output.append(item)
            
        return output
    except MemoryStatusException as e:
        logging.warning(f"Memory operation blocked by status check: {e}")
        return {
            "error": "MemoryOperationBlocked",
            "message": str(e)
        }

VALID_STATUSES = ["ON", "OFF", "PAUSED", "MAINTENANCE"]


def set_memory_status(status: str) -> Dict[str, Any]:
    """
    设置记忆库服务的运行状态。

    此函数用于控制记忆库的全局状态。当状态被设置为非 "ON" 时，
    可能会影响到其他工具函数的正常运行（如 search_memory）。
    状态变更后，会清空所有相关缓存，以确保状态的即时生效。

    :param status: 目标状态，必须是以下之一: "ON", "OFF", "PAUSED", "MAINTENANCE"。
    :return: 一个表示操作成功的字典。
    :raises ValueError: 如果传入了无效的状态字符串。
    """
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Must be one of {VALID_STATUSES}")

    engine = get_engine()
    engine.db_service.set_status(status)

    # 状态变更后，清空所有缓存以确保一致性
    get_global_cache().clear()

    return {"status": "success", "new_status": status}



def get_memory_status() -> Dict[str, Any]:
    """
    获取记忆库服务的当前运行状态。

    :return: 一个包含当前状态的字典, 例如: {"current_status": "ON"}
    """
    engine = get_engine()
    current_status = engine.db_service.get_status()
    return {"current_status": current_status}
