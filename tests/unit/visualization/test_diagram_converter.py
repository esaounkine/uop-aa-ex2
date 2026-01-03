import pytest

from src.infra_fail_mngr.vis.diagram_converter import (
    step_history_to_flow_diagram,
    mermaid_to_link,
)


def describe_step_history_to_flow_diagram():
    def when_history_has_steps():
        @pytest.fixture
        def history():
            return [
                {'from_state': 'INIT', 'to_state': 'FAILURE_DETECTION', 'action': 'initialize', 'data': {}}
            ]

        def it_returns_string(history):
            result = step_history_to_flow_diagram(history)

            assert isinstance(result, str)

        def it_starts_with_graph_declaration(history):
            result = step_history_to_flow_diagram(history)

            assert result.startswith("graph TD")

        def it_includes_state_nodes(history):
            result = step_history_to_flow_diagram(history)

            assert "INIT[INIT]" in result
            assert "FAILURE_DETECTION[FAILURE_DETECTION]" in result

        def it_includes_transition_arrow(history):
            result = step_history_to_flow_diagram(history)

            assert "INIT -->|initialize| FAILURE_DETECTION" in result

        def it_styles_final_state_differently(history):
            result = step_history_to_flow_diagram(history)

            assert "FINAL([FINAL])" in result
            assert "classDef finalState" in result

    def when_history_has_failure_data():
        @pytest.fixture
        def history():
            return [
                {
                    'from_state': 'FAILURE_DETECTION',
                    'to_state': 'IMPACT_ANALYSIS',
                    'action': 'failures_detected',
                    'data': {'failures': ['node1', 'node2']}
                }
            ]

        def it_includes_data_in_label(history):
            result = step_history_to_flow_diagram(history)

            assert "failures: node1, node2" in result

    def when_history_has_decision():
        @pytest.fixture
        def history():
            return [
                {
                    'from_state': 'REPAIR_PLANNING',
                    'to_state': 'EXECUTION',
                    'action': 'llm_decision_assign_crew',
                    'data': {
                        'decision': {
                            'action': 'assign_repair_crew',
                            'arguments': {'node_ids': ['node1']}
                        }
                    }
                }
            ]

        def it_includes_data_in_label(history):
            result = step_history_to_flow_diagram(history)

            assert "nodes: node1" in result

    def when_history_has_multiple_steps():
        @pytest.fixture
        def history():
            return [
                {'from_state': 'INIT', 'to_state': 'FAILURE_DETECTION', 'action': 'initialize', 'data': {}},
                {'from_state': 'FAILURE_DETECTION', 'to_state': 'IMPACT_ANALYSIS', 'action': 'failures_detected',
                 'data': {}},
                {'from_state': 'IMPACT_ANALYSIS', 'to_state': 'FINAL', 'action': 'complete', 'data': {}}
            ]

        def it_returns_multiple_transitions(history):
            result = step_history_to_flow_diagram(history)

            assert "INIT -->|initialize| FAILURE_DETECTION" in result
            assert "FAILURE_DETECTION -->|failures detected| IMPACT_ANALYSIS" in result
            assert "IMPACT_ANALYSIS -->|complete| FINAL" in result

    def when_history_has_loop():
        @pytest.fixture
        def history():
            return [
                {'from_state': 'INIT', 'to_state': 'FAILURE_DETECTION', 'action': 'action1', 'data': {}},
                {'from_state': 'FAILURE_DETECTION', 'to_state': 'INIT', 'action': 'action2', 'data': {}}
            ]

        def it_returns_single_state_definitions(history):
            result = step_history_to_flow_diagram(history)

            assert result.count("INIT[INIT]") == 1
            assert result.count("FAILURE_DETECTION[FAILURE_DETECTION]") == 1

    def when_history_is_empty():
        @pytest.fixture
        def history():
            return []

        def it_returns_empty_graph(history):
            result = step_history_to_flow_diagram(history)

            assert "No execution history" in result


def describe_mermaid_to_link():
    def it_returns_string():
        mermaid_code = "graph TD\n    A --> B"

        result = mermaid_to_link(mermaid_code)

        assert isinstance(result, str)

    def it_starts_with_mermaid_live_url():
        mermaid_code = "graph TD\n    A --> B"

        result = mermaid_to_link(mermaid_code)

        assert result.startswith("https://mermaid.live/edit#pako:")

    def it_includes_base64_encoded_content():
        mermaid_code = "graph TD\n    A --> B"

        result = mermaid_to_link(mermaid_code)

        base64_part = result.split("#pako:")[1]
        # not validating the whole thing, just checking length is above zero
        assert len(base64_part) > 0

    def it_handles_empty_mermaid_code():
        result = mermaid_to_link("")

        assert result.startswith("https://mermaid.live/edit#pako:")
