"""
Tests for tools/tool_manager.py -- tool binding and registry.

Covers tool listing, lookup by name, and binding to mock models.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from tools.tool_manager import (
    AVAILABLE_TOOLS,
    bind_tools_to_model,
    get_tool_by_name,
    list_available_tools,
)


class TestAvailableTools:
    """Tests for the AVAILABLE_TOOLS registry."""

    def test_not_empty(self):
        assert len(AVAILABLE_TOOLS) > 0

    def test_has_seven_tools(self):
        assert len(AVAILABLE_TOOLS) == 7

    def test_all_have_names(self):
        for t in AVAILABLE_TOOLS:
            assert t.name, f"Tool missing name"

    def test_all_have_descriptions(self):
        for t in AVAILABLE_TOOLS:
            assert t.description, f"Tool {t.name} missing description"


class TestGetToolByName:
    """Tests for get_tool_by_name()."""

    def test_finds_search_web(self):
        tool = get_tool_by_name("search_web")
        assert tool is not None
        assert tool.name == "search_web"

    def test_finds_calculate_math(self):
        tool = get_tool_by_name("calculate_math")
        assert tool is not None

    def test_returns_none_for_missing(self):
        assert get_tool_by_name("nonexistent") is None

    def test_returns_none_for_empty_string(self):
        assert get_tool_by_name("") is None


class TestListAvailableTools:
    """Tests for list_available_tools()."""

    def test_returns_list_of_strings(self):
        names = list_available_tools()
        assert all(isinstance(n, str) for n in names)

    def test_contains_expected_tools(self):
        names = list_available_tools()
        expected = {
            "search_web", "search_documents", "fetch_weather",
            "calculate_math", "get_current_time", "convert_currency",
            "parse_news_article",
        }
        assert expected == set(names)


class TestBindToolsToModel:
    """Tests for bind_tools_to_model()."""

    def test_calls_bind_tools_on_model(self):
        model = MagicMock()
        model.bind_tools.return_value = MagicMock()
        bind_tools_to_model(model)
        model.bind_tools.assert_called_once()

    def test_uses_default_tools_when_none(self):
        model = MagicMock()
        model.bind_tools.return_value = MagicMock()
        bind_tools_to_model(model)
        call_args = model.bind_tools.call_args
        assert call_args[0][0] is AVAILABLE_TOOLS

    def test_uses_custom_tools(self):
        model = MagicMock()
        model.bind_tools.return_value = MagicMock()
        custom_tools = [AVAILABLE_TOOLS[0]]
        bind_tools_to_model(model, tools=custom_tools)
        call_args = model.bind_tools.call_args
        assert call_args[0][0] is custom_tools

    def test_passes_tool_choice(self):
        model = MagicMock()
        model.bind_tools.return_value = MagicMock()
        bind_tools_to_model(model, tool_choice="any")
        call_kwargs = model.bind_tools.call_args[1]
        assert call_kwargs["tool_choice"] == "any"

    def test_returns_model_with_tools(self):
        model = MagicMock()
        bound_model = MagicMock()
        model.bind_tools.return_value = bound_model
        result = bind_tools_to_model(model)
        assert result is bound_model
