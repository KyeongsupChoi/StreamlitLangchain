"""
Tests for config/env.py -- environment loading and settings resolution.

Uses monkeypatch to isolate environment variable state. Streamlit secrets
are not available in test context, so tests focus on env-var fallback paths.
"""

from __future__ import annotations

import os

import pytest

from config.env import (
    GroqSettings,
    get_optional_env,
    get_optional_float_env,
    get_required_env,
)


class TestGetRequiredEnv:
    """Tests for get_required_env()."""

    def test_returns_env_value(self, monkeypatch):
        monkeypatch.setenv("TEST_REQUIRED_VAR", "test_value")
        assert get_required_env("TEST_REQUIRED_VAR") == "test_value"

    def test_raises_when_missing(self, monkeypatch):
        monkeypatch.delenv("MISSING_VAR_12345", raising=False)
        with pytest.raises(RuntimeError, match="Missing required"):
            get_required_env("MISSING_VAR_12345")

    def test_raises_when_empty(self, monkeypatch):
        monkeypatch.setenv("EMPTY_VAR", "")
        with pytest.raises(RuntimeError, match="Missing required"):
            get_required_env("EMPTY_VAR")

    def test_raises_when_whitespace(self, monkeypatch):
        monkeypatch.setenv("WHITESPACE_VAR", "   ")
        with pytest.raises(RuntimeError, match="Missing required"):
            get_required_env("WHITESPACE_VAR")


class TestGetOptionalEnv:
    """Tests for get_optional_env()."""

    def test_returns_env_value(self, monkeypatch):
        monkeypatch.setenv("TEST_OPT_VAR", "found")
        assert get_optional_env("TEST_OPT_VAR", "default") == "found"

    def test_returns_default_when_missing(self, monkeypatch):
        monkeypatch.delenv("MISSING_OPT_VAR_12345", raising=False)
        assert get_optional_env("MISSING_OPT_VAR_12345", "fallback") == "fallback"

    def test_returns_default_when_empty(self, monkeypatch):
        monkeypatch.setenv("EMPTY_OPT_VAR", "")
        assert get_optional_env("EMPTY_OPT_VAR", "fallback") == "fallback"

    def test_returns_default_when_whitespace(self, monkeypatch):
        monkeypatch.setenv("WS_OPT_VAR", "   ")
        assert get_optional_env("WS_OPT_VAR", "fallback") == "fallback"


class TestGetOptionalFloatEnv:
    """Tests for get_optional_float_env()."""

    def test_returns_parsed_float(self, monkeypatch):
        monkeypatch.setenv("FLOAT_VAR", "0.75")
        assert get_optional_float_env("FLOAT_VAR", 0.5) == 0.75

    def test_returns_default_when_missing(self, monkeypatch):
        monkeypatch.delenv("MISSING_FLOAT_12345", raising=False)
        assert get_optional_float_env("MISSING_FLOAT_12345", 0.2) == 0.2

    def test_returns_default_when_empty(self, monkeypatch):
        monkeypatch.setenv("EMPTY_FLOAT", "")
        assert get_optional_float_env("EMPTY_FLOAT", 0.3) == 0.3

    def test_returns_default_when_invalid(self, monkeypatch):
        monkeypatch.setenv("BAD_FLOAT", "not_a_number")
        assert get_optional_float_env("BAD_FLOAT", 0.4) == 0.4

    def test_integer_string_parsed(self, monkeypatch):
        monkeypatch.setenv("INT_FLOAT", "1")
        assert get_optional_float_env("INT_FLOAT", 0.0) == 1.0

    def test_negative_float(self, monkeypatch):
        monkeypatch.setenv("NEG_FLOAT", "-0.5")
        assert get_optional_float_env("NEG_FLOAT", 0.0) == -0.5


class TestGroqSettings:
    """Tests for the GroqSettings dataclass."""

    def test_construction(self):
        settings = GroqSettings(
            api_key="key123", model="llama-3.1-8b-instant", temperature=0.2,
        )
        assert settings.api_key == "key123"
        assert settings.model == "llama-3.1-8b-instant"
        assert settings.temperature == 0.2

    def test_frozen(self):
        settings = GroqSettings(
            api_key="key", model="model", temperature=0.0,
        )
        with pytest.raises(AttributeError):
            settings.api_key = "new_key"
