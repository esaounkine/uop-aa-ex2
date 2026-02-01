import inspect
from typing import Dict, List
from datetime import datetime

from ..domain import AgentRepository


class AgentTools:
    def __init__(self, repo: AgentRepository, additional_tools: list):
        self.repo = repo
        self.AGENT_TOOLS = [
            self.get_weather_at_location,
            self.is_holiday,
            self.is_weekend,
            self.get_time_of_day,
            self.estimate_travel_time,
            self.estimate_repair_time,
            self.get_crew_location,
            self.is_crew_available,
            self.get_available_crews
        ]
        self.AGENT_TOOLS.extend(additional_tools)

    def get_weather_at_location(self, location: str, **kwargs) -> Dict:
        """
        Return basic weather metrics for a location.

        Args:
            location (str): Location identifier.

        Returns:
            dict: A dictionary containing:
                - "location" (str): The location identifier.
                - "temperature" (int): Temperature value.
                - "is_raining" (bool): A derived condition flag.
        """
        temperature = self.repo.get_weather_at_location(location)

        return {
            "location": location,
            "temperature": temperature,
            "is_raining": temperature < 15
        }
    
    def is_holiday(self, date: datetime, **kwargs) -> bool:
        """
        Check whether a given date is a fixed-date public holiday in Greece.

        Args:
            date (datetime): The date to check.

        Returns:
            bool: True if the date is a public holiday, False otherwise.
        """
        is_public_holiday = self.repo.is_holiday(date)
        return is_public_holiday
    
    def is_weekend(self, date: datetime, **kwargs) -> bool:
        """
        Check whether a given date is Saturday or Sunday.

        Args:
            date (datetime): The date to check.

        Returns:
            bool: True if the date is Saturday or Sunday, False otherwise.
        """
        is_weekend = self.repo.is_weekend(date)
        return is_weekend
        
    def get_time_of_day(self, hour: int, **kwargs) -> str:
        """
        Categorize an hour of the day as daytime, evening, or overnight.
        
        Args:
            hour (int): Hour of the day (0–23).
        
        Returns:
            str: One of "daytime", "evening", or "overnight".
        """
        time_of_day = self.repo.get_time_of_day(hour)
        return time_of_day

    def estimate_travel_time(self, origin: str, destination: str, **kwargs) -> Dict[str, str | int]:
        """
         Estimate the travel time between two locations.

        Args:
            origin (str): The starting location.
            destination (str): The destination location.

        Returns:
            dict: A dictionary containing:
                - "origin" (str): The origin location.
                - "destination" (str): The destination location.
                - "time" (int): Estimated travel time in milliseconds.
        """
        travel_time = self.repo.estimate_travel_time(origin, destination)
        
        return {
            "origin": origin,
            "destination": destination,
            "time": travel_time
        }
    
    def estimate_repair_time(self, node: str, **kwargs) -> Dict[str, str | int]:
        """
         Estimate the repair time for a node.

        Args:
            node (str): The node type.

        Returns:
            dict: A dictionary containing:
                - "node" (str): The node type.
                - "time" (int): Estimated repair time in milliseconds.
        """
        repair_time = self.repo.estimate_repair_time(node)

        return {
            "node": node,
            "time": repair_time
        }


    def get_crew_location(self, crew_id: str, **kwargs) -> Dict[str, str]:
        """
        Retrieve the current assigned location of a repair crew.

        Args:
            crew_id (str): Identifier of the crew.

        Returns:
            dict: A dictionary containing:
                - "crew_id" (str): Identifier of the crew.
                - "location" (str): The location where the crew is currently assigned.
        """
        crew_location = self.repo.crew_location(crew_id)
        return {
            "crew_id": crew_id,
            "location": crew_location
        }
    
    def is_crew_available(self, crew_id: str, **kwargs) -> Dict[str, str | bool]:
        """
        Check whether a given repair crew is currently available.

        Args:
            crew_id (str): Identifier of the crew.

        Returns:
            dict: A dictionary containing:
                - "crew_id" (str): Identifier of the crew.
                - "is_available" (bool): True if the crew is available, False otherwise.
        """
        is_available = self.repo.is_crew_available(crew_id)
        return {
            "crew_id": crew_id,
            "is_available": is_available
        }
    
    def get_available_crews(self, **kwargs) -> List[str]:
        """
        Retrieve the list of currently available repair crews.

        Returns:
            List[str]: A list of crew identifiers that are currently available for assignment.
        """
        available_crews = self.repo.get_available_crews()
        return available_crews


    # Internal

    def get_tool_descriptions(self):
        """
        Reflect into the ENABLED_TOOLS list to generate the list of available tools.
        """
        descriptions = []
        for func in self.AGENT_TOOLS:
            name = func.__name__
            doc = inspect.getdoc(func)
            sig = inspect.signature(func)
            descriptions.append(f"{name}{sig} - {doc}")

        return "\n".join(descriptions)

    def get_tool(self, name: str):
        """
        Helper to match the function to the name.
        """
        return getattr(self, name, None)
