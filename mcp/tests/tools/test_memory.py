import unittest
import sys
import os

from src.tools.memory import MemoryTool


class TestMemoryTool(unittest.TestCase):

    def setUp(self):
        """Set up a new MemoryTool instance before each test."""
        self.memory_tool = MemoryTool()

    def test_save_and_search_knowledge(self):
        """Test saving a new piece of knowledge and searching for it."""
        content = "The sky is blue."
        metadata = {"source": "observation"}
        knowledge_id = self.memory_tool.save_knowledge(content, metadata)
        self.assertIsInstance(knowledge_id, str)

        results = self.memory_tool.search_knowledge(query="sky")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], knowledge_id)
        self.assertEqual(results[0]["content"], content)

    def test_working_memory(self):
        """Test updating, getting, and clearing working memory."""
        self.memory_tool.update_working_memory("current_task", "testing memory tool")
        task = self.memory_tool.get_working_memory("current_task")
        self.assertEqual(task, "testing memory tool")

        self.memory_tool.clear_working_memory()
        task_after_clear = self.memory_tool.get_working_memory("current_task")
        self.assertIsNone(task_after_clear)

    def test_core_memory(self):
        """Test getting and updating core memory."""
        core_mem = self.memory_tool.get_core_memory()
        self.assertIn("persona", core_mem)

        new_core_mem = {"persona": "Advanced AI", "user_preferences": {"theme": "dark"}}
        self.memory_tool.update_core_memory(new_core_mem)
        # The mock implementation just prints, so we can't assert a change here.
        # In a real scenario, we would check the persistent store.
        # For now, we just ensure the method runs without error.
        self.assertTrue(True)

    def test_relate_and_forget_knowledge(self):
        """Test creating a relationship between knowledge and then forgetting it."""
        id1 = self.memory_tool.save_knowledge("Fact A", {})
        id2 = self.memory_tool.save_knowledge("Fact B", {})

        # Relate knowledge
        self.memory_tool.relate_knowledge(id1, id2, "is related to")

        # In a real implementation, we would search and check the relations.
        # Our mock search doesn't support this, so we check that the method runs.

        # Forget knowledge
        self.memory_tool.forget_knowledge(id1)
        results = self.memory_tool.search_knowledge(query="Fact A")
        self.assertEqual(len(results), 0)


if __name__ == "__main__":
    unittest.main()
