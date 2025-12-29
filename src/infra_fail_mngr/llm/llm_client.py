from typing import Protocol


class LLMClient(Protocol):
    def generate(self, system_prompt: str) -> str: ...


class LLMClientImpl(LLMClient):
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.response_index = 0

    """
    Simulates the LLM interface, returns pre-defined response at the current index.
    """

    def generate(self, system_prompt):
        if not self.responses or len(self.responses) == 0:
            return ""

        _index = min(self.response_index, len(self.responses) - 1)

        response = self.responses[_index]

        self.response_index += 1

        return response
