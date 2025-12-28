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
        response = self.responses[self.response_index]

        self.response_index += 1

        return response

    def set_responses(self, responses):
        self.responses = responses
