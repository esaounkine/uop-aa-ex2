import base64
import json
import zlib
from typing import List, Dict


def step_history_to_flow_diagram(step_history: List[Dict]) -> str:
    """
    Converts the step history to a flow diagram using Mermaid syntax.
    """
    if not step_history:
        return "graph TD\n    Start[No execution history]"

    lines = ["graph TD"]

    states_seen = set()

    for i, step in enumerate(step_history):
        from_state = step['from_state']
        to_state = step['to_state']
        action = step['action']
        data = step.get('data', {})

        if from_state not in states_seen:
            lines.append(f"    {from_state}[{from_state}]")
            states_seen.add(from_state)

        if to_state not in states_seen:
            if to_state == 'FINAL':  # Final state is a round node, that's why it's in `()`
                lines.append(f"    {to_state}([{to_state}])")
            else:
                lines.append(f"    {to_state}[{to_state}]")
            states_seen.add(to_state)

        label = _format_edge_label(action, data)

        lines.append(f"    {from_state} -->|{label}| {to_state}")

    lines.append("")
    lines.append("    classDef finalState fill:#90EE90,stroke:#2E8B57,stroke-width:3px")
    lines.append("    class FINAL finalState")

    return "\n".join(lines)


def _format_edge_label(action: str, data: Dict) -> str:
    action_short = action.replace('llm_decision_', '').replace('_', ' ')

    details = []

    if 'failures' in data and data['failures']:
        failures = data['failures']
        details.append(f"failures: {', '.join(failures)}")

    if 'decision' in data:
        decision = data['decision']
        if 'arguments' in decision:
            args = decision['arguments']
            if 'node_ids' in args:
                nodes = args['node_ids']
                details.append(f"nodes: {', '.join(nodes)}")

    if 'details' in data and isinstance(data['details'], dict):
        assigned = [k for k, v in data['details'].items() if v == 'Assigned']
        if assigned:
            details.append(f"assigned: {', '.join(assigned)}")

    if details:
        return f"{action_short}<br/>{', '.join(details)}"
    else:
        return action_short


def mermaid_to_link(mermaid_code: str) -> str:
    state = {
        # mermaid.live expected structure
        "code": mermaid_code,
        "mermaid": {"theme": "default"},
        "autoSync": True,
        "updateDiagram": True
    }

    json_str = json.dumps(state)

    # compress with zlib (pako is zlib-compatible)
    compressed = zlib.compress(json_str.encode('utf-8'))
    base64_encoded = base64.urlsafe_b64encode(compressed).decode('utf-8')

    return f"https://mermaid.live/edit#pako:{base64_encoded}"

