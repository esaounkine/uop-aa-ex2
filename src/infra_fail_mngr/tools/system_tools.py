from typing import List, Dict

from ..domain import SystemRepository


class SystemTools:
    def __init__(self, repo: SystemRepository):
        self.repo = repo

    def detect_failure_nodes(self, **kwargs) -> List[str]:
        """
        Scans the network for broken nodes.
        """
        return self.repo.get_failed_nodes()

    def estimate_impact(self, node_id: str, **kwargs) -> Dict:
        """
        Estimate the operational impact of a node failure.

        Args:
            node_id (str): Identifier of the affected node.

        Returns:
            dict: A dictionary containing:
                - "population_affected" (int): Estimated number of impacted users.
                - "criticality" (str): Impact level ("High" or "Low").
        """
        details = self.repo.get_node_details(node_id)

        return {
            # mock data
            "population_affected": 5000 if details.get("critical") else 100,
            "criticality": "High" if details.get("critical") else "Low"
        }

    def assign_repair_crew(self, node_ids: List[str], crew_ids: List[str], **kwargs) -> Dict:
        """
        Assigns crews to nodes.

        Args:
            node_ids (List[str]): List of node ids.
            crew_ids (List[str]): List of crew ids.

        Returns:
            dict: A dictionary containing:
                - "status" (str): Assignment process status ("completed").
                - "details" (dict): Mapping of node_id to assignment result ("Assigned" or "Failed").
        """
        assignments = {}
        for node, crew in zip(node_ids, crew_ids):
            success = self.repo.assign_crew(node, crew)
            assignments[node] = "Assigned" if success else "Failed"

        return {
            "status": "completed",
            "details": assignments,
        }
