class Memory:
    """
    This class manages the memory of the orchestrator agent.
    """
    def __init__(self):
        self.data = {}

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

    def update(self, key, value):
        self.data[key].update(value)

    def clear(self):
        self.data = {}
