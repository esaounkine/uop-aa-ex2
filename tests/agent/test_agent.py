import json

import pytest

from src.infra_fail_mngr.agent.agent import InfraAgent
from src.infra_fail_mngr.states import State


@pytest.fixture
def agent_base(mocker):
    llm_service = mocker.Mock()
    system_tools = mocker.Mock()
    agent_tools = mocker.Mock()
    agent_tools.get_tool_descriptions.return_value = "tools"
    return InfraAgent(llm_service, system_tools, agent_tools)


@pytest.mark.unit
def describe_infra_agent():
    def describe_run_step():
        def describe_when_state_is_init():
            @pytest.fixture
            def agent(agent_base):
                return agent_base

            def it_sets_memory_to_empty_lists(agent):
                agent.run_step()

                assert agent.memory["failures"] == []
                assert agent.memory["impact_report"] == {}
                assert agent.memory["plan_history"] == []

            def it_transitions_to_failure_detection(agent):
                agent.run_step()

                assert agent.state == State.FAILURE_DETECTION

        def describe_when_state_is_failure_detection():
            @pytest.fixture
            def agent_in_failure_detection(agent_base):
                agent_base.state = State.FAILURE_DETECTION
                agent_base.memory = {"failures": []}
                return agent_base

            def describe_and_no_failures():
                @pytest.fixture
                def agent(agent_in_failure_detection):
                    agent_in_failure_detection.sys.detect_failure_nodes.return_value = []
                    return agent_in_failure_detection

                def it_transitions_to_final(agent):
                    agent.run_step()

                    assert agent.state == State.FINAL

                def it_calls_detect_failure_nodes(agent):
                    agent.run_step()

                    agent.sys.detect_failure_nodes.assert_called_once()

            def describe_and_has_failures():
                @pytest.fixture
                def agent(agent_in_failure_detection):
                    agent_in_failure_detection.sys.detect_failure_nodes.return_value = ["node-1", "node-2", "node-3"]
                    return agent_in_failure_detection

                def it_stores_all_failures(agent):
                    agent.run_step()

                    assert agent.memory["failures"] == ["node-1", "node-2", "node-3"]

        def describe_when_state_is_impact_analysis():
            @pytest.fixture
            def agent_in_impact_analysis(agent_base):
                agent_base.state = State.IMPACT_ANALYSIS
                agent_base.memory = {"impact_report": {}, "failures": ["node-1", "node-2"]}
                return agent_base

            def describe_and_estimates_impact_low():
                @pytest.fixture
                def agent(agent_in_impact_analysis):
                    agent_in_impact_analysis.sys.estimate_impact.return_value = {
                        "population": 100,
                        "criticality": "Low"
                    }
                    return agent_in_impact_analysis

                def it_estimates_impact_for_each_failure(agent):
                    agent.run_step()

                    assert agent.sys.estimate_impact.call_count == 2
                    agent.sys.estimate_impact.assert_any_call(node_id="node-1")
                    agent.sys.estimate_impact.assert_any_call(node_id="node-2")

                def it_stores_impact_report_in_memory(agent):
                    agent.run_step()

                    assert "node-1" in agent.memory["impact_report"]
                    assert "node-2" in agent.memory["impact_report"]

                def it_transitions_to_repair_planning(agent):
                    agent.run_step()

                    assert agent.state == State.REPAIR_PLANNING

        def describe_when_state_is_execution():
            @pytest.fixture
            def agent_in_execution(agent_base):
                agent_base.state = State.EXECUTION
                agent_base.memory = {
                    "pending_action": {
                        "action": "assign_repair_crew",
                        "arguments": {"node_ids": ["node-1"], "crew_ids": ["crew-1"]}
                    }
                }
                return agent_base

            def describe_and_assignment_completes():
                @pytest.fixture
                def agent(agent_in_execution):
                    agent_in_execution.sys.assign_repair_crew.return_value = {
                        "status": "completed",
                        "details": {"node-1": "Assigned"}
                    }
                    return agent_in_execution

                def it_calls_assign_repair_crew_with_args(agent):
                    agent.run_step()

                    agent.sys.assign_repair_crew.assert_called_once_with(
                        node_ids=["node-1"], crew_ids=["crew-1"]
                    )

                def it_stores_execution_result(agent):
                    agent.run_step()

                    assert agent.memory["execution_result"] == {
                        "status": "completed",
                        "details": {"node-1": "Assigned"}
                    }

                def it_transitions_to_rescheduling(agent):
                    agent.run_step()

                    assert agent.state == State.RESCHEDULING

        def describe_when_state_is_rescheduling():
            @pytest.fixture
            def agent_in_rescheduling(agent_base):
                agent_base.state = State.RESCHEDULING
                agent_base.memory = {}
                return agent_base

            def describe_and_no_new_failures():
                @pytest.fixture
                def agent(agent_in_rescheduling):
                    agent_in_rescheduling.sys.detect_failure_nodes.return_value = []
                    return agent_in_rescheduling

                def it_transitions_to_final(agent):
                    agent.run_step()

                    assert agent.state == State.FINAL

                def it_calls_detect_failure_nodes(agent):
                    agent.run_step()

                    agent.sys.detect_failure_nodes.assert_called_once()

            def describe_and_cascading_failures():
                @pytest.fixture
                def agent(agent_base):
                    agent_base.sys.detect_failure_nodes.return_value = ["node-3"]
                    return agent_base

                def it_transitions_to_failure_detection(agent):
                    agent.run_step()

                    assert agent.state == State.FAILURE_DETECTION

    def describe_run_to_completion():
        def describe_when_no_failures():
            @pytest.fixture
            def agent(agent_base):
                agent_base.sys.detect_failure_nodes.return_value = []
                return agent_base

            def it_reaches_final_state(agent):
                agent.run_to_completion()

                assert agent.state == State.FINAL

            def it_runs_limited_steps(agent, mocker):
                spy = mocker.spy(agent, 'run_step')

                agent.run_to_completion()

                assert spy.call_count <= agent.max_steps

        def describe_when_max_steps_reached():
            @pytest.fixture
            def agent(agent_base):
                agent_base.sys.detect_failure_nodes.return_value = ["node-1"]
                agent_base.max_steps = 2
                return agent_base

            def it_stops_after_max_steps(agent, mocker):
                spy = mocker.spy(agent, 'run_step')

                agent.run_to_completion()

                assert spy.call_count == 2

    def describe_handle_planning_step():
        @pytest.fixture
        def agent_in_repair_planning(agent_base):
            agent_base.state = State.REPAIR_PLANNING
            agent_base.memory = {
                "failures": ["node-1"],
                "impact_report": {"node-1": {"criticality": "High"}},
                "plan_history": []
            }
            return agent_base

        def describe_when_llm_returns_assign_crew():
            @pytest.fixture
            def agent(agent_in_repair_planning):
                agent_in_repair_planning.llm_service.handle_request.return_value = json.dumps({
                    "action": "assign_repair_crew",
                    "arguments": {"node_ids": ["node-1"], "crew_ids": ["crew-1"]}
                })
                return agent_in_repair_planning

            def it_stores_pending_action(agent):
                agent.handle_planning_step()

                assert "pending_action" in agent.memory
                assert agent.memory["pending_action"]["action"] == "assign_repair_crew"

            def it_transitions_to_execution(agent):
                agent.handle_planning_step()

                assert agent.state == State.EXECUTION

            def it_calls_llm_service(agent):
                agent.handle_planning_step()

                agent.llm_service.handle_request.assert_called_once()

        def describe_when_llm_returns_other_tool():
            @pytest.fixture
            def agent(agent_in_repair_planning, mocker):
                agent_in_repair_planning.llm_service.handle_request.return_value = json.dumps({
                    "action": "tool-1",
                    "arguments": {"arg-1": "value-1"}
                })
                tool_func = mocker.Mock(return_value={"result": "data-1"})
                agent_in_repair_planning.tools.get_tool.return_value = tool_func
                return agent_in_repair_planning

            def it_calls_tool_function(agent):
                agent.handle_planning_step()

                tool_func = agent.tools.get_tool.return_value
                tool_func.assert_called_once_with(**{"arg-1": "value-1"})

            def it_adds_result_to_history(agent):
                agent.handle_planning_step()

                assert len(agent.memory["plan_history"]) == 1
                assert agent.memory["plan_history"][0]["role"] == "tool_output"
                assert agent.memory["plan_history"][0]["tool"] == "tool-1"

            def it_does_not_transition_state(agent):
                agent.handle_planning_step()

                assert agent.state == State.REPAIR_PLANNING

        def describe_when_llm_returns_unknown_tool():
            @pytest.fixture
            def agent(agent_in_repair_planning, mocker):
                agent_in_repair_planning.llm_service.handle_request.return_value = json.dumps({
                    "action": "unknown-tool",
                    "arguments": {}
                })
                agent_in_repair_planning.tools.get_tool.return_value = None
                return agent_in_repair_planning

            def it_does_not_add_to_history(agent):
                agent.handle_planning_step()

                assert len(agent.memory["plan_history"]) == 0

            def it_does_not_transition_state(agent):
                agent.handle_planning_step()

                assert agent.state == State.REPAIR_PLANNING

        def describe_when_llm_returns_invalid_json():
            @pytest.fixture
            def agent(agent_in_repair_planning):
                agent_in_repair_planning.llm_service.handle_request.return_value = "invalid json"
                return agent_in_repair_planning

            def it_does_not_transition_state(agent):
                agent.handle_planning_step()

                assert agent.state == State.REPAIR_PLANNING
