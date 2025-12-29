from .agent import InfraAgent
from .domain import SystemRepository, AgentRepository
from .llm import LLMServiceImpl, LLMClientImpl
from .tools import SystemTools, AgentTools

class InlineSystemRepo(SystemRepository):
    def get_failed_nodes(self):
        return ["node1", "node2"]

    def get_node_details(self, node_id):
        return {"critical": True}

    def assign_crew(self, node_id, crew_id):
        return True

class InlineAgentRepo(AgentRepository):
    def get_available_crews(self):
        return ["crew1", "crew2"]

    def get_weather_at_location(self, location):
        return 25

    def estimate_repair_time(self, node_id, crew_id):
        return 60

    def estimate_arrival_time(self, node_id, crew_id):
        return 30

    def get_crew_location(self, crew_id):
        return "location1"

    def get_crew_remaining_capacity(self, crew_id):
        return 10

def wire() -> InfraAgent:
    llm_client = LLMClientImpl([])
    llm_service = LLMServiceImpl(llm_client)

    system_repo: SystemRepository = InlineSystemRepo()
    system_tools = SystemTools(system_repo)

    agent_repo: AgentRepository = InlineAgentRepo()
    agent_tools = AgentTools(agent_repo)

    return InfraAgent(llm_service, system_tools, agent_tools)
