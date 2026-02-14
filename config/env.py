"""
Environment loading and access helpers.

Project role:
  Centralize .env loading and safe access to settings from either environment
  variables or Streamlit Community Cloud secrets.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


def load_environment() -> None:
    """
    Load environment variables from a local `.env` file if present.

    Notes:
      Streamlit Community Cloud secrets (from `.streamlit/secrets.toml` or the
      Cloud Secrets UI) are accessed via `streamlit.secrets` at runtime and do
      not require explicit loading here.
    """

    # `override=False` ensures real environment variables win over `.env`.
    load_dotenv(override=False)

def _get_streamlit_secret(name: str) -> str | None:
    """
    Attempt to read a secret from Streamlit secrets.

    Params:
      name: Secret key (e.g. "GROQ_API_KEY").

    Returns:
      The secret value as a string, or None if unavailable.
    """

    try:
        import streamlit as st  # local import to avoid hard dependency in non-UI contexts
    except Exception:
        return None

    try:
        if name not in st.secrets:
            return None
        value = st.secrets[name]
    except Exception:
        return None

    if value is None:
        return None
    if isinstance(value, str):
        return value
    return str(value)


def get_required_env(name: str) -> str:
    """
    Get a required environment variable.

    Params:
      name: Environment variable name.

    Returns:
      The environment variable value.

    Raises:
      RuntimeError: If the variable is missing or empty.
    """

    secret_value = _get_streamlit_secret(name)
    if secret_value is not None and secret_value.strip():
        return secret_value

    value = os.getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def get_optional_env(name: str, default: str) -> str:
    """
    Get an optional environment variable with a default.

    Params:
      name: Environment variable name.
      default: Default if missing/empty.

    Returns:
      The environment variable value or the default.
    """

    secret_value = _get_streamlit_secret(name)
    if secret_value is not None and secret_value.strip():
        return secret_value

    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value


def get_optional_float_env(name: str, default: float) -> float:
    """
    Get an optional float environment variable with a default.

    Params:
      name: Environment variable name.
      default: Default if missing/invalid.

    Returns:
      Parsed float value.
    """

    secret_value = _get_streamlit_secret(name)
    if secret_value is not None and secret_value.strip():
        try:
            return float(secret_value)
        except ValueError:
            return default

    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass(frozen=True)
class GroqSettings:
    """Settings for Groq-backed chat models."""

    api_key: str
    model: str
    temperature: float


def get_groq_settings(
    *,
    model_default: str = "llama-3.1-8b-instant",
    temperature_default: float = 0.2,
) -> GroqSettings:
    """
    Read Groq settings from environment variables.

    Environment variables:
      GROQ_API_KEY (required)
      GROQ_MODEL (optional)
      GROQ_TEMPERATURE (optional)
    """

    api_key = get_required_env("GROQ_API_KEY")
    model = get_optional_env("GROQ_MODEL", model_default)
    temperature = get_optional_float_env("GROQ_TEMPERATURE", temperature_default)
    return GroqSettings(api_key=api_key, model=model, temperature=temperature)
