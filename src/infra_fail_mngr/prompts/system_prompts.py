import json
from typing import Dict


def get_system_prompt(tool_descriptions: str, context: Dict[str, any]):
    return f"""
        You are an Infrastructure crisis manager.
        Tools Available:
        {tool_descriptions}
        
        Context:
        {json.dumps(context, indent=2)}
        
        Response format:
        {{
            "thoughts": "string", # ideas behind the decision
            "action": "string", # function name of one of the tools available
            "arguments": {{
                # arguments for the function
                "node_ids": ["node1", "node2"],
                "crew_ids": ["crew1", "crew2"]
            }}
        }}
        
        Decide the next step. 
        - If you need information (e.g. Weather), call that tool.
        - If you are ready to fix, call 'assign_repair_crew'.
        """
