from src.memory.memory_manager import MemoryManager
from src.memory.knowledge_manager import KnowledgeManager
from src.memory.working_manager import WorkingManager


class MemoryTool:
    def __init__(self):
        self.memory_manager = MemoryManager()
        self.knowledge_manager = KnowledgeManager()
        self.working_manager = WorkingManager()

    def save_knowledge(self, content: str, metadata: dict) -> str:
        return self.knowledge_manager.save_knowledge(content, metadata)

    def search_knowledge(self, query: str, top_k: int = 5) -> list:
        return self.knowledge_manager.search_knowledge(query, top_k)

    def update_working_memory(self, key: str, value: any):
        self.working_manager.update_working_memory(key, value)

    def get_working_memory(self, key: str) -> any:
        return self.working_manager.get_working_memory(key)

    def clear_working_memory(self):
        self.working_manager.clear_working_memory()

    def get_core_memory(self) -> dict:
        return self.memory_manager.get_core_memory()

    def update_core_memory(self, new_core_memory: dict):
        self.memory_manager.update_core_memory(new_core_memory)

    def relate_knowledge(self, source_id: str, target_id: str, relationship: str):
        return self.knowledge_manager.relate_knowledge(source_id, target_id, relationship)

    def forget_knowledge(self, knowledge_id: str):
        return self.knowledge_manager.forget_knowledge(knowledge_id)
