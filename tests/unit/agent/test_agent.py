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
                assert agent.step_history[-1]["from_state"] == State.INIT.name
                assert agent.step_history[-1]["to_state"] == State.FAILURE_DETECTION.name
                assert agent.step_history[-1]["action"] == "initialize"
                assert agent.step_history[-1]["data"] == {}

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
                    assert agent.step_history[-1]["from_state"] == State.FAILURE_DETECTION.name
                    assert agent.step_history[-1]["to_state"] == State.FINAL.name
                    assert agent.step_history[-1]["action"] == "no_failures_detected"
                    assert agent.step_history[-1]["data"] == {}

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
                    assert agent.step_history[-1]["from_state"] == State.IMPACT_ANALYSIS.name
                    assert agent.step_history[-1]["to_state"] == State.REPAIR_PLANNING.name
                    assert agent.step_history[-1]["action"] == "impact_analyzed"
                    assert agent.step_history[-1]["data"] == {"impact_report": {
                        "node-1": {"population": 100, "criticality": "Low"},
                        "node-2": {"population": 100, "criticality": "Low"}
                    }}

        def describe_when_state_is_repair_planning():
            @pytest.fixture
            def agent_in_repair_planning(agent_base):
                agent_base.state = State.REPAIR_PLANNING
                agent_base.memory = {
                    "failures": ["node-1"],
                    "impact_report": {},
                    "plan_history": []
                }
                return agent_base

            def describe_and_planning_fails_below_max_retries():
                @pytest.fixture
                def agent(agent_in_repair_planning):
                    agent_in_repair_planning.llm_service.handle_request.return_value = "invalid json"
                    agent_in_repair_planning.max_retries = 3
                    agent_in_repair_planning.retry_count = 0
                    return agent_in_repair_planning

                def it_increments_retry_count(agent):
                    agent.run_step()

                    assert agent.retry_count == 1

                def it_stays_in_repair_planning(agent):
                    agent.run_step()

                    assert agent.state == State.REPAIR_PLANNING

            def describe_and_planning_fails_at_max_retries():
                @pytest.fixture
                def agent(agent_in_repair_planning):
                    agent_in_repair_planning.llm_service.handle_request.return_value = "invalid json"
                    agent_in_repair_planning.max_retries = 3
                    agent_in_repair_planning.retry_count = 2
                    return agent_in_repair_planning

                def it_transitions_to_final(agent):
                    agent.run_step()

                    assert agent.state == State.FINAL
                    assert agent.step_history[-1]["from_state"] == State.REPAIR_PLANNING.name
                    assert agent.step_history[-1]["to_state"] == State.FINAL.name
                    assert agent.step_history[-1]["action"] == "max_retries_reached"
                    assert agent.step_history[-1]["data"] == {"retry_count": 3}

                def it_increments_retry_count_first(agent):
                    agent.run_step()

                    assert agent.retry_count == 3

            def describe_and_planning_succeeds_after_retries():
                @pytest.fixture
                def agent(agent_in_repair_planning):
                    agent_in_repair_planning.llm_service.handle_request.return_value = json.dumps({
                        "action": "assign_repair_crew",
                        "arguments": {}
                    })
                    agent_in_repair_planning.retry_count = 2
                    return agent_in_repair_planning

                def it_resets_retry_count(agent):
                    agent.run_step()

                    assert agent.retry_count == 0

                def it_transitions_to_execution(agent):
                    agent.run_step()

                    assert agent.state == State.EXECUTION
                    assert agent.step_history[-1]["from_state"] == State.REPAIR_PLANNING.name
                    assert agent.step_history[-1]["to_state"] == State.EXECUTION.name
                    assert agent.step_history[-1]["action"] == "llm_decision_assign_crew"
                    assert agent.step_history[-1]["data"] == {"decision": {
                        "action": "assign_repair_crew",
                        "arguments": {}
                    }}

        def describe_when_state_is_execution():
            @pytest.fixture
            def agent_in_execution(agent_base):
                agent_base.state = State.EXECUTION
                agent_base.memory = {
                    "pending_action": {
                        "action": "assign_repair_crew",
                        "arguments": {"node_ids": ["node-1"], "crew_ids": ["crew-1"]}
                    },
                    "failures": ["node-1"],
                    "plan_history": []
                }
                return agent_base

            def describe_and_all_assignments_succeed():
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
                    assert agent.step_history[-1]["from_state"] == State.EXECUTION.name
                    assert agent.step_history[-1]["to_state"] == State.RESCHEDULING.name
                    assert agent.step_history[-1]["action"] == "assignments_succeeded"
                    assert agent.step_history[-1]["data"] == {"details": {"node-1": "Assigned"}}

            def describe_and_some_assignments_fail():
                @pytest.fixture
                def agent(agent_in_execution):
                    agent_in_execution.memory["pending_action"]["arguments"] = {
                        "node_ids": ["node-1", "node-2", "node-3"],
                        "crew_ids": ["crew-1", "crew-2", "crew-3"]
                    }
                    agent_in_execution.memory["failures"] = ["node-1", "node-2", "node-3"]
                    agent_in_execution.sys.assign_repair_crew.return_value = {
                        "status": "completed",
                        "details": {
                            "node-1": "Assigned",
                            "node-2": "Failed",
                            "node-3": "Assigned"
                        }
                    }
                    return agent_in_execution

                def it_stores_execution_result(agent):
                    agent.run_step()

                    assert agent.memory["execution_result"]["status"] == "completed"
                    assert agent.memory["execution_result"]["details"]["node-2"] == "Failed"

                def it_updates_failures_to_only_failed_nodes(agent):
                    agent.run_step()

                    assert agent.memory["failures"] == ["node-2"]

                def it_adds_failure_to_plan_history(agent):
                    agent.run_step()

                    assert len(agent.memory["plan_history"]) == 1
                    assert agent.memory["plan_history"][0]["role"] == "execution_result"
                    assert "node-2" in agent.memory["plan_history"][0]["message"]

                def it_transitions_back_to_repair_planning(agent):
                    agent.run_step()

                    assert agent.state == State.REPAIR_PLANNING
                    assert agent.step_history[-1]["from_state"] == State.EXECUTION.name
                    assert agent.step_history[-1]["to_state"] == State.REPAIR_PLANNING.name
                    assert agent.step_history[-1]["action"] == "assignments_failed"
                    assert agent.step_history[-1]["data"] == {
                        "failed_nodes": ["node-2"],
                        "details": {
                            "node-1": "Assigned",
                            "node-2": "Failed",
                            "node-3": "Assigned"
                        }
                    }

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
                    assert agent.step_history[-1]["from_state"] == State.RESCHEDULING.name
                    assert agent.step_history[-1]["to_state"] == State.FINAL.name
                    assert agent.step_history[-1]["action"] == "repairs_completed"
                    assert agent.step_history[-1]["data"] == {}

                def it_calls_detect_failure_nodes(agent):
                    agent.run_step()

                    agent.sys.detect_failure_nodes.assert_called_once()

            def describe_and_cascading_failures():
                @pytest.fixture
                def agent(agent_in_rescheduling):
                    agent_in_rescheduling.sys.detect_failure_nodes.return_value = ["node-4"]
                    return agent_in_rescheduling

                def it_transitions_to_failure_detection(agent):
                    agent.run_step()

                    assert agent.state == State.FAILURE_DETECTION
                    assert agent.step_history[-1]["from_state"] == State.RESCHEDULING.name
                    assert agent.step_history[-1]["to_state"] == State.FAILURE_DETECTION.name
                    assert agent.step_history[-1]["action"] == "cascading_failures"
                    assert agent.step_history[-1]["data"] == {"new_failures": ["node-4"]}

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
                assert agent.step_history[-1]["to_state"] == State.EXECUTION.name
                assert agent.step_history[-1]["action"] == "llm_decision_assign_crew"
                assert agent.step_history[-1]["data"] == {
                    "decision": {
                        "action": "assign_repair_crew",
                        "arguments": {"node_ids": ["node-1"], "crew_ids": ["crew-1"]}
                    }
                }

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

            def it_returns_false(agent):
                result = agent.handle_planning_step()

                assert result is False

            def it_adds_error_to_history(agent):
                agent.handle_planning_step()

                assert len(agent.memory["plan_history"]) == 1
                assert agent.memory["plan_history"][0]["role"] == "error"
                assert "Unknown tool" in agent.memory["plan_history"][0]["message"]

            def it_does_not_transition_state(agent):
                agent.handle_planning_step()

                assert agent.state == State.REPAIR_PLANNING

        def describe_when_llm_returns_invalid_json():
            @pytest.fixture
            def agent(agent_in_repair_planning):
                agent_in_repair_planning.llm_service.handle_request.return_value = "invalid json"
                return agent_in_repair_planning

            def it_returns_false(agent):
                result = agent.handle_planning_step()

                assert result is False

            def it_adds_error_to_history(agent):
                agent.handle_planning_step()

                assert len(agent.memory["plan_history"]) == 1
                assert agent.memory["plan_history"][0]["role"] == "error"
                assert "Invalid JSON" in agent.memory["plan_history"][0]["message"]

            def it_does_not_transition_state(agent):
                agent.handle_planning_step()

                assert agent.state == State.REPAIR_PLANNING

        def describe_when_history_is_empty():
            @pytest.fixture
            def agent(agent_in_repair_planning):
                agent_in_repair_planning.memory["plan_history"] = []
                return agent_in_repair_planning

            def it_passes_empty_history_to_llm(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                assert context["conversation_history"] == []

        def describe_when_history_is_below_limit():
            @pytest.fixture
            def agent(agent_in_repair_planning):
                agent_in_repair_planning.max_history_size = 3
                agent_in_repair_planning.memory["plan_history"] = [
                    {"role": "tool_output", "tool": "tool-1", "result": "result-1"},
                    {"role": "tool_output", "tool": "tool-2", "result": "result-2"},
                ]
                return agent_in_repair_planning

            def it_passes_all_history_to_llm(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                assert len(context["conversation_history"]) == 2

            def it_preserves_history_order(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                assert context["conversation_history"][0]["tool"] == "tool-1"
                assert context["conversation_history"][1]["tool"] == "tool-2"

        def describe_when_history_exceeds_limit():
            @pytest.fixture
            def agent(agent_in_repair_planning):
                agent_in_repair_planning.max_history_size = 3
                agent_in_repair_planning.memory["plan_history"] = [
                    {"role": "tool_output", "tool": "tool-1", "result": "result-1"},
                    {"role": "tool_output", "tool": "tool-2", "result": "result-2"},
                    {"role": "tool_output", "tool": "tool-3", "result": "result-3"},
                    {"role": "tool_output", "tool": "tool-4", "result": "result-4"},
                ]
                return agent_in_repair_planning

            def it_limits_history_to_max_size(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                assert len(context["conversation_history"]) == 3

            def it_keeps_most_recent_entries(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                assert context["conversation_history"][0]["tool"] == "tool-2"
                assert context["conversation_history"][1]["tool"] == "tool-3"
                assert context["conversation_history"][2]["tool"] == "tool-4"

            def it_discards_oldest_entries(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                tools = [entry["tool"] for entry in context["conversation_history"]]
                assert "tool-1" not in tools

        def describe_when_history_equals_limit():
            @pytest.fixture
            def agent(agent_in_repair_planning):
                agent_in_repair_planning.max_history_size = 3
                agent_in_repair_planning.memory["plan_history"] = [
                    {"role": "tool_output", "tool": "tool-1", "result": "result-1"},
                    {"role": "tool_output", "tool": "tool-2", "result": "result-2"},
                    {"role": "tool_output", "tool": "tool-3", "result": "result-3"}
                ]
                return agent_in_repair_planning

            def it_passes_all_history_to_llm(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                assert len(context["conversation_history"]) == 3

            def it_preserves_all_entries(agent):
                agent.handle_planning_step()

                call_args = agent.llm_service.handle_request.call_args
                context = call_args[0][1]
                assert context["conversation_history"][0]["tool"] == "tool-1"
                assert context["conversation_history"][1]["tool"] == "tool-2"
                assert context["conversation_history"][2]["tool"] == "tool-3"

    def describe_get_summary():
        def describe_when_agent_has_history():
            @pytest.fixture
            def agent(agent_base):
                agent_base.memory = {
                    "failures": ["node-1", "node-2"],
                    "execution_result": {"status": "completed"}
                }
                return agent_base

            def it_returns_summary(agent):
                agent._transition_state(State.FAILURE_DETECTION, "initialize", {})
                agent.state = State.FAILURE_DETECTION
                agent._transition_state(State.IMPACT_ANALYSIS, "failures_detected", {})
                agent.state = State.REPAIR_PLANNING
                agent._transition_state(
                    State.REPAIR_PLANNING,
                    "llm_decision_use_tool",
                    {"tool": "tool1", "arguments": {}, "result": {}}
                )

                summary = agent.get_summary()

                assert summary["current_state"] == "REPAIR_PLANNING"
                assert summary["total_steps"] == 3
                assert summary["failures_detected"] == ["node-1", "node-2"]
                assert summary["execution_result"] == {"status": "completed"}

        def describe_when_agent_has_no_history():
            @pytest.fixture
            def agent(agent_base):
                return agent_base

            def it_returns_summary(agent):
                summary = agent.get_summary()

                assert summary["current_state"] == "INIT"
                assert summary["total_steps"] == 0
                assert summary["failures_detected"] == []
                assert summary["execution_result"] is None
