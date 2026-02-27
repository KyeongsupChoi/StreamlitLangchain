"""
Tests for chat/respond_with_tools.py -- ReAct loop with tool execution.

Uses mock models and tools to test the tool-calling loop, tool resolution,
iteration limits, and error handling without actual API calls.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import MagicMock

import pytest
from langchain_core.tools import tool

from chat.respond_with_tools import (
    _find_tool_by_name,
    _find_tool_in_list,
    _to_langchain_messages,
    generate_reply_with_tools,
)


# ---------------------------------------------------------------------------
# Test tool for use in ReAct loop tests
# ---------------------------------------------------------------------------

@tool
def test_tool(arg1: str) -> str:
    """A test tool that echoes its argument."""
    return f"result: {arg1}"


@tool
def another_tool(x: int) -> str:
    """Another test tool."""
    return f"computed: {x * 2}"


# ---------------------------------------------------------------------------
# Helpers (fake AI message)
# ---------------------------------------------------------------------------

@dataclass
class FakeAIMessage:
    content: str
    tool_calls: list = field(default_factory=list)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFindToolInList:
    """Tests for _find_tool_in_list()."""

    def test_finds_existing_tool(self):
        tools = [test_tool, another_tool]
        result = _find_tool_in_list(tools, "test_tool")
        assert result is test_tool

    def test_finds_second_tool(self):
        tools = [test_tool, another_tool]
        result = _find_tool_in_list(tools, "another_tool")
        assert result is another_tool

    def test_returns_none_for_missing(self):
        tools = [test_tool]
        result = _find_tool_in_list(tools, "nonexistent")
        assert result is None

    def test_empty_list_returns_none(self):
        result = _find_tool_in_list([], "test_tool")
        assert result is None


class TestFindToolByName:
    """Tests for _find_tool_by_name() model inspection."""

    def test_finds_via_bound_tools(self):
        model = MagicMock()
        model.bound_tools = [test_tool]
        result = _find_tool_by_name(model, "test_tool")
        assert result is test_tool

    def test_finds_via_tools_attr(self):
        model = MagicMock(spec=[])
        model.tools = [test_tool]
        result = _find_tool_by_name(model, "test_tool")
        assert result is test_tool

    def test_returns_none_when_no_tools(self):
        model = MagicMock(spec=[])
        result = _find_tool_by_name(model, "test_tool")
        assert result is None


class TestToLangchainMessages:
    """Tests for _to_langchain_messages() in respond_with_tools module."""

    def test_converts_system_user_assistant(self):
        history = [
            {"role": "system", "content": "S"},
            {"role": "user", "content": "U"},
            {"role": "assistant", "content": "A"},
        ]
        messages = _to_langchain_messages(history)
        assert len(messages) == 3

    def test_empty_history(self):
        assert _to_langchain_messages([]) == []


class TestGenerateReplyWithTools:
    """Tests for the ReAct loop in generate_reply_with_tools()."""

    def test_simple_response_no_tools(self):
        """Model returns text without calling any tools."""
        model = MagicMock()
        model.invoke.return_value = FakeAIMessage(content="Direct answer")

        history = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "Hello"},
        ]
        result = generate_reply_with_tools(history=history, model=model)
        assert result == "Direct answer"
        assert model.invoke.call_count == 1

    def test_tool_call_then_final_answer(self):
        """Model calls a tool, gets result, then produces final answer."""
        model = MagicMock()
        # First invocation: model requests tool call
        model.invoke.side_effect = [
            FakeAIMessage(
                content="",
                tool_calls=[{
                    "name": "test_tool",
                    "args": {"arg1": "hello"},
                    "id": "call_001",
                }],
            ),
            # Second invocation: model produces final answer
            FakeAIMessage(content="The tool returned: result: hello"),
        ]

        history = [{"role": "user", "content": "Call test_tool"}]
        result = generate_reply_with_tools(
            history=history, model=model, tools=[test_tool],
        )
        assert "result: hello" in result
        assert model.invoke.call_count == 2

    def test_tool_call_uses_explicit_tools_list(self):
        """When tools= is provided, tool lookup uses the list, not model attrs."""
        model = MagicMock()
        model.invoke.side_effect = [
            FakeAIMessage(
                content="",
                tool_calls=[{
                    "name": "another_tool",
                    "args": {"x": 5},
                    "id": "call_002",
                }],
            ),
            FakeAIMessage(content="Result is computed: 10"),
        ]

        result = generate_reply_with_tools(
            history=[{"role": "user", "content": "Compute"}],
            model=model,
            tools=[test_tool, another_tool],
        )
        assert "10" in result

    def test_max_iterations_raises(self):
        """Exceeding max_iterations raises RuntimeError."""
        model = MagicMock()
        # Model always requests a tool call (never produces final answer)
        model.invoke.return_value = FakeAIMessage(
            content="",
            tool_calls=[{
                "name": "test_tool",
                "args": {"arg1": "loop"},
                "id": "call_loop",
            }],
        )

        with pytest.raises(RuntimeError, match="Maximum tool calling iterations"):
            generate_reply_with_tools(
                history=[{"role": "user", "content": "Loop"}],
                model=model,
                tools=[test_tool],
                max_iterations=2,
            )

    def test_empty_response_raises(self):
        """Empty final response raises RuntimeError."""
        model = MagicMock()
        model.invoke.return_value = FakeAIMessage(content="")

        with pytest.raises(RuntimeError, match="empty response"):
            generate_reply_with_tools(
                history=[{"role": "user", "content": "Hello"}],
                model=model,
            )

    def test_tool_not_found_returns_error_message(self):
        """When tool is not found, error message is sent back to model."""
        model = MagicMock()
        model.invoke.side_effect = [
            FakeAIMessage(
                content="",
                tool_calls=[{
                    "name": "nonexistent_tool",
                    "args": {},
                    "id": "call_003",
                }],
            ),
            FakeAIMessage(content="Sorry, tool not found"),
        ]

        result = generate_reply_with_tools(
            history=[{"role": "user", "content": "Call missing tool"}],
            model=model,
            tools=[test_tool],
        )
        assert result == "Sorry, tool not found"

    def test_tool_execution_error_returns_error_message(self):
        """When a tool raises an exception, error is sent back to model."""
        @tool
        def failing_tool(x: str) -> str:
            """A tool that always fails."""
            raise ValueError("Intentional failure")

        model = MagicMock()
        model.invoke.side_effect = [
            FakeAIMessage(
                content="",
                tool_calls=[{
                    "name": "failing_tool",
                    "args": {"x": "test"},
                    "id": "call_004",
                }],
            ),
            FakeAIMessage(content="The tool failed, sorry"),
        ]

        result = generate_reply_with_tools(
            history=[{"role": "user", "content": "Fail"}],
            model=model,
            tools=[failing_tool],
        )
        assert result == "The tool failed, sorry"

    def test_multiple_tool_calls_in_one_response(self):
        """Model requests multiple tools in a single response."""
        model = MagicMock()
        model.invoke.side_effect = [
            FakeAIMessage(
                content="",
                tool_calls=[
                    {"name": "test_tool", "args": {"arg1": "a"}, "id": "call_a"},
                    {"name": "another_tool", "args": {"x": 3}, "id": "call_b"},
                ],
            ),
            FakeAIMessage(content="Both tools returned results"),
        ]

        result = generate_reply_with_tools(
            history=[{"role": "user", "content": "Call both"}],
            model=model,
            tools=[test_tool, another_tool],
        )
        assert result == "Both tools returned results"
        assert model.invoke.call_count == 2

    def test_backward_compatible_without_tools_param(self):
        """Calling without tools= still works (falls through to model inspection)."""
        model = MagicMock()
        model.invoke.return_value = FakeAIMessage(content="No tools needed")

        result = generate_reply_with_tools(
            history=[{"role": "user", "content": "Hello"}],
            model=model,
        )
        assert result == "No tools needed"
