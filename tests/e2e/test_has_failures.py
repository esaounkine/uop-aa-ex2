import json

import pytest

from infra_fail_mngr.states import State


def describe_when_there_are_failures():
    @pytest.fixture
    def agent_with_failures(e2e_agent_base, system_repo):
        system_repo.get_failed_nodes.return_value = ["node1"]
        return e2e_agent_base

    def describe_and_llm_responds_with_assign_crew():
        @pytest.fixture
        def agent(agent_with_failures, system_repo):
            agent_with_failures.llm_service.handle_request.return_value = json.dumps({
                "action": "assign_repair_crew",
                "arguments": {"node_ids": ["node1"], "crew_ids": ["crew1"]}
            })
            return agent_with_failures

        def it_reaches_final_state(agent):
            agent.run_to_completion()
            print(agent.step_history)

            assert agent.state == State.FINAL
