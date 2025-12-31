import pytest

from infra_fail_mngr.agent import InfraAgent
from infra_fail_mngr.tools import SystemTools, AgentTools


@pytest.fixture
def system_repo(mocker):
    system_repo = mocker.Mock()
    system_repo.get_failed_nodes.return_value = []
    return system_repo

@pytest.fixture
def agent_repo(mocker):
    agent_repo = mocker.Mock()
    agent_repo.get_available_crews.return_value = ["crew1", "crew2"]
    return agent_repo

@pytest.fixture
def system_tools(system_repo):
    return SystemTools(system_repo)

@pytest.fixture
def agent_tools(agent_repo, system_tools):
    return AgentTools(agent_repo, [
        system_tools.assign_repair_crew
    ])

@pytest.fixture
def e2e_agent_base(system_tools, agent_tools, mocker):
    llm_service = mocker.Mock()
    return InfraAgent(llm_service, system_tools, agent_tools)