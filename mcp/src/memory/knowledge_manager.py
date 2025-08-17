import uuid


class KnowledgeManager:
    def __init__(self):
        self.knowledge_base = {}

    def save_knowledge(self, content: str, metadata: dict) -> str:
        knowledge_id = str(uuid.uuid4())
        self.knowledge_base[knowledge_id] = {
            "content": content,
            "metadata": metadata,
            "relations": [],
        }
        return knowledge_id

    def search_knowledge(self, query: str, top_k: int = 5) -> list:
        # This is a mock search. A real implementation would use vector search.
        results = []
        for kid, data in self.knowledge_base.items():
            if query in data["content"]:
                results.append({"id": kid, **data})
        return results[:top_k]

    def relate_knowledge(self, source_id: str, target_id: str, relationship: str):
        if source_id in self.knowledge_base and target_id in self.knowledge_base:
            self.knowledge_base[source_id]["relations"].append(
                {"target_id": target_id, "relationship": relationship}
            )
            return True
        return False

    def forget_knowledge(self, knowledge_id: str):
        if knowledge_id in self.knowledge_base:
            del self.knowledge_base[knowledge_id]
            # Also remove relations pointing to this knowledge
            for kid in self.knowledge_base:
                self.knowledge_base[kid]["relations"] = [
                    r
                    for r in self.knowledge_base[kid]["relations"]
                    if r["target_id"] != knowledge_id
                ]
            return True
        return False
