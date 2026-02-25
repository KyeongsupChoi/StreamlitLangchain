"""
Main Streamlit application for LangChainExpo.

Project role:
  Compose UI + domain logic to provide a LangChain-powered chat experience
  and a Korean real estate valuation page with factor breakdown.
"""

from __future__ import annotations

import logging

import streamlit as st

from app.valuation_ui import render_valuation_page
from chat.history import append_turn, ensure_history_initialized, get_history
from chat.respond import generate_reply
from config.env import get_groq_settings, load_environment
from llm.groq_chat_model import build_groq_chat_model
from observability.logging_config import configure_logging

logger = logging.getLogger(__name__)

PAGE_VALUATION = "부동산 감정 평가"
PAGE_CHAT = "Chat"


def _render_sidebar() -> dict:
    """Render sidebar with page navigation and chat settings."""

    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Page",
        options=[PAGE_VALUATION, PAGE_CHAT],
        label_visibility="collapsed",
    )

    chat_settings = {}
    if page == PAGE_CHAT:
        st.sidebar.divider()
        st.sidebar.header("Chat Settings")
        chat_settings["model"] = st.sidebar.text_input(
            "Groq model",
            value="llama-3.1-8b-instant",
            help="Overrides GROQ_MODEL if set here.",
        )
        chat_settings["temperature"] = float(
            st.sidebar.slider(
                "Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05
            )
        )
        chat_settings["system_prompt"] = st.sidebar.text_area(
            "System prompt", value="You are a helpful assistant."
        )
        if st.sidebar.button("Reset chat"):
            st.session_state.pop("chat_history", None)
            st.rerun()

    return {"page": page, **chat_settings}


def _render_chat_page(sidebar: dict) -> None:
    """Render the LangChain chat page."""

    st.title("LangChainExpo")
    st.caption("Streamlit + LangChain (Groq)")

    ensure_history_initialized(
        st.session_state, system_prompt=sidebar["system_prompt"]
    )

    groq_settings = get_groq_settings(
        model_default=sidebar["model"],
        temperature_default=sidebar["temperature"],
    )
    model = build_groq_chat_model(groq_settings)

    history = get_history(st.session_state)

    for turn in history:
        if turn["role"] == "system":
            continue
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.markdown(turn["content"])

    prompt = st.chat_input("Ask something...")
    if not prompt:
        return

    append_turn(st.session_state, role="user", content=prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                assistant_text = generate_reply(
                    history=get_history(st.session_state), model=model
                )
            except Exception:
                logger.exception("Failed to generate reply")
                st.error(
                    "Failed to generate a reply. Check `logs/app.log` for details."
                )
                return
        st.markdown(assistant_text)

    append_turn(st.session_state, role="assistant", content=assistant_text)


def run() -> None:
    """Run the Streamlit application."""

    configure_logging()
    load_environment()

    st.set_page_config(page_title="LangChainExpo", layout="centered")

    sidebar = _render_sidebar()

    if sidebar["page"] == PAGE_VALUATION:
        render_valuation_page()
    else:
        _render_chat_page(sidebar)
