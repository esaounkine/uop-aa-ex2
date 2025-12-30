import inspect
from typing import Dict

from ..domain import AgentRepository


class AgentTools:
    def __init__(self, repo: AgentRepository, additional_tools: list):
        self.repo = repo
        self.AGENT_TOOLS = [
            self.get_weather_at_location,
        ]
        self.AGENT_TOOLS.extend(additional_tools)

    def get_weather_at_location(self, location: str, **kwargs) -> Dict:
        """Returns metrics for a node."""
        temperature = self.repo.get_weather_at_location(location)

        return {
            # mock data
            "location": location,
            "temperature": temperature,
            "is_raining": temperature > 20
        }

    # TODO: Implement rest of the interafces to expose more tools to the agent

    # Internal

    def get_tool_descriptions(self):
        """
        Reflect into the ENABLED_TOOLS list to generate the list of available tools.
        """
        descriptions = []
        for func in self.AGENT_TOOLS:
            name = func.__name__
            doc = inspect.getdoc(func)
            sig = inspect.signature(func)
            descriptions.append(f"{name}{sig} - {doc}")

        return "\n".join(descriptions)

    def get_tool(self, name: str):
        """
        Helper to match the function to the name.
        """
        return getattr(self, name, None)
