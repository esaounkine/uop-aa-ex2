import json

from ..llm.llm_service import LLMService
from ..prompts.system_prompts import get_system_prompt
from ..states import State
from ..tools import SystemTools, AgentTools


class InfraAgent:
    def __init__(self, llm_service: LLMService, system_tools: SystemTools, agent_tools: AgentTools):
        self.llm_service = llm_service
        self.sys = system_tools
        self.tools = agent_tools
        self.max_steps = 10
        self.max_history_size = 5
        self.max_retries = 3
        self.tool_descriptions = self.tools.get_tool_descriptions()

        self.state = State.INIT
        self.memory = {}
        self.retry_count = 0
        self.step_history = []

    def run_to_completion(self):
        step = 0
        while self.state != State.FINAL and step < self.max_steps:
            self.run_step()
            step += 1

    def _transition_state(self, to_state: State, action: str, data: dict = None):
        self.step_history.append({
            "from_state": self.state.name,
            "to_state": to_state.name,
            "action": action,
            "data": data or {}
        })
        self.state = to_state

    def run_step(self):
        print(f"--- STATE: {self.state.name} ---")

        if self.state == State.INIT:
            self.memory = {
                "failures": [],
                "impact_report": {},
                "plan_history": []
            }
            self._transition_state(State.FAILURE_DETECTION, "initialize", {})
            return

        elif self.state == State.FAILURE_DETECTION:
            failures = self.sys.detect_failure_nodes()

            if not failures:
                print("[SYSTEM] No failures detected. System Healthy.")
                self._transition_state(State.FINAL, "no_failures_detected", {})
            else:
                self.memory['failures'] = failures
                print(f"[SYSTEM] Detected: {failures}")
                self._transition_state(State.IMPACT_ANALYSIS, "failures_detected", {"failures": failures})
            return

        elif self.state == State.IMPACT_ANALYSIS:
            report = {}
            for node in self.memory['failures']:
                report[node] = self.sys.estimate_impact(node_id=node)

            self.memory['impact_report'] = report
            self._transition_state(State.REPAIR_PLANNING, "impact_analyzed", {"impact_report": report})
            return

        elif self.state == State.REPAIR_PLANNING:
            success = self.handle_planning_step()
            if not success:
                self.retry_count += 1
                if self.retry_count >= self.max_retries:
                    print(f"[ERROR] Max retries ({self.max_retries}) reached. Transitioning to FINAL state.")
                    self._transition_state(State.FINAL, "max_retries_reached", {"retry_count": self.retry_count})
            else:
                self.retry_count = 0
            return

        elif self.state == State.EXECUTION:
            pending = self.memory.get('pending_action', {})
            args = pending.get('arguments', {})

            print(f"[EXECUTION] Dispatching Crews: {args}")
            result = self.sys.assign_repair_crew(**args)

            self.memory['execution_result'] = result

            details = result.get('details', {})
            failed_nodes = [node for node, status in details.items() if status == "Failed"]

            if failed_nodes:
                print(f"[EXECUTION] Some assignments failed: {failed_nodes}")
                self.memory['failures'] = failed_nodes
                self.memory['plan_history'].append({
                    "role": "execution_result",
                    "message": f"Assignment failed for nodes: {failed_nodes}",
                    "details": details
                })
                self._transition_state(State.REPAIR_PLANNING, "assignments_failed", {
                    "failed_nodes": failed_nodes,
                    "details": details
                })
            else:
                print("[EXECUTION] All assignments succeeded")
                self._transition_state(State.RESCHEDULING, "assignments_succeeded", {"details": details})
            return

        elif self.state == State.RESCHEDULING:
            existing_failures = self.memory['failures'] if self.memory else []
            new_failures = [node for node in self.sys.detect_failure_nodes() if node not in existing_failures]

            if new_failures:
                print(f"[ALERT] Cascading failures detected: {new_failures}")
                self._transition_state(State.FAILURE_DETECTION, "cascading_failures", {"new_failures": new_failures})
            else:
                print("[SUCCESS] Nothing new, good to proceed with the repairs")
                self._transition_state(State.FINAL, "repairs_completed", {})
            return

    def handle_planning_step(self):
        limited_history = self.memory['plan_history'][-self.max_history_size:] if self.memory['plan_history'] else []

        context = {
            "failures": self.memory['failures'],
            "impact_report": self.memory['impact_report'],
            "conversation_history": limited_history
        }

        response_str = self.llm_service.handle_request(
            get_system_prompt(),
            context,
            self.tool_descriptions,
        )

        try:
            decision = json.loads(response_str)
            tool_name = decision.get('action')
            args = decision.get('arguments', {})

            print(f"[LLM DECISION] {tool_name} with {args}")

            if tool_name == "assign_repair_crew":
                # TERMINAL ACTION
                self.memory['pending_action'] = decision
                self._transition_state(State.EXECUTION, "llm_decision_assign_crew", {
                    "decision": decision
                })
                return True

            else:
                tool_func = self.tools.get_tool(tool_name)
                if tool_func:
                    result = tool_func(**args)
                    self.memory['plan_history'].append({
                        "role": "tool_output",
                        "tool": tool_name,
                        "result": result
                    })
                    self._transition_state(self.state, "llm_decision_use_tool", {
                        "tool": tool_name,
                        "arguments": args,
                        "result": result
                    })
                    return True
                else:
                    print(f"[ERROR] Unknown tool {tool_name}")
                    self.memory['plan_history'].append({
                        "role": "error",
                        "message": f"Unknown tool: {tool_name}"
                    })
                    return False

        except (ValueError, TypeError) as e:
            print(f"[ERROR] Invalid JSON from LLM: {e}")
            self.memory['plan_history'].append({
                "role": "error",
                "message": "Invalid JSON response from LLM"
            })
            return False

    def get_summary(self):
        return {
            "current_state": self.state.name,
            "total_steps": len(self.step_history),
            "failures_detected": self.memory.get('failures', []),
            "execution_result": self.memory.get('execution_result'),
        }
