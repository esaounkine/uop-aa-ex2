import pytest

from src.infra_fail_mngr.tools.agent_tools import AgentTools


@pytest.fixture
def repo_mock(mocker):
    return mocker.Mock()


@pytest.fixture
def agent_tools_base(repo_mock):
    return AgentTools(repo_mock, additional_tools=[])


def describe_agent_tools():
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

            assert "Returns metrics for a node" in result

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
                assert len(lines) == 2

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
