"""
Tests for chat/history.py -- session state chat history management.

Covers initialization, appending turns, retrieval, and state key isolation.
"""

from __future__ import annotations

import pytest

from chat.history import (
    DEFAULT_SYSTEM_PROMPT,
    append_turn,
    ensure_history_initialized,
    get_history,
)


class TestEnsureHistoryInitialized:
    """Tests for ensure_history_initialized()."""

    def test_creates_history_in_empty_state(self, empty_session_state):
        ensure_history_initialized(empty_session_state)
        assert "chat_history" in empty_session_state

    def test_default_system_prompt(self, empty_session_state):
        ensure_history_initialized(empty_session_state)
        history = empty_session_state["chat_history"]
        assert len(history) == 1
        assert history[0]["role"] == "system"
        assert history[0]["content"] == DEFAULT_SYSTEM_PROMPT

    def test_custom_system_prompt(self, empty_session_state):
        ensure_history_initialized(
            empty_session_state, system_prompt="Custom prompt"
        )
        assert empty_session_state["chat_history"][0]["content"] == "Custom prompt"

    def test_does_not_overwrite_existing(self, session_with_history):
        original_len = len(session_with_history["chat_history"])
        ensure_history_initialized(session_with_history)
        assert len(session_with_history["chat_history"]) == original_len

    def test_custom_state_key(self, empty_session_state):
        ensure_history_initialized(
            empty_session_state, state_key="realestate_chat_history"
        )
        assert "realestate_chat_history" in empty_session_state
        assert "chat_history" not in empty_session_state

    def test_multiple_keys_independent(self, empty_session_state):
        ensure_history_initialized(
            empty_session_state,
            system_prompt="Prompt A",
            state_key="key_a",
        )
        ensure_history_initialized(
            empty_session_state,
            system_prompt="Prompt B",
            state_key="key_b",
        )
        assert empty_session_state["key_a"][0]["content"] == "Prompt A"
        assert empty_session_state["key_b"][0]["content"] == "Prompt B"


class TestAppendTurn:
    """Tests for append_turn()."""

    def test_append_user_turn(self, session_with_history):
        initial_len = len(session_with_history["chat_history"])
        append_turn(session_with_history, role="user", content="New message")
        assert len(session_with_history["chat_history"]) == initial_len + 1
        assert session_with_history["chat_history"][-1]["role"] == "user"
        assert session_with_history["chat_history"][-1]["content"] == "New message"

    def test_append_assistant_turn(self, session_with_history):
        append_turn(session_with_history, role="assistant", content="Response")
        assert session_with_history["chat_history"][-1]["role"] == "assistant"

    def test_append_to_custom_key(self, empty_session_state):
        empty_session_state["custom_key"] = [
            {"role": "system", "content": "test"}
        ]
        append_turn(
            empty_session_state,
            role="user",
            content="Hello",
            state_key="custom_key",
        )
        assert len(empty_session_state["custom_key"]) == 2

    def test_preserves_existing_turns(self, session_with_history):
        original = list(session_with_history["chat_history"])
        append_turn(session_with_history, role="user", content="New")
        for i, turn in enumerate(original):
            assert session_with_history["chat_history"][i] == turn


class TestGetHistory:
    """Tests for get_history()."""

    def test_returns_full_history(self, session_with_history):
        history = get_history(session_with_history)
        assert len(history) == 3

    def test_includes_system_prompt(self, session_with_history):
        history = get_history(session_with_history)
        assert history[0]["role"] == "system"

    def test_custom_state_key(self, empty_session_state):
        empty_session_state["other_key"] = [
            {"role": "system", "content": "test"}
        ]
        history = get_history(empty_session_state, state_key="other_key")
        assert len(history) == 1

    def test_returns_same_list_object(self, session_with_history):
        """get_history returns the actual list, not a copy."""
        h1 = get_history(session_with_history)
        h2 = get_history(session_with_history)
        assert h1 is h2
