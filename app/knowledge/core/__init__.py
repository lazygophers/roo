"""
知识库核心服务模块
"""

from .service import KnowledgeBaseService, init_knowledge_base_service, get_knowledge_base_service
from .hierarchical_service import HierarchicalKnowledgeBaseService, init_hierarchical_knowledge_base_service, get_hierarchical_knowledge_base_service
from .vector_interface import VectorDatabaseInterface, VectorDatabaseFactory

__all__ = [
    "KnowledgeBaseService",
    "init_knowledge_base_service",
    "get_knowledge_base_service",
    "HierarchicalKnowledgeBaseService",
    "init_hierarchical_knowledge_base_service",
    "get_hierarchical_knowledge_base_service",
    "VectorDatabaseInterface",
    "VectorDatabaseFactory"
]