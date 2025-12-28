import json
from typing import Dict, Protocol

from .llm_client import LLMClient
from ..prompts.prompt_formatting import include_context, include_response_format, include_tools


class LLMService(Protocol):
    def handle_request(self, system_prompt: str, user_context: Dict, tool_descriptions: str) -> str: ...


class LLMServiceImpl(LLMService):
    def __init__(self, llm_client: LLMClient):
        self.client = llm_client

    def handle_request(self, system_prompt: str, context: Dict, tool_descriptions: str):
        _prompt = include_tools(
            include_response_format(
                include_context(
                    system_prompt, context
                )
            ),
            tool_descriptions
        )

        res_str = self.client.generate(_prompt)

        print(f"Raw LLM response: {res_str}")

        res_json = json.loads(res_str)

        print(f"Parsed LLM response: {res_json}")

        return res_json
