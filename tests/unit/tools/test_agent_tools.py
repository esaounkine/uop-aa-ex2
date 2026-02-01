import pytest
from datetime import datetime

from src.infra_fail_mngr.tools.agent_tools import AgentTools


@pytest.fixture
def repo_mock(mocker):
    mock_repo = mocker.Mock()
    return mock_repo


@pytest.fixture
def agent_tools_base(repo_mock):
    return AgentTools(repo_mock, additional_tools=[])


def describe_agent_tools():
    def describe_get_weather():
        def it_returns_weather_for_location(agent_tools_base, repo_mock):
            location = "location-1"
            repo_mock.get_weather_at_location.return_value = 14

            result = agent_tools_base.get_weather_at_location(location)

            assert result["location"] == location
            assert result["temperature"] == 14
            assert result["is_raining"] is True

    def describe_is_holiday():
        def it_is_holiday(agent_tools_base, repo_mock):
            date = datetime(2026, 1, 1)
            repo_mock.is_holiday.return_value = True

            result = agent_tools_base.is_holiday(date)

            assert result is True
        
        def it_is_not_holiday(agent_tools_base, repo_mock):
            date = datetime(2026, 7, 15)
            repo_mock.is_holiday.return_value = False

            result = agent_tools_base.is_holiday(date)

            assert result is False

    def describe_is_weekend():
        def it_returns_true_when_weekend(agent_tools_base, repo_mock):
            date = datetime(2026, 2, 1)
            repo_mock.is_weekend.return_value = True

            result = agent_tools_base.is_weekend(date)

            assert result is True
    
        def it_returns_false_when_weekend(agent_tools_base, repo_mock):
            date = datetime(2026, 1, 1)
            repo_mock.is_weekend.return_value = False

            result = agent_tools_base.is_weekend(date)

            assert result is False

    def describe_time_of_day():
        def it_is_daytime(agent_tools_base, repo_mock):
            repo_mock.get_time_of_day.return_value = "daytime"

            result = agent_tools_base.get_time_of_day(8)

            assert result == "daytime"

        def it_is_evening(agent_tools_base, repo_mock):
            repo_mock.get_time_of_day.return_value = "evening"

            result = agent_tools_base.get_time_of_day(20)

            assert result == "evening"

        def it_is_overnight(agent_tools_base, repo_mock):
            repo_mock.get_time_of_day.return_value = "overnight"

            result = agent_tools_base.get_time_of_day(0)

            assert result == "overnight"

    def describe_estimate_travel_time():
        def it_estimates_travel_time(agent_tools_base, repo_mock):
            origin = "location-1"
            destination = "location-2"
            repo_mock.estimate_travel_time.return_value = 3600000

            result = agent_tools_base.estimate_travel_time(origin, destination)

            assert result["origin"] == origin
            assert result["destination"] == destination
            assert result["time"] == 3600000

    def describe_estimate_repair_time():
        def it_estimates_repair_time(agent_tools_base, repo_mock):
            node = "node-1"
            repo_mock.estimate_repair_time.return_value = 1800000

            result = agent_tools_base.estimate_repair_time(node)

            assert result["node"] == node
            assert result["time"] == 1800000

    def describe_get_crew_location():
        def it_returns_crew_location(agent_tools_base, repo_mock):
            crew_id = "crew-1"
            repo_mock.crew_location.return_value = "location-1"

            result = agent_tools_base.get_crew_location(crew_id)

            assert result["crew_id"] == crew_id
            assert result["location"] == "location-1"

    def describe_is_crew_available():
        def it_returns_true_when_available(agent_tools_base, repo_mock):
            crew_id = "crew-1"
            repo_mock.is_crew_available.return_value = True

            result = agent_tools_base.is_crew_available(crew_id)

            assert result["crew_id"] == crew_id
            assert result["is_available"] is True

        def it_returns_false_when_unavailable(agent_tools_base, repo_mock):
            crew_id = "crew-10"
            repo_mock.is_crew_available.return_value = False

            result = agent_tools_base.is_crew_available(crew_id)

            assert result["crew_id"] == crew_id
            assert result["is_available"] is False

    def describe_get_available_crews():
        def it_returns_list_of_crews(agent_tools_base, repo_mock):
            repo_mock.get_available_crews.return_value = ["crew-1", "crew-2"]

            result = agent_tools_base.get_available_crews()

            assert result == ["crew-1", "crew-2"]

    def describe_get_tool_descriptions():
        def it_returns_string(agent_tools_base):
            result = agent_tools_base.get_tool_descriptions()

            assert isinstance(result, str)

        def it_includes_default_tool_name(agent_tools_base):
            result = agent_tools_base.get_tool_descriptions()

            assert "get_weather_at_location" in result

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

                assert "get_weather_at_location" in result
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
                return "get_weather_at_location"

            def it_returns_function(agent_tools_base, tool_name):
                result = agent_tools_base.get_tool(tool_name)

                assert callable(result)
                assert result.__name__ == "get_weather_at_location"

        def describe_when_tool_does_not_exist():
            @pytest.fixture
            def tool_name():
                return "nonexistent_tool"

            def it_returns_none(agent_tools_base, tool_name):
                result = agent_tools_base.get_tool(tool_name)

                assert result is None
