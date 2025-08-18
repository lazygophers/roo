import pytest
import numpy as np
from unittest.mock import MagicMock, patch

from src.tools import memory as memory_tools
from src.memory.models import CoreMemory, KnowledgeMemory, WorkingMemory


@pytest.fixture
def mock_engine_instance():
    """
    提供一个配置好的 IntelligentEngine 模拟实例。
    """
    engine_instance = MagicMock()
    
    mock_embedding = np.random.rand(768).astype(np.float32)
    
    engine_instance.save_core_memory.return_value = CoreMemory(id="core-123", name="Test Core", description="Test Desc", embedding=mock_embedding)
    engine_instance.save_knowledge_memory.return_value = KnowledgeMemory(id="knowledge-456", core_id="core-123", objective="Test Knowledge", embedding=mock_embedding)
    engine_instance.save_working_memory.return_value = WorkingMemory(id="work-789", knowledge_id="knowledge-456", details="Test Details", embedding=mock_embedding)
    
    mock_search_result = [
        KnowledgeMemory(id="res-1", core_id="core-123", objective="Relevant knowledge", embedding=mock_embedding, _distance=0.1)
    ]
    engine_instance.search_memory.return_value = mock_search_result
    
    engine_instance.db_service.get_status.return_value = "ON"
    
    return engine_instance


@pytest.fixture(autouse=True)
def patch_get_engine(mock_engine_instance):
    """
    自动应用的 Fixture，用模拟实例 patch get_engine 函数。
    """
    with patch('src.tools.memory.get_engine', return_value=mock_engine_instance) as mock_get_engine:
        yield mock_get_engine


def test_save_core_memory(mock_engine_instance):
    """
    测试保存核心记忆。
    """
    result = memory_tools.save_core_memory(name="Test Project", description="A test project.", confidence=95)
    
    mock_engine_instance.save_core_memory.assert_called_once_with(name="Test Project", description="A test project.", confidence=95)
    
    assert result["id"] == "core-123"
    assert result["level"] == "CoreMemory"


def test_save_knowledge_memory(mock_engine_instance):
    """
    测试保存知识记忆。
    """
    result = memory_tools.save_knowledge_memory(objective="Test objective", core_id="core-123", confidence=90)
    
    mock_engine_instance.save_knowledge_memory.assert_called_once_with(objective="Test objective", core_id="core-123", confidence=90)
    
    assert result["id"] == "knowledge-456"
    assert result["level"] == "KnowledgeMemory"


def test_save_working_memory(mock_engine_instance):
    """
    测试保存工作记忆。
    """
    result = memory_tools.save_working_memory(details="Detailed step-by-step instructions.", knowledge_id="knowledge-456", confidence=99)
    
    mock_engine_instance.save_working_memory.assert_called_once_with(details="Detailed step-by-step instructions.", knowledge_id="knowledge-456", confidence=99)
    
    assert result["id"] == "work-789"
    assert result["level"] == "WorkingMemory"


def test_search_memory(mock_engine_instance):
    """
    测试搜索记忆功能。
    """
    results = memory_tools.search_memory(query="relevant", top_k=1, levels=["KnowledgeMemory"])
    
    mock_engine_instance.search_memory.assert_called_once_with(
        query_text="relevant",
        context=None,
        top_k=1,
        levels=["KnowledgeMemory"]
    )
    
    assert len(results) == 1
    assert results["id"] == "res-1"
    assert results["content"] == "Relevant knowledge"
    assert results["similarity_score"] > 0.89


def test_set_and_get_memory_status(mock_engine_instance):
    """
    测试设置和获取记忆库状态。
    """
    status_result = memory_tools.get_memory_status()
    assert status_result["current_status"] == "ON"
    mock_engine_instance.db_service.get_status.assert_called_once()
    
    memory_tools.set_memory_status("PAUSED")
    mock_engine_instance.db_service.set_status.assert_called_once_with("PAUSED")
