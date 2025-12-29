import json

import pytest

from src.infra_fail_mngr.prompts.prompt_formatting import (
    include_context,
    include_response_format,
    include_tools
)

@pytest.mark.unit
def describe_prompt_formatting():

    def describe_include_context():
        def describe_when_context_is_empty():
            @pytest.fixture
            def context():
                return {}

            def it_includes_prompt(context):
                result = include_context("prompt-1", context)

                assert "prompt-1" in result

            def it_includes_context_label(context):
                result = include_context("prompt-1", context)

                assert "Context:" in result

            def it_includes_empty_json(context):
                result = include_context("prompt-1", context)

                assert "{}" in result

        def describe_when_context_has_single_key():
            @pytest.fixture
            def context():
                return {"key-1": "value-1"}

            def it_includes_prompt(context):
                result = include_context("prompt-1", context)

                assert "prompt-1" in result

            def it_includes_context_key(context):
                result = include_context("prompt-1", context)

                assert '"key-1"' in result

            def it_includes_context_value(context):
                result = include_context("prompt-1", context)

                assert '"value-1"' in result

            def it_formats_as_json(context):
                result = include_context("prompt-1", context)

                assert "Context:" in result
                json_str = result.split("Context:")[1].strip()
                parsed = json.loads(json_str)
                assert parsed == context

        def describe_when_context_has_multiple_keys():
            @pytest.fixture
            def context():
                return {"key-1": "value-1", "key-2": "value-2", "key-3": "value-3"}

            def it_includes_all_keys(context):
                result = include_context("prompt-1", context)

                assert '"key-1"' in result
                assert '"key-2"' in result
                assert '"key-3"' in result

            def it_includes_all_values(context):
                result = include_context("prompt-1", context)

                assert '"value-1"' in result
                assert '"value-2"' in result
                assert '"value-3"' in result

        def describe_when_context_is_nested():
            @pytest.fixture
            def context():
                return {
                    "key-1": "value-1",
                    "nested-l1": {
                        "key-2": "value-2",
                        "nested-l2": {
                            "key-3": "value-3"
                        }
                    }
                }

            def it_includes_nested_keys(context):
                result = include_context("prompt-1", context)

                assert '"nested-l1"' in result
                assert '"nested-l2"' in result

            def it_includes_nested_values(context):
                result = include_context("prompt-1", context)

                assert '"value-1"' in result
                assert '"value-2"' in result
                assert '"value-3"' in result

            def it_formats_nested_structure(context):
                result = include_context("prompt-1", context)

                json_str = result.split("Context:")[1].strip()
                parsed = json.loads(json_str)
                assert parsed == context

        def describe_when_context_has_list():
            @pytest.fixture
            def context():
                return {"items": ["item-1", "item-2", "item-3"]}

            def it_includes_list_items(context):
                result = include_context("prompt-1", context)

                assert '"item-1"' in result
                assert '"item-2"' in result
                assert '"item-3"' in result

            def it_formats_list_as_json(context):
                result = include_context("prompt-1", context)

                json_str = result.split("Context:")[1].strip()
                parsed = json.loads(json_str)
                assert parsed == context

    def describe_include_response_format():
        def it_includes_prompt():
            result = include_response_format("prompt-1")

            assert "prompt-1" in result

        def it_includes_response_format_label():
            result = include_response_format("prompt-1")

            assert "Response Format:" in result

        def it_includes_thoughts_field():
            result = include_response_format("prompt-1")

            assert '"thoughts"' in result

        def it_includes_action_field():
            result = include_response_format("prompt-1")

            assert '"action"' in result

        def it_includes_arguments_field():
            result = include_response_format("prompt-1")

            assert '"arguments"' in result

    def describe_include_tools():
        def describe_when_tools_is_empty_string():
            def it_includes_prompt():
                result = include_tools("prompt-1", "")

                assert "prompt-1" in result

            def it_includes_tools_label():
                result = include_tools("prompt-1", "")

                assert "Available Tools:" in result

        def describe_when_tools_is_single_tool():
            def it_includes_prompt():
                result = include_tools("prompt-1", "tool-1")

                assert "prompt-1" in result

            def it_includes_tool_description():
                result = include_tools("prompt-1", "tool-1")

                assert "tool-1" in result

            def it_includes_tools_label():
                result = include_tools("prompt-1", "tool-1")

                assert "Available Tools:" in result

        def describe_when_tools_is_multiple_tools():
            def it_includes_prompt():
                result = include_tools("prompt-1", "tool-1, tool-2, tool-3")

                assert "prompt-1" in result

            def it_includes_all_tools():
                result = include_tools("prompt-1", "tool-1, tool-2, tool-3")

                assert "tool-1" in result
                assert "tool-2" in result
                assert "tool-3" in result

            def it_includes_tools_label():
                result = include_tools("prompt-1", "tool-1, tool-2, tool-3")

                assert "Available Tools:" in result

        def describe_when_tools_is_multiline():
            @pytest.fixture
            def tools():
                return """tool-1: description-1
    tool-2: description-2
    tool-3: description-3"""

            def it_includes_prompt(tools):
                result = include_tools("prompt-1", tools)

                assert "prompt-1" in result

            def it_includes_all_tool_lines(tools):
                result = include_tools("prompt-1", tools)

                assert "tool-1" in result
                assert "tool-2" in result
                assert "tool-3" in result

            def it_includes_all_descriptions(tools):
                result = include_tools("prompt-1", tools)

                assert "description-1" in result
                assert "description-2" in result
                assert "description-3" in result
