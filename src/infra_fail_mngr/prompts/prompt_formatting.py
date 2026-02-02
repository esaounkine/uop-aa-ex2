import json
from typing import Dict, Any


def include_context(prompt: str, context: Dict[str, Any]) -> str:
    """Include context data in the prompt as formatted JSON.

    Args:
        prompt: The base prompt string.
        context: Dictionary of context data to include.

    Returns:
        The prompt with context appended.
    """
    return f"""
        {prompt}

        Context:
        {json.dumps(context, indent=2)}
        """


def include_response_format(prompt: str) -> str:
    """Include the expected response format in the prompt.

    Args:
        prompt: The base prompt string.

    Returns:
        The prompt with detailed response format and examples appended.
    """
    return f"""
        {prompt}

        Response Format:
        Always respond with valid JSON matching this exact structure:

        {{
            "thoughts": "<string: your reasoning and analysis>",
            "action": "<string: tool name or 'assign_repair_crew'>",
            "arguments": {{<object: parameters for the action>}}
        }}

        Important Notes:
        - "thoughts" must be a non-empty string explaining your decision
        - "action" must be one of the available tools or "assign_repair_crew"
        - "arguments" must be an object with the required parameters for the chosen action
        - Do not include extra fields or deviate from this format

        Examples:

        For gathering information:
        {{
            "thoughts": "Need to check weather conditions before planning repairs",
            "action": "get_weather_at_location",
            "arguments": {{"location": "downtown"}}
        }}

        For making assignments:
        {{
            "thoughts": "All critical information gathered, ready to dispatch crews",
            "action": "assign_repair_crew",
            "arguments": {{"node_ids": ["node1", "node2"], "crew_ids": ["crew1", "crew2"]}}
        }}
        """


def include_tools(prompt: str, tool_descriptions: str) -> str:
    """Include available tools descriptions in the prompt.

    Args:
        prompt: The base prompt string.
        tool_descriptions: String describing available tools.

    Returns:
        The prompt with tools appended.
    """
    return f"""
        {prompt}

        Available Tools:
        {tool_descriptions}
        """
