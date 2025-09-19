"""
LazyAI 知识库模块
支持分层知识库管理、多种数据源、向量搜索等功能
"""

from .core.service import KnowledgeBaseService
from .core.hierarchical_service import HierarchicalKnowledgeBaseService
from .core.vector_interface import VectorDatabaseInterface, VectorDatabaseFactory
from .models.base import *

__version__ = "1.0.0"
__all__ = [
    "KnowledgeBaseService",
    "HierarchicalKnowledgeBaseService",
    "VectorDatabaseInterface",
    "VectorDatabaseFactory"
]