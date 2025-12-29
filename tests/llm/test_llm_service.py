import json

import pytest

from src.infra_fail_mngr.llm.llm_client import LLMClientImpl
from src.infra_fail_mngr.llm.llm_service import LLMServiceImpl


@pytest.mark.unit
def describe_llm_service_impl():
    def describe_initialization():
        def it_creates_service_with_client():
            client = LLMClientImpl(["res-1"])

            service = LLMServiceImpl(client)

            assert service.client == client

    def describe_handle_request():
        def describe_when_valid_json_response():
            @pytest.fixture
            def valid_response():
                return {
                    "thoughts": "thoughts-1",
                    "action": "action-1",
                    "arguments": {
                        "arg-name-1": "arg-val-1",
                        "arg-name-2": "arg-val-2"}
                }

            @pytest.fixture
            def client(valid_response):
                return LLMClientImpl([json.dumps(valid_response)])

            @pytest.fixture
            def service(client):
                return LLMServiceImpl(client)

            def it_returns_parsed_json_response(service, valid_response):
                system_prompt = "prompt-1"
                context = {"key-1": ["val-1", "val-2"]}
                tools = "tool-1, tool-2"

                result = service.handle_request(system_prompt, context, tools)

                assert result == valid_response

            def it_includes_context_in_prompt(service, mocker):
                spy = mocker.spy(service.client, 'generate')
                context = {"key-1": ["val-1"], "key-2": "val-2"}

                service.handle_request("prompt-1", context, "tools")

                spy.assert_called_once()
                call_args = spy.call_args[0][0]
                assert "Context:" in call_args
                assert '"key-1"' in call_args
                assert '"key-2"' in call_args

            def it_includes_response_format_in_prompt(service, mocker):
                spy = mocker.spy(service.client, 'generate')

                service.handle_request("prompt-1", {}, "tools")

                call_args = spy.call_args[0][0]
                assert "Response Format:" in call_args
                assert '"thoughts"' in call_args
                assert '"action"' in call_args
                assert '"arguments"' in call_args

            def it_includes_tools_in_prompt(service, mocker):
                spy = mocker.spy(service.client, 'generate')
                tools = "tool-1, tool-2, tool-3"

                service.handle_request("prompt-1", {}, tools)

                call_args = spy.call_args[0][0]
                assert "Available Tools:" in call_args
                assert tools in call_args

            def it_calls_client_generate_once(service, mocker):
                spy = mocker.spy(service.client, 'generate')

                service.handle_request("prompt-1", {}, "tools")

                spy.assert_called_once()

        def describe_when_multiple_requests():
            @pytest.fixture
            def responses():
                return [
                    {
                        "action": "action-1",
                        "arguments": {
                            "arg-name-1": "arg-val-1"
                        }
                    },
                    {
                        "action": "action-2", "arguments": {}
                    },
                ]

            @pytest.fixture
            def client(responses):
                return LLMClientImpl([json.dumps(r) for r in responses])

            @pytest.fixture
            def service(client):
                return LLMServiceImpl(client)

            def it_returns_different_responses_for_each_request(service, responses):
                result1 = service.handle_request("prompt-1", {}, "tools")
                result2 = service.handle_request("prompt-2", {}, "tools")

                assert result1 == responses[0]
                assert result2 == responses[1]

            def it_handles_different_contexts_for_each_request(service, mocker):
                spy = mocker.spy(service.client, 'generate')
                context1 = {"con-key-1": ["con-val-1"]}
                context2 = {"con-key-2": ["con-val-2", "con-val-3"]}

                service.handle_request("prompt-1", context1, "tools")
                service.handle_request("prompt-1", context2, "tools")

                assert spy.call_count == 2
                res1 = spy.call_args_list[0][0][0]
                res2 = spy.call_args_list[1][0][0]
                assert '"con-val-1"' in res1
                assert '"con-val-2"' in res2
                assert '"con-val-3"' in res2

        def describe_when_empty_context():
            @pytest.fixture
            def client():
                response = {"action": "action-1", "arguments": {}}
                return LLMClientImpl([json.dumps(response)])

            @pytest.fixture
            def service(client):
                return LLMServiceImpl(client)

            def it_handles_empty_context_dict(service):
                result = service.handle_request("prompt-1", {}, "tools")

                assert result["action"] == "action-1"

            def it_includes_empty_context_in_prompt(service, mocker):
                spy = mocker.spy(service.client, 'generate')

                service.handle_request("prompt-1", {}, "tools")

                call_args = spy.call_args[0][0]
                assert "Context:" in call_args
                assert "{}" in call_args

        def describe_when_invalid_json_response():

            @pytest.fixture
            def client():
                return LLMClientImpl(["error-1"])

            @pytest.fixture
            def service(client):
                return LLMServiceImpl(client)

            def it_raises_json_decode_error(service):
                with pytest.raises(json.JSONDecodeError):
                    service.handle_request("prompt-1", {}, "tools")

        def describe_when_empty_string_response():

            @pytest.fixture
            def client():
                return LLMClientImpl([""])

            @pytest.fixture
            def service(client):
                return LLMServiceImpl(client)

            def it_raises_json_decode_error(service):
                with pytest.raises(ValueError):
                    service.handle_request("prompt-1", {}, "tools")

        def describe_when_null_string_response():

            @pytest.fixture
            def client():
                return LLMClientImpl([None])

            @pytest.fixture
            def service(client):
                return LLMServiceImpl(client)

            def it_raises_json_decode_error(service):
                with pytest.raises(ValueError):
                    service.handle_request("prompt-1", {}, "tools")
