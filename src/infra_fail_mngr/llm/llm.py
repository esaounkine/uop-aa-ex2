import json

from ..memory import Memory


class MockLLM:
    def __init__(self, responses):
        self.responses = responses

    """
    Simulates the LLM interface, returns pre-defined responses.
    """
    def generate(self, system_prompt, memory: Memory):
        context = memory.get('context', {})

        response = self.responses.get(system_prompt, "no_response_err")

        return json.dumps({
            "response": response,
            "context": context,
        })
