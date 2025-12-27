import inspect

from .tools import estimate_impact, assign_repair_crew, detect_failure_nodes

"""
This module is an abstraction layer to declaratively define the tools available to the orchestrator agent.
It relies on the `tools` module to register the available tools.
"""

ENABLED_TOOLS = [
    assign_repair_crew,
    detect_failure_nodes,
    estimate_impact,
]


def get_tool_descriptions():
    """
    Reflect into the ENABLED_TOOLS list to generate the list of available tools.
    """
    descriptions = []
    for func in ENABLED_TOOLS:
        name = func.__name__
        doc = inspect.getdoc(func)
        sig = inspect.signature(func)
        descriptions.append(f"{name}{sig} - {doc}")

    return "\n".join(descriptions)


def get_tool_by_name(name: str):
    """
    Helper for the Dispatcher to match the function to the name.
    """
    return next((t for t in ENABLED_TOOLS if t.__name__ == name), None)
