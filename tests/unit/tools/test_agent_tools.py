import pytest
from datetime import datetime  #* added

from src.infra_fail_mngr.tools.agent_tools import AgentTools


@pytest.fixture
def repo_mock(mocker):
    mock_repo = mocker.Mock()
    mock_repo.get_weather_at_location.return_value = 25
    mock_repo.estimate_travel_time_in_ms.return_value = 3600000
    mock_repo.estimate_repair_time_in_ms.return_value = 1800000
    return mock_repo


@pytest.fixture
def agent_tools_base(repo_mock):
    return AgentTools(repo_mock, additional_tools=[])


def describe_agent_tools():
    def describe_get_weather():
        def it_returns_weather_for_location(agent_tools_base):
            location = "location-1"
            result = agent_tools_base.get_weather(location)

            assert result["location"] == location

    def describe_is_holiday():
        def it_is_holiday(agent_tools_base):
            new_years = datetime(2026, 1, 1)
            is_holiday = agent_tools_base.is_holiday(new_years)

            assert is_holiday
        
        def it_is_not_holiday(agent_tools_base):
            day_in_summer = datetime(2026, 7, 15)
            is_holiday = agent_tools_base.is_holiday(day_in_summer)

            assert not is_holiday

    def describe_time_of_day():
        def it_is_daytime(agent_tools_base):
            time_of_day = agent_tools_base.get_time_of_day(8)

            assert time_of_day == "daytime"

        def it_is_evening(agent_tools_base):
            time_of_day = agent_tools_base.get_time_of_day(20)

            assert time_of_day == "evening"

        def it_is_overnight(agent_tools_base):
            time_of_day = agent_tools_base.get_time_of_day(00)

            assert time_of_day == "overnight"

    def describe_is_weekend():
        def it_is_weekend(agent_tools_base):
            date = datetime(2026, 2, 1)
            is_weekend = agent_tools_base.is_weekend(date)

            assert is_weekend
    
        def it_is_not_weekend(agent_tools_base):
            date = datetime(2026, 1, 1)
            is_weekend = agent_tools_base.is_weekend(date)
            
            assert not is_weekend

    def describe_travel_time():
        def it_estimates_travel_time(agent_tools_base):
            origin = "location-1"
            destination = "location-2"
            result = agent_tools_base.estimate_travel_time(origin, destination)

            assert result["origin"] == origin
            assert result["destination"] == destination

    def describe_repair_time():
        def it_estimates_repair_time(agent_tools_base):
            node = "pipe"
            result = agent_tools_base.estimate_repair_time(node)

            assert result["node"] == node

    def describe_get_tool_descriptions():
        def it_returns_string(agent_tools_base):
            result = agent_tools_base.get_tool_descriptions()

            assert isinstance(result, str)

        def it_includes_default_tool_name(agent_tools_base):
            result = agent_tools_base.get_tool_descriptions()

            assert "get_weather" in result

        def it_includes_function_signature(agent_tools_base):
            result = agent_tools_base.get_tool_descriptions()

            assert "(location: str" in result

        def it_includes_docstring(agent_tools_base):
            result = agent_tools_base.get_tool_descriptions()

            assert "Return basic weather metrics for a location." in result

        def describe_when_additional_tools_provided():
            @pytest.fixture
            def test_tool():
                def test_tool_1(arg1: str, arg2: int):
                    """Test tool 1 docstring."""
                    return {"result": "data"}

                return test_tool_1

            @pytest.fixture
            def agent_tools_with_additional(repo_mock, test_tool):
                return AgentTools(repo_mock, additional_tools=[test_tool])

            def it_includes_test_tool_name(agent_tools_with_additional):
                result = agent_tools_with_additional.get_tool_descriptions()

                assert "test_tool_1" in result

            def it_includes_test_tool_signature(agent_tools_with_additional):
                result = agent_tools_with_additional.get_tool_descriptions()

                assert "(arg1: str, arg2: int)" in result

            def it_includes_test_tool_docstring(agent_tools_with_additional):
                result = agent_tools_with_additional.get_tool_descriptions()

                assert "Test tool 1 docstring" in result

            def it_includes_both_default_and_test_tools(agent_tools_with_additional):
                result = agent_tools_with_additional.get_tool_descriptions()

                assert "get_weather" in result
                assert "test_tool_1" in result

            def it_separates_tools_entries(agent_tools_with_additional):
                result = agent_tools_with_additional.get_tool_descriptions()

                lines = result.split("\n")
                assert len(lines) > 2

        def describe_when_tool_has_no_docstring():
            @pytest.fixture
            def tool_no_doc():
                def test_tool_2(arg: str):
                    pass

                return test_tool_2

            @pytest.fixture
            def agent_tools_no_doc(repo_mock, tool_no_doc):
                return AgentTools(repo_mock, additional_tools=[tool_no_doc])

            def it_includes_none_for_missing_docstring(agent_tools_no_doc):
                result = agent_tools_no_doc.get_tool_descriptions()

                assert "test_tool_2" in result
                assert "None" in result

    def describe_get_tool():
        def describe_when_tool_exists():
            @pytest.fixture
            def tool_name():
                return "get_weather"

            def it_returns_function(agent_tools_base, tool_name):
                result = agent_tools_base.get_tool(tool_name)

                assert callable(result)
                assert result.__name__ == "get_weather"

        def describe_when_tool_does_not_exist():
            @pytest.fixture
            def tool_name():
                return "nonexistent_tool"

            def it_returns_none(agent_tools_base, tool_name):
                result = agent_tools_base.get_tool(tool_name)

                assert result is None
