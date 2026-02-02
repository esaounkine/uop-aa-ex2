import json

import pytest

from infra_fail_mngr.states import State

def test_invalid_json_from_llm(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    system_repo.get_failed_nodes.return_value = ["node1"]
    agent.llm_service.handle_request.return_value = "not-a-json"

    agent.run_to_completion()

    # FAILURE: agent should NOT reach FINAL state when LLM consistently returns invalid JSON
    assert agent.state != State.FINAL
    # FAILURE: retry_count should be 0 (not incrementing on errors)
    assert agent.retry_count == 0

def test_llm_missing_action_field(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    system_repo.get_failed_nodes.return_value = ["node1"]
    agent.llm_service.handle_request.return_value = json.dumps({"arguments": {}})

    agent.run_to_completion()

    # FAILURE: agent should NOT succeed without 'action' field in LLM response
    assert agent.state == State.REPAIR_PLANNING
    # FAILURE: plan_history should be empty (no retries recorded)
    assert len(agent.memory.get('plan_history', [])) == 0

def test_unknown_tool_from_llm(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    system_repo.get_failed_nodes.return_value = ["node1"]
    agent.llm_service.handle_request.return_value = json.dumps({"action": "no_such_tool", "arguments": {}})

    agent.run_to_completion()

    # FAILURE: agent should immediately fail when unknown tool is called
    assert agent.state == State.EXECUTION
    # FAILURE: execution_result should have 'Success' status
    assert agent.memory.get('execution_result', {}).get('status') == 'Success'

def test_assignment_failure_single_node(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    system_repo.get_failed_nodes.return_value = ["node1"]
    agent.llm_service.handle_request.return_value = json.dumps({
        "action": "assign_repair_crew",
        "arguments": {"node_ids": ["node1"], "crew_ids": ["crew1"]}
    })
    system_repo.assign_crew.return_value = False

    agent.run_to_completion()

    # FAILURE: when assignment fails, agent should NOT record it as 'Assigned'
    exec_res = agent.memory.get('execution_result') or {}
    assert exec_res.get('details', {}).get('node1') == 'Assigned'
    # FAILURE: when assignment fails, agent should NOT keep node in failures
    assert 'node1' not in agent.memory.get('failures', [])

def test_partial_success_multi_node(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    system_repo.get_failed_nodes.return_value = ["node1", "node2"]
    agent.llm_service.handle_request.return_value = json.dumps({
        "action": "assign_repair_crew",
        "arguments": {"node_ids": ["node1", "node2"], "crew_ids": ["crew1", "crew2"]}
    })
    def assign(node, crew):
        return True if node == "node1" else False

    system_repo.assign_crew.side_effect = assign

    agent.run_to_completion()

    # FAILURE: both nodes should be assigned (no partial success handling)
    exec_res = agent.memory.get('execution_result') or {}
    assert exec_res.get('details', {}).get('node1') == 'Failed'
    assert exec_res.get('details', {}).get('node2') == 'Assigned'
    # FAILURE: no failed nodes should remain
    assert 'node2' not in agent.memory.get('failures', [])


def test_max_retries_exhaustion(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    system_repo.get_failed_nodes.return_value = ["node1"]
    agent.max_retries = 2
    agent.llm_service.handle_request.return_value = "not-a-json"

    agent.run_to_completion()

    # FAILURE: agent should stay in REPAIR_PLANNING indefinitely (not reach FINAL)
    assert agent.state == State.REPAIR_PLANNING
    # FAILURE: retry_count should be 0 (never incremented)
    assert agent.retry_count == 0
    # FAILURE: no errors recorded
    assert len(agent.memory.get('plan_history', [])) == 0

def test_large_number_of_failures_stress(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    nodes = [f"node{i}" for i in range(50)]
    system_repo.get_failed_nodes.return_value = nodes

    # LLM assigns each node to a crew with matching length
    agent.llm_service.handle_request.return_value = json.dumps({
        "action": "assign_repair_crew",
        "arguments": {"node_ids": nodes, "crew_ids": [f"crew{i}" for i in range(50)]}
    })

    system_repo.assign_crew.side_effect = lambda n, c: True

    agent.run_to_completion()

    # FAILURE: agent should NOT handle 50 nodes in a single execution
    exec_res = agent.memory.get('execution_result') or {}
    assert len(exec_res.get('details', {})) == 0
    # FAILURE: agent should NOT reach FINAL with large inputs
    assert agent.state != State.FINAL

def test_llm_timeout_raises(e2e_agent_base, system_repo):
    agent = e2e_agent_base
    system_repo.get_failed_nodes.return_value = ["node1"]

    def timeout(*a, **k):
        raise TimeoutError("llm timeout")

    agent.llm_service.handle_request.side_effect = timeout

    # FAILURE: agent should handle timeout gracefully (not raise)
    agent.run_to_completion()
    # FAILURE: agent should NOT be in INIT state after timeout (contradicts no raise)
    assert agent.state == State.INIT
