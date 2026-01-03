import pytest

from infra_fail_mngr.states import State



def describe_when_no_failures():
    @pytest.fixture
    def agent_no_failures(e2e_agent_base, system_repo):
        system_repo.get_failed_nodes.return_value = []
        return e2e_agent_base

    def it_reaches_final_state(agent_no_failures):
        agent_no_failures.run_to_completion()

        assert agent_no_failures.state == State.FINAL
