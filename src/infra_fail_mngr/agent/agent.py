import json

from ..domain import LLMService
from ..prompts.system_prompts import get_system_prompt
from ..states import State
from ..tools import SystemTools, AgentTools


class InfraAgent:
    def __init__(self, llm: LLMService, system_tools: SystemTools, agent_tools: AgentTools):
        self.llm = llm
        self.sys = system_tools
        self.tools = agent_tools
        self.max_steps = 10
        self.tool_descriptions = self.tools.get_tool_descriptions()

        self.state = State.INIT
        self.memory = {}

    def run_step(self):
        print(f"--- STATE: {self.state.name} ---")

        if self.state == State.INIT:
            self.memory = {
                "failures": [],
                "impact_report": {},
                "plan_history": []
            }
            self.state = State.FAILURE_DETECTION
            return

        elif self.state == State.FAILURE_DETECTION:
            failures = self.sys.detect_failure_nodes()

            if not failures:
                print("[SYSTEM] No failures detected. System Healthy.")
                self.state = State.FINAL
            else:
                self.memory['failures'] = failures
                print(f"[SYSTEM] Detected: {failures}")
                self.state = State.IMPACT_ANALYSIS
            return

        elif self.state == State.IMPACT_ANALYSIS:
            report = {}
            for node in self.memory['failures']:
                report[node] = self.sys.estimate_impact(node_id=node)

            self.memory['impact_report'] = report
            self.state = State.REPAIR_PLANNING
            return

        elif self.state == State.REPAIR_PLANNING:
            self._handle_planning_step()
            return

        elif self.state == State.EXECUTION:
            pending = self.memory.get('pending_action', {})
            args = pending.get('arguments', {})

            print(f"[EXECUTION] Dispatching Crews: {args}")
            result = self.sys.assign_repair_crew(**args)

            self.memory['execution_result'] = result
            self.state = State.RESCHEDULING
            return

        # TODO:
        #  1. Review the implementation: currently, we assign a crew and then check for new failures;
        #  this ignores the case where by the time a crew is assigned, there's a new failure where it can
        #  be used better.
        #  2. Review the maximum steps to reschedule - the flow should not enter the analysis paralysis.
        elif self.state == State.RESCHEDULING:
            # Check for cascading failures
            new_failures = self.sys.detect_failure_nodes()

            # Filter out the ones we just fixed? 
            # Or assume detect_nodes returns CURRENT broken nodes.
            if new_failures:
                print(f"[ALERT] Cascading failure detected: {new_failures}")
                # Reset partial memory but keep history?
                self.state = State.FAILURE_DETECTION
            else:
                print("[SUCCESS] Good to progress with the repairs")
                self.state = State.FINAL
            return

    def _handle_planning_step(self):
        context = {
            "failures": self.memory['failures'],
            "impact_report": self.memory['impact_report'],
            # TODO: limit the history to max_steps
            "conversation_history": self.memory['plan_history']
        }

        system_prompt = get_system_prompt(self.tool_descriptions, context)
        response_str = self.llm.generate(system_prompt, self.memory)

        try:
            decision = json.loads(response_str)
            tool_name = decision.get('action')
            args = decision.get('arguments', {})

            print(f"[LLM DECISION] {tool_name} with {args}")

            if tool_name == "assign_repair_crew":
                # TERMINAL ACTION
                self.memory['pending_action'] = decision
                self.state = State.EXECUTION

            else:
                tool_func = self.tools.get_tool(tool_name)
                if tool_func:
                    result = tool_func(**args)
                    # Add to history so LLM sees it in next loop
                    self.memory['plan_history'].append({
                        "role": "tool_output",
                        "tool": tool_name,
                        "result": result
                    })
                else:
                    print(f"[ERROR] Unknown tool {tool_name}")
                    # TODO: Handle to prevent getting stuck in the current state, perhaps retrying is a good idea

        except json.JSONDecodeError:
            print("[ERROR] Invalid JSON from LLM")
            # TODO: Handle to prevent getting stuck in the current state, perhaps retrying is a good idea
