class WorkingManager:
    def __init__(self):
        self.working_memory = {}

    def update_working_memory(self, key: str, value: any):
        self.working_memory[key] = value

    def get_working_memory(self, key: str) -> any:
        return self.working_memory.get(key)

    def clear_working_memory(self):
        self.working_memory.clear()
