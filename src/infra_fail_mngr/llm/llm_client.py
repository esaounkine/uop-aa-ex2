from typing import Protocol
import json
import sys


class LLMClient(Protocol):
    """Protocol for LLM client interfaces."""

    def generate(self, system_prompt: str) -> str:
        """Generate a response based on the system prompt.

        Args:
            system_prompt: The formatted prompt to send to the LLM.

        Returns:
            The raw response string from the LLM.
        """
        ...


class LLMClientImpl(LLMClient):
    """Mock implementation of LLMClient that returns predefined responses."""

    def __init__(self, responses: list[str]):
        """Initialize with a list of predefined responses.

        Args:
            responses: List of JSON strings to return in sequence.
        """
        self.responses = responses
        self.response_index = 0
        self.is_test_mode = 'pytest' in sys.modules or 'unittest' in sys.modules

    def generate(self, system_prompt: str) -> str:
        """Return the next predefined response.

        Args:
            system_prompt: Ignored in mock implementation.

        Returns:
            The next response string, or empty string if no more responses.
        """
        # Αν τρέχουμε tests και η λίστα είναι κενή, επέστρεψε κενή συμβολοσειρά
        if self.is_test_mode and (not self.responses or len(self.responses) == 0):
            return ""

        # Αν ΔΕΝ τρέχουμε tests και η λίστα είναι κενή, δημιούργησε default response
        if not self.is_test_mode and (not self.responses or len(self.responses) == 0):
            if self.response_index == 0:
                self.response_index += 1
                return json.dumps({
                    "thoughts": "Checking available crews",
                    "action": "get_available_crews",
                    "arguments": {}
                })
            elif self.response_index == 1:
                self.response_index += 1
                return json.dumps({
                    "thoughts": "Ready to dispatch repair crews",
                    "action": "assign_repair_crew",
                    "arguments": {
                        "node_ids": ["node1", "node2"],
                        "crew_ids": ["crew1", "crew2"]
                    }
                })
            else:
                return json.dumps({
                    "thoughts": "Default assignment",
                    "action": "assign_repair_crew",
                    "arguments": {
                        "node_ids": ["node1", "node2"],
                        "crew_ids": ["crew1", "crew2"]
                    }
                })

        
        if self.responses and len(self.responses) > 0:
            _index = min(self.response_index, len(self.responses) - 1)
            response = self.responses[_index]
            self.response_index += 1
            return response
        
        return ""
