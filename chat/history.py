"""
Chat history helpers for Streamlit session state.

Project role:
  Keep session-state data structures consistent and easy to evolve.
"""

from __future__ import annotations

from typing import Literal, TypedDict


Role = Literal["system", "user", "assistant"]


class ChatTurn(TypedDict):
    role: Role
    content: str


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


def ensure_history_initialized(
    session_state: dict,
    *,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    state_key: str = "chat_history",
) -> None:
    """
    Ensure the Streamlit session state contains an initialized chat history.

    Params:
      session_state: Streamlit `st.session_state`.
      system_prompt: System prompt injected as the first message.
      state_key: Session-state key for storing chat history.
    """

    if state_key in session_state:
        return
    session_state[state_key] = [{"role": "system", "content": system_prompt}]


def append_turn(session_state: dict, *, role: Role, content: str, state_key: str = "chat_history") -> None:
    """
    Append a single chat turn to the session-state chat history.

    Params:
      session_state: Streamlit `st.session_state`.
      role: One of "system", "user", "assistant".
      content: Turn content.
      state_key: Session-state key for storing chat history.
    """

    history: list[ChatTurn] = session_state[state_key]
    history.append({"role": role, "content": content})


def get_history(session_state: dict, *, state_key: str = "chat_history") -> list[ChatTurn]:
    """
    Get the current chat history.

    Returns:
      A list of ChatTurn objects (including the system prompt).
    """

    return session_state[state_key]
