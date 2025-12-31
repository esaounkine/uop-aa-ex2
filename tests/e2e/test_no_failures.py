import pytest

from infra_fail_mngr.states import State


@pytest.fixture
def agent(e2e_agent_base, system_repo):
    system_repo.get_failed_nodes.return_value = []
    return e2e_agent_base

def it_reaches_final_state(agent):
    agent.run_to_completion()

    assert agent.state == State.FINAL
