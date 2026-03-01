"""
Tests for chat/history.py -- session history helpers and summary memory.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from chat.history import (
    SUMMARY_THRESHOLD,
    append_turn,
    count_non_system_turns,
    ensure_history_initialized,
    get_conversation_summary,
    get_history,
    should_summarize,
    store_conversation_summary,
    summarize_history,
)


class TestEnsureHistoryInitialized:
    def test_initializes_empty_state(self):
        state = {}
        ensure_history_initialized(state)
        assert "chat_history" in state

    def test_first_message_is_system(self):
        state = {}
        ensure_history_initialized(state)
        assert state["chat_history"][0]["role"] == "system"

    def test_does_not_overwrite_existing_history(self):
        state = {"chat_history": [{"role": "user", "content": "existing"}]}
        ensure_history_initialized(state)
        assert state["chat_history"][0]["role"] == "user"

    def test_custom_system_prompt(self):
        state = {}
        ensure_history_initialized(state, system_prompt="Custom prompt")
        assert state["chat_history"][0]["content"] == "Custom prompt"

    def test_custom_state_key(self):
        state = {}
        ensure_history_initialized(state, state_key="other_key")
        assert "other_key" in state


class TestAppendTurn:
    def test_appends_user_turn(self):
        state = {"chat_history": [{"role": "system", "content": "S"}]}
        append_turn(state, role="user", content="Hello")
        assert state["chat_history"][-1] == {"role": "user", "content": "Hello"}

    def test_appends_assistant_turn(self):
        state = {"chat_history": [{"role": "system", "content": "S"}]}
        append_turn(state, role="assistant", content="Hi!")
        assert state["chat_history"][-1]["role"] == "assistant"

    def test_length_increases(self):
        state = {"chat_history": [{"role": "system", "content": "S"}]}
        append_turn(state, role="user", content="Q")
        assert len(state["chat_history"]) == 2


class TestGetHistory:
    def test_returns_history(self, session_with_history):
        result = get_history(session_with_history)
        assert len(result) == 3

    def test_includes_system_turn(self, session_with_history):
        result = get_history(session_with_history)
        assert result[0]["role"] == "system"


class TestCountNonSystemTurns:
    def test_empty_history_returns_zero(self):
        state = {"chat_history": [{"role": "system", "content": "S"}]}
        assert count_non_system_turns(state) == 0

    def test_counts_user_and_assistant(self, session_with_history):
        # session_with_history has system + user + assistant = 2 non-system
        assert count_non_system_turns(session_with_history) == 2

    def test_missing_key_returns_zero(self):
        assert count_non_system_turns({}) == 0

    def test_only_counts_non_system(self):
        state = {
            "chat_history": [
                {"role": "system", "content": "S"},
                {"role": "system", "content": "S2"},
                {"role": "user", "content": "Q"},
            ]
        }
        assert count_non_system_turns(state) == 1


class TestShouldSummarize:
    def test_below_threshold_returns_false(self):
        state = {
            "chat_history": [
                {"role": "system", "content": "S"},
                {"role": "user", "content": "Q"},
            ]
        }
        assert not should_summarize(state, threshold=10)

    def test_at_threshold_returns_true(self):
        state = {"chat_history": [{"role": "system", "content": "S"}]}
        for i in range(10):
            state["chat_history"].append({"role": "user", "content": f"Q{i}"})
        assert should_summarize(state, threshold=10)

    def test_uses_summary_threshold_constant(self):
        assert isinstance(SUMMARY_THRESHOLD, int)
        assert SUMMARY_THRESHOLD > 0


class TestSummarizeHistory:
    def _make_model(self, summary_text: str):
        model = MagicMock()
        response = MagicMock()
        response.content = summary_text
        model.invoke.return_value = response
        return model

    def test_returns_string(self):
        history = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "Q"},
            {"role": "assistant", "content": "A"},
        ]
        model = self._make_model("요약된 내용입니다.")
        result = summarize_history(history, model)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_returns_model_content(self):
        history = [
            {"role": "user", "content": "Q"},
            {"role": "assistant", "content": "A"},
        ]
        model = self._make_model("요약된 내용입니다.")
        result = summarize_history(history, model)
        assert result == "요약된 내용입니다."

    def test_empty_history_returns_empty(self):
        result = summarize_history([], MagicMock())
        assert result == ""

    def test_only_system_turns_returns_empty(self):
        history = [{"role": "system", "content": "S"}]
        result = summarize_history(history, MagicMock())
        assert result == ""

    def test_model_failure_returns_empty(self):
        history = [{"role": "user", "content": "Q"}, {"role": "assistant", "content": "A"}]
        model = MagicMock()
        model.invoke.side_effect = RuntimeError("LLM error")
        result = summarize_history(history, model)
        assert result == ""


class TestSummaryStoreGet:
    def test_store_and_get(self):
        state = {}
        store_conversation_summary(state, "요약입니다.")
        assert get_conversation_summary(state) == "요약입니다."

    def test_get_returns_none_when_absent(self):
        assert get_conversation_summary({}) is None

    def test_custom_key(self):
        state = {}
        store_conversation_summary(state, "요약", summary_key="my_summary")
        assert get_conversation_summary(state, summary_key="my_summary") == "요약"
        assert get_conversation_summary(state) is None
