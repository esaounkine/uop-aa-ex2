import json
from typing import Dict


def include_context(prompt: str, context: Dict[str, any]):
    return f"""
        {prompt}
        
        Context:
        {json.dumps(context, indent=2)}
        """


def include_response_format(prompt: str):
    return f"""
        {prompt}
        
        Response Format:
        {{
            "thoughts": "<ideas behind the decision>"
            "action": <tool name>,
            "arguments": {{<tool arguments as dict>}}
        }}
        """


def include_tools(prompt: str, tool_descriptions: str):
    return f"""
        {prompt}
        
        Available Tools:
        {tool_descriptions}
        """
