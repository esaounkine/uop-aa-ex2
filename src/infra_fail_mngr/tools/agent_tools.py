import inspect
from typing import Dict
from datetime import datetime

from ..domain import AgentRepository


class AgentTools:
    def __init__(self, repo: AgentRepository, additional_tools: list):
        self.repo = repo
        self.AGENT_TOOLS = [
            self.get_weather,
            self.is_holiday,
            self.is_weekend,
            self.get_time_of_day,
            self.estimate_travel_time,
            self.estimate_repair_time
        ]
        self.AGENT_TOOLS.extend(additional_tools)

    def get_weather(self, location: str, **kwargs) -> Dict:
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
            # mock data
            "location": location,
            "temperature": temperature,
            "is_raining": temperature > 20
        }
    
    def is_holiday(self, date: datetime, **kwargs) -> bool:  # https://en.wikipedia.org/wiki/Public_holidays_in_Greece
        """
        Check whether a given date is a fixed-date public holiday in Greece.

        Args:
            date (datetime): The date to check.

        Returns:
            bool: True if the date is a public holiday, False otherwise.
        """
        holidays = {"01 January", "06 January", "25 March", "01 May", "15 August", "28 October", "25 December", "26 December"}
        today = date.strftime("%d %B")
        return today in holidays
    
    def is_weekend(self, date: datetime, **kwargs) -> bool:
        """
        Check whether a given date is Saturday or Sunday.

        Args:
            date (datetime): The date to check.

        Returns:
            bool: True if the date is Saturday or Sunday, False otherwise.
        """
        return date.weekday() in (5, 6)
        
    def get_time_of_day(self, hour: int, **kwargs) -> str:
        """
        Categorize an hour of the day as daytime, evening, or overnight.
        
        Args:
            hour (int): Hour of the day (0–23).
        
        Returns:
            str: One of "daytime", "evening", or "overnight".
        """
        if (7 <= hour < 17):
            return "daytime"
        elif (17 <= hour < 23):
            return "evening"
        elif (hour == 23) or (0 <= hour < 7):
            return 'overnight'


    def estimate_travel_time(self, origin: str, destination: str, **kwargs) -> int:
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
        travel_time = self.repo.estimate_travel_time_in_ms(origin, destination)
        
        return {
            "origin": origin,
            "destination": destination,
            "time": travel_time
        }
    
    def estimate_repair_time(self, node: str, **kwargs) -> int:
        """
         Estimate the repair time for a node.

        Args:
            node (str): The node type.

        Returns:
            dict: A dictionary containing:
                - "node" (str): The node type.
                - "time" (int): Estimated repair time in milliseconds.
        """
        repair_time = self.repo.estimate_repair_time_in_ms(node)

        return {
            "node": node,
            "time": repair_time
        }

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
