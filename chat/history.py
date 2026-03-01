"""
Chat history helpers for Streamlit session state.

Project role:
  Keep session-state data structures consistent and easy to evolve.
  Also provides ConversationSummaryMemory helpers: summarize long histories
  into a rolling summary that is injected as context in future turns.
"""

from __future__ import annotations

import logging
from typing import Literal, TypedDict

logger = logging.getLogger(__name__)

Role = Literal["system", "user", "assistant"]

SUMMARY_THRESHOLD = 10  # non-system turns before auto-summarization kicks in


class ChatTurn(TypedDict):
    role: Role
    content: str


DEFAULT_SYSTEM_PROMPT = "You are a helpful assistant."


# ── History initialization and basic accessors ────────────────────────────────


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


def append_turn(
    session_state: dict,
    *,
    role: Role,
    content: str,
    state_key: str = "chat_history",
) -> None:
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


# ── ConversationSummaryMemory helpers ─────────────────────────────────────────


def count_non_system_turns(
    session_state: dict,
    state_key: str = "chat_history",
) -> int:
    """
    Count the number of non-system turns (user + assistant) in the history.

    Params:
      session_state: Streamlit `st.session_state`.
      state_key: Session-state key for the chat history list.

    Returns:
      Integer count of user + assistant turns.
    """
    history = session_state.get(state_key, [])
    return sum(1 for t in history if t["role"] != "system")


def should_summarize(
    session_state: dict,
    state_key: str = "chat_history",
    threshold: int = SUMMARY_THRESHOLD,
) -> bool:
    """
    Return True when the conversation is long enough to benefit from summarization.

    Params:
      session_state: Streamlit `st.session_state`.
      state_key: Session-state key for the chat history.
      threshold: Minimum non-system turns before summarization is triggered.

    Returns:
      True if turn count >= threshold.
    """
    return count_non_system_turns(session_state, state_key) >= threshold


def summarize_history(history: list[ChatTurn], model) -> str:
    """
    Call the LLM to produce a rolling summary of the chat history.

    The summary is intended to replace older turns as injected context,
    keeping the effective context window manageable.

    Params:
      history: Full list of ChatTurn dicts (including system prompt).
      model: A LangChain chat model (plain, not tool-bound).

    Returns:
      Summary string in Korean. Returns an empty string on failure.
    """
    from langchain_core.messages import HumanMessage, SystemMessage

    from chat.prompts import SUMMARY_SYSTEM_PROMPT, SUMMARY_USER_TEMPLATE

    # Format non-system turns for the summary prompt.
    conversation_text = "\n".join(
        f"[{t['role'].upper()}] {t['content']}"
        for t in history
        if t["role"] != "system"
    )

    if not conversation_text.strip():
        return ""

    try:
        response = model.invoke([
            SystemMessage(content=SUMMARY_SYSTEM_PROMPT),
            HumanMessage(content=SUMMARY_USER_TEMPLATE.format(conversation=conversation_text)),
        ])
        summary = getattr(response, "content", str(response)).strip()
        logger.info("summarize_history: produced %d-char summary", len(summary))
        return summary
    except Exception as exc:
        logger.warning("summarize_history failed: %s", exc)
        return ""


def get_conversation_summary(
    session_state: dict,
    *,
    summary_key: str = "conversation_summary",
) -> str | None:
    """
    Retrieve the stored conversation summary from session state.

    Returns:
      Summary string, or None if not yet generated.
    """
    return session_state.get(summary_key)


def store_conversation_summary(
    session_state: dict,
    summary: str,
    *,
    summary_key: str = "conversation_summary",
) -> None:
    """
    Store the conversation summary in session state.

    Params:
      session_state: Streamlit `st.session_state`.
      summary: The summary string to store.
      summary_key: Session-state key for the summary.
    """
    session_state[summary_key] = summary
    logger.debug("Stored conversation summary (%d chars)", len(summary))
