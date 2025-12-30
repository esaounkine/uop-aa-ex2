import pytest

from src.infra_fail_mngr.tools.system_tools import SystemTools


@pytest.mark.unit
def describe_system_tools():
    def describe_detect_failure_nodes():
        def describe_when_no_failures():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_failed_nodes.return_value = []
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_empty_list(tools):
                result = tools.detect_failure_nodes()

                assert result == []

            def it_calls_repo_get_failed_nodes(tools, repo):
                tools.detect_failure_nodes()

                repo.get_failed_nodes.assert_called_once()

        def describe_when_single_failure():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_failed_nodes.return_value = ["node-1"]
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_single_node(tools):
                result = tools.detect_failure_nodes()

                assert result == ["node-1"]

            def it_calls_repo_get_failed_nodes(tools, repo):
                tools.detect_failure_nodes()

                repo.get_failed_nodes.assert_called_once()

        def describe_when_multiple_failures():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_failed_nodes.return_value = ["node-1", "node-2", "node-3"]
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_all_nodes(tools):
                result = tools.detect_failure_nodes()

                assert result == ["node-1", "node-2", "node-3"]
                assert len(result) == 3

        def describe_when_called_with_kwargs():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_failed_nodes.return_value = ["node-1"]
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_ignores_extra_kwargs(tools):
                result = tools.detect_failure_nodes(
                    kwarg1="arg-1",
                    kwarg2="arg-2"
                )

                assert result == ["node-1"]

    def describe_estimate_impact():
        def describe_when_node_is_critical():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_node_details.return_value = {"critical": True}
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_high_impact(tools):
                result = tools.estimate_impact("node-1")

                assert result["population_affected"] == 5000
                assert result["criticality"] == "High"

            def it_calls_repo_get_node_details(tools, repo):
                tools.estimate_impact("node-1")

                repo.get_node_details.assert_called_once_with("node-1")

        def describe_when_node_is_not_critical():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_node_details.return_value = {"critical": False}
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_low_impact(tools):
                result = tools.estimate_impact("node-1")

                assert result["population_affected"] == 100
                assert result["criticality"] == "Low"

            def it_calls_repo_get_node_details(tools, repo):
                tools.estimate_impact("node-1")

                repo.get_node_details.assert_called_once_with("node-1")

        def describe_when_node_details_empty():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_node_details.return_value = {}
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_low_impact(tools):
                result = tools.estimate_impact("node-1")

                assert result["population_affected"] == 100
                assert result["criticality"] == "Low"

        def describe_when_called_with_kwargs():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.get_node_details.return_value = {"critical": True}
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_ignores_extra_kwargs(tools):
                result = tools.estimate_impact("node-1", kwarg1="arg-1")

                assert result["population_affected"] == 5000

    def describe_assign_repair_crew():
        def describe_when_single_assignment_succeeds():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.assign_crew.return_value = True
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_completed_status(tools):
                result = tools.assign_repair_crew(["node-1"], ["crew-1"])

                assert result["status"] == "completed"

            def it_returns_assigned_details(tools):
                result = tools.assign_repair_crew(["node-1"], ["crew-1"])

                assert result["details"]["node-1"] == "Assigned"

            def it_calls_repo_assign_crew(tools, repo):
                tools.assign_repair_crew(["node-1"], ["crew-1"])

                repo.assign_crew.assert_called_once_with("node-1", "crew-1")

        def describe_when_single_assignment_fails():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.assign_crew.return_value = False
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_completed_status(tools):
                result = tools.assign_repair_crew(["node-1"], ["crew-1"])

                assert result["status"] == "completed"

            def it_returns_failed_details(tools):
                result = tools.assign_repair_crew(["node-1"], ["crew-1"])

                assert result["details"]["node-1"] == "Failed"

        def describe_when_multiple_assignments_all_succeed():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.assign_crew.return_value = True
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_completed_status(tools):
                result = tools.assign_repair_crew(
                    ["node-1", "node-2", "node-3"],
                    ["crew-1", "crew-2", "crew-3"]
                )

                assert result["status"] == "completed"

            def it_returns_all_assigned(tools):
                result = tools.assign_repair_crew(
                    ["node-1", "node-2", "node-3"],
                    ["crew-1", "crew-2", "crew-3"]
                )

                assert result["details"]["node-1"] == "Assigned"
                assert result["details"]["node-2"] == "Assigned"
                assert result["details"]["node-3"] == "Assigned"

            def it_calls_repo_for_each_assignment(tools, repo):
                tools.assign_repair_crew(
                    ["node-1", "node-2", "node-3"],
                    ["crew-1", "crew-2", "crew-3"]
                )

                assert repo.assign_crew.call_count == 3
                repo.assign_crew.assert_any_call("node-1", "crew-1")
                repo.assign_crew.assert_any_call("node-2", "crew-2")
                repo.assign_crew.assert_any_call("node-3", "crew-3")

        def describe_when_multiple_assignments_mixed_results():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.assign_crew.side_effect = [True, False, True]
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_completed_status(tools):
                result = tools.assign_repair_crew(
                    ["node-1", "node-2", "node-3"],
                    ["crew-1", "crew-2", "crew-3"]
                )

                assert result["status"] == "completed"

            def it_returns_mixed_details(tools):
                result = tools.assign_repair_crew(
                    ["node-1", "node-2", "node-3"],
                    ["crew-1", "crew-2", "crew-3"]
                )

                assert result["details"]["node-1"] == "Assigned"
                assert result["details"]["node-2"] == "Failed"
                assert result["details"]["node-3"] == "Assigned"

        def describe_when_empty_lists():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_returns_completed_status(tools):
                result = tools.assign_repair_crew([], [])

                assert result["status"] == "completed"

            def it_returns_empty_details(tools):
                result = tools.assign_repair_crew([], [])

                assert result["details"] == {}

            def it_does_not_call_repo(tools, repo):
                tools.assign_repair_crew([], [])

                repo.assign_crew.assert_not_called()

        def describe_when_called_with_kwargs():
            @pytest.fixture
            def repo(mocker):
                mock = mocker.Mock()
                mock.assign_crew.return_value = True
                return mock

            @pytest.fixture
            def tools(repo):
                return SystemTools(repo)

            def it_ignores_extra_kwargs(tools):
                result = tools.assign_repair_crew(
                    ["node-1"], ["crew-1"], kwarg1="arg-1"
                )

                assert result["status"] == "completed"
