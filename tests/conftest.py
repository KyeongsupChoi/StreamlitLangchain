"""
Shared pytest fixtures for LangChainExpo test suite.

Project role:
  Provides reusable fixtures for Property instances, mock chat models,
  and session state dictionaries used across multiple test modules.
"""

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock

import pytest

from valuation.models import Property


# ---------------------------------------------------------------------------
# Valuation fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def gangnam_apt() -> Property:
    """Standard Gangnam apartment for testing."""
    return Property(
        region="서울 강남구",
        property_type="아파트",
        area_sqm=84.0,
        floor=10,
        construction_year=2015,
    )


@pytest.fixture()
def seocho_officetel() -> Property:
    """Seocho officetel for testing."""
    return Property(
        region="서울 서초구",
        property_type="오피스텔",
        area_sqm=59.0,
        floor=5,
        construction_year=2020,
    )


@pytest.fixture()
def busan_house() -> Property:
    """Busan single-family house for testing."""
    return Property(
        region="부산 해운대구",
        property_type="단독주택",
        area_sqm=120.0,
        floor=1,
        construction_year=2000,
    )


# ---------------------------------------------------------------------------
# Chat / session state fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def empty_session_state() -> dict:
    """Empty session state dict (simulates fresh st.session_state)."""
    return {}


@pytest.fixture()
def session_with_history() -> dict:
    """Session state with pre-initialized chat history."""
    return {
        "chat_history": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
    }


# ---------------------------------------------------------------------------
# Mock LLM fixtures
# ---------------------------------------------------------------------------

@dataclass
class FakeAIMessage:
    """Minimal AI message for testing without LangChain model calls."""
    content: str
    tool_calls: list = None

    def __post_init__(self):
        if self.tool_calls is None:
            self.tool_calls = []


@pytest.fixture()
def mock_model():
    """Mock chat model that returns a simple text response."""
    model = MagicMock()
    model.invoke.return_value = FakeAIMessage(content="Mock response")
    return model


@pytest.fixture()
def mock_model_with_tool_call():
    """Mock chat model that first calls a tool, then returns a final answer."""
    model = MagicMock()
    # First call: model requests a tool call
    tool_call_response = FakeAIMessage(
        content="",
        tool_calls=[{
            "name": "test_tool",
            "args": {"arg1": "value1"},
            "id": "call_001",
        }],
    )
    # Second call: model returns final text answer
    final_response = FakeAIMessage(content="Final answer after tool call")
    model.invoke.side_effect = [tool_call_response, final_response]
    return model
