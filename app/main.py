"""
Main Streamlit application for LangChainExpo.

Project role:
  Compose UI + domain logic to provide a simple LangChain-powered chat experience.
"""

from __future__ import annotations

import logging

import streamlit as st

from src.chat.history import append_turn, ensure_history_initialized, get_history
from src.chat.respond import generate_reply
from src.config.env import get_groq_settings, load_environment
from src.llm.groq_chat_model import build_groq_chat_model
from src.observability.logging_config import configure_logging

logger = logging.getLogger(__name__)


def _render_sidebar() -> dict:
    st.sidebar.header("Settings")
    model = st.sidebar.text_input("Groq model", value="llama-3.1-8b-instant", help="Overrides GROQ_MODEL if set here.")
    temperature = st.sidebar.slider("Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05)
    system_prompt = st.sidebar.text_area("System prompt", value="You are a helpful assistant.")
    if st.sidebar.button("Reset chat"):
        st.session_state.pop("chat_history", None)
        st.rerun()

    return {"model": model, "temperature": float(temperature), "system_prompt": system_prompt}


def run() -> None:
    """Run the Streamlit application."""

    configure_logging()
    load_environment()

    st.set_page_config(page_title="LangChainExpo (Streamlit)", layout="centered")
    st.title("LangChainExpo")
    st.caption("Streamlit + LangChain (Groq)")

    sidebar = _render_sidebar()

    # Initialize session history
    ensure_history_initialized(st.session_state, system_prompt=sidebar["system_prompt"])

    # Build model (settings resolved from env + sidebar overrides)
    groq_settings = get_groq_settings(
        model_default=sidebar["model"],
        temperature_default=sidebar["temperature"],
    )
    model = build_groq_chat_model(groq_settings)

    history = get_history(st.session_state)

    # Render history (skip system prompt)
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
                assistant_text = generate_reply(history=get_history(st.session_state), model=model)
            except Exception:
                logger.exception("Failed to generate reply")
                st.error("Failed to generate a reply. Check `logs/app.log` for details.")
                return
        st.markdown(assistant_text)

    append_turn(st.session_state, role="assistant", content=assistant_text)
