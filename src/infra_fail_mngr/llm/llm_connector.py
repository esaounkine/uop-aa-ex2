import json

from src.infra_fail_mngr.memory import Memory


class LLMConnector:
    def __init__(self, llm_model):
        self.model = llm_model

    def generate(self, system_prompt, memory: Memory):
        res_str = self.model.generate(system_prompt, memory)

        print(f"Raw LLM response: {res_str}")

        res_json = json.loads(res_str)

        print(f"Parsed LLM response: {res_json}")

        return res_json
