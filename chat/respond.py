"""
Generate assistant responses using LangChain chat models.

Project role:
  Convert internal chat history to LangChain messages and invoke the model.
"""

from __future__ import annotations

import logging

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage

from src.chat.history import ChatTurn

logger = logging.getLogger(__name__)


def _to_langchain_messages(history: list[ChatTurn]) -> list[BaseMessage]:
    messages: list[BaseMessage] = []
    for turn in history:
        role = turn["role"]
        content = turn["content"]
        if role == "system":
            messages.append(SystemMessage(content=content))
        elif role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
        else:
            # Future-proofing: ignore unknown roles rather than crashing UI.
            logger.warning("Unknown role in history: %s", role)
    return messages


def generate_reply(*, history: list[ChatTurn], model) -> str:
    """
    Generate an assistant reply from chat history.

    Params:
      history: Chat turns including the system prompt and prior turns.
      model: A LangChain chat model supporting `.invoke(messages)`.

    Returns:
      Assistant message content.

    Raises:
      RuntimeError: If the model response doesn't contain text.
    """

    messages = _to_langchain_messages(history)
    response = model.invoke(messages)
    content = getattr(response, "content", None)
    if content is None or (isinstance(content, str) and not content.strip()):
        raise RuntimeError("Model returned an empty response.")
    return str(content)
