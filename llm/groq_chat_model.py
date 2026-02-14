"""
Groq chat model factory via LangChain.

Project role:
  Provide a single place to create the Groq-backed LangChain chat model.
"""

from __future__ import annotations

from langchain_groq import ChatGroq

from src.config.env import GroqSettings


def build_groq_chat_model(settings: GroqSettings) -> ChatGroq:
    """
    Build a LangChain `ChatGroq` model from settings.

    Params:
      settings: GroqSettings containing api_key, model, and temperature.

    Returns:
      A configured `ChatGroq` instance.
    """

    return ChatGroq(
        api_key=settings.api_key,
        model=settings.model,
        temperature=settings.temperature,
        max_retries=2,
    )
