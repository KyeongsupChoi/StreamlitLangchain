"""
Tests for chat/respond.py -- plain LLM response generation.

Uses mock models to test message conversion and error handling
without actual API calls.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from chat.respond import _to_langchain_messages, generate_reply


class TestToLangchainMessages:
    """Tests for _to_langchain_messages() conversion."""

    def test_system_message(self):
        history = [{"role": "system", "content": "You are helpful."}]
        messages = _to_langchain_messages(history)
        assert len(messages) == 1
        assert messages[0].__class__.__name__ == "SystemMessage"
        assert messages[0].content == "You are helpful."

    def test_user_message(self):
        history = [{"role": "user", "content": "Hello"}]
        messages = _to_langchain_messages(history)
        assert messages[0].__class__.__name__ == "HumanMessage"

    def test_assistant_message(self):
        history = [{"role": "assistant", "content": "Hi"}]
        messages = _to_langchain_messages(history)
        assert messages[0].__class__.__name__ == "AIMessage"

    def test_full_conversation(self):
        history = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "User"},
            {"role": "assistant", "content": "Assistant"},
        ]
        messages = _to_langchain_messages(history)
        assert len(messages) == 3
        assert messages[0].__class__.__name__ == "SystemMessage"
        assert messages[1].__class__.__name__ == "HumanMessage"
        assert messages[2].__class__.__name__ == "AIMessage"

    def test_unknown_role_skipped(self):
        history = [{"role": "unknown", "content": "skipped"}]
        messages = _to_langchain_messages(history)
        assert len(messages) == 0

    def test_empty_history(self):
        messages = _to_langchain_messages([])
        assert messages == []


class TestGenerateReply:
    """Tests for generate_reply() with mock models."""

    def test_returns_model_content(self, mock_model):
        history = [
            {"role": "system", "content": "System"},
            {"role": "user", "content": "Hello"},
        ]
        result = generate_reply(history=history, model=mock_model)
        assert result == "Mock response"
        mock_model.invoke.assert_called_once()

    def test_raises_on_empty_content(self):
        model = MagicMock()
        model.invoke.return_value = MagicMock(content="")
        history = [{"role": "user", "content": "Hello"}]
        with pytest.raises(RuntimeError, match="empty response"):
            generate_reply(history=history, model=model)

    def test_raises_on_none_content(self):
        model = MagicMock()
        model.invoke.return_value = MagicMock(content=None)
        history = [{"role": "user", "content": "Hello"}]
        with pytest.raises(RuntimeError, match="empty response"):
            generate_reply(history=history, model=model)

    def test_raises_on_whitespace_content(self):
        model = MagicMock()
        model.invoke.return_value = MagicMock(content="   ")
        history = [{"role": "user", "content": "Hello"}]
        with pytest.raises(RuntimeError, match="empty response"):
            generate_reply(history=history, model=model)

    def test_stringifies_non_string_content(self):
        model = MagicMock()
        model.invoke.return_value = MagicMock(content=42)
        history = [{"role": "user", "content": "Hello"}]
        result = generate_reply(history=history, model=model)
        assert result == "42"
