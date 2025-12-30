import pytest

from src.infra_fail_mngr.llm import LLMClientImpl

def describe_llm_client_impl():

    def describe_generate():

        def describe_when_response_list_is_null():
            @pytest.fixture
            def client():
                return LLMClientImpl(None)

            def it_returns_empty_string(client):
                result = client.generate("test-prompt")

                assert result == ""

        def describe_when_response_list_is_empty():
            @pytest.fixture
            def client():
                return LLMClientImpl([])

            def it_returns_empty_string(client):
                result = client.generate("test-prompt")

                assert result == ""

        def describe_when_response_list_is_not_empty():
            @pytest.fixture
            def client():
                return LLMClientImpl(["test-res-1", "test-res-2"])

            def it_returns_first_response_on_first_call(client):
                result = client.generate("test-prompt-1")

                assert result == "test-res-1"

            def it_increments_index_after_call(client):
                client.generate("test-prompt-1")

                assert client.response_index == 1

            def it_returns_sequential_responses(client):
                res1 = client.generate("test-prompt-1")
                res2 = client.generate("test-prompt-2")

                assert res1 == "test-res-1"
                assert res2 == "test-res-2"
                assert client.response_index == 2

            def it_returns_last_response_when_exhausted(client):
                res1 = client.generate("test-prompt-1")
                res2 = client.generate("test-prompt-2")
                res3 = client.generate("test-prompt-3")

                assert res1 == "test-res-1"
                assert res2 == "test-res-2"
                assert res3 == "test-res-2"
                assert client.response_index == 3

