"""
Main Streamlit application for LangChainExpo.

Phase 3 additions:
  • 뉴스 분석 (News Analysis) page — Trend Hunter entry point
  • Cross-page navigation via st.session_state["navigate_to"]
  • Pyeong ↔ ㎡ unit toggle (valuation sidebar)
  • Expert / Newbie mode toggle (real estate chat sidebar)
  • Watchlist panel (sidebar, all pages)
"""

from __future__ import annotations

import logging

import streamlit as st

from app.context import get_app_context, remove_from_watchlist
from app.news_ui import render_news_page
from app.realestate_chat_ui import render_realestate_chat_page
from app.valuation_ui import render_valuation_page
from chat.history import append_turn, ensure_history_initialized, get_history
from chat.respond import generate_reply
from config.env import get_groq_settings, load_environment
from llm.groq_chat_model import build_groq_chat_model
from observability.logging_config import configure_logging

logger = logging.getLogger(__name__)

PAGE_HOME = "홈"
PAGE_VALUATION = "부동산 감정 평가"
PAGE_REALESTATE_CHAT = "부동산 AI 상담"
PAGE_NEWS = "뉴스 분석"
PAGE_CHAT = "Chat"
_ALL_PAGES = [PAGE_HOME, PAGE_VALUATION, PAGE_REALESTATE_CHAT, PAGE_NEWS, PAGE_CHAT]


def _render_sidebar() -> dict:
    """Render sidebar with page navigation, settings, and watchlist."""

    # ── Navigation ─────────────────────────────────────────────────────────────
    # Support programmatic navigation via st.session_state["navigate_to"].
    nav_override = st.session_state.pop("navigate_to", None)
    nav_index = (
        _ALL_PAGES.index(nav_override)
        if nav_override in _ALL_PAGES
        else 0
    )

    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Page",
        options=_ALL_PAGES,
        index=nav_index,
        label_visibility="collapsed",
    )

    chat_settings: dict = {}

    # ── Valuation page sidebar ─────────────────────────────────────────────────
    if page == PAGE_VALUATION:
        st.sidebar.divider()
        st.sidebar.header("표시 설정")
        unit_mode = st.sidebar.radio(
            "면적 단위",
            options=["㎡", "평"],
            horizontal=True,
            key="unit_mode",
        )
        chat_settings["unit_mode"] = unit_mode

    # ── Real estate chat sidebar ───────────────────────────────────────────────
    if page == PAGE_REALESTATE_CHAT:
        st.sidebar.divider()
        st.sidebar.header("Chat Settings")
        chat_settings["model"] = st.sidebar.text_input(
            "Groq model",
            value="llama-3.3-70b-versatile",
            help="Tool calling requires a capable model.",
        )
        chat_settings["temperature"] = float(
            st.sidebar.slider(
                "Temperature", min_value=0.0, max_value=1.0, value=0.2, step=0.05
            )
        )
        chat_settings["expert_mode"] = st.sidebar.toggle(
            "전문가 모드",
            value=True,
            help=(
                "전문가 모드: LTV·DSR·분양가 등 전문 용어 사용.\n"
                "입문자 모드: 쉬운 말로 풀어서 설명."
            ),
        )
        if st.sidebar.button("Reset chat"):
            st.session_state.pop("realestate_chat_history", None)
            st.session_state.pop("realestate_conversation_summary", None)
            st.rerun()

        # Memory indicator
        from chat.history import count_non_system_turns
        turn_count = count_non_system_turns(
            st.session_state, "realestate_chat_history"
        )
        if turn_count > 0:
            st.sidebar.caption(f"대화 기록: {turn_count}턴")
        if st.session_state.get("realestate_conversation_summary"):
            st.sidebar.info("🧠 메모리 활성화됨")

    # ── News analysis sidebar ──────────────────────────────────────────────────
    if page == PAGE_NEWS:
        st.sidebar.divider()
        st.sidebar.header("모델 설정")
        chat_settings["model"] = st.sidebar.text_input(
            "Groq model",
            value="llama-3.3-70b-versatile",
            key="news_model",
        )
        chat_settings["temperature"] = float(
            st.sidebar.slider(
                "Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.2,
                step=0.05,
                key="news_temp",
            )
        )

    # ── Generic chat sidebar ───────────────────────────────────────────────────
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

    # ── Home page sidebar — nothing extra ─────────────────────────────────────
    # (no settings needed; hero buttons handle navigation)

    # ── Watchlist (always visible if non-empty) ────────────────────────────────
    ctx = get_app_context(st.session_state)
    if ctx.watchlist:
        st.sidebar.divider()
        st.sidebar.subheader("★ 관심 목록")
        for name in list(ctx.watchlist):
            wl_col, rm_col = st.sidebar.columns([4, 1])
            with wl_col:
                if st.sidebar.button(
                    name,
                    key=f"wl_nav_{name}",
                    use_container_width=True,
                ):
                    # Navigate to valuation with this complex pre-filled
                    from valuation.data.complex_directory import get_complex
                    found = get_complex(name)
                    if found:
                        st.session_state["prefill_complex"] = found
                    st.session_state["navigate_to"] = PAGE_VALUATION
                    st.rerun()
            with rm_col:
                if st.sidebar.button("✕", key=f"wl_rm_{name}"):
                    remove_from_watchlist(st.session_state, name)
                    st.rerun()

    return {"page": page, **chat_settings}


def _render_home_page() -> None:
    """Render the landing page with two large hero entry-point buttons."""

    st.title("🏢 한국 부동산 AI 플랫폼")
    st.markdown("시작할 기능을 선택하세요.")
    st.divider()

    # Make the two hero buttons tall — scoped to the main content area only.
    st.markdown(
        """
        <style>
        [data-testid="stMain"] [data-testid="stButton"] > button {
            min-height: 180px;
            font-size: 1.3rem !important;
            font-weight: 700 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        if st.button(
            "🏠  Evaluate Listing",
            use_container_width=True,
            type="primary",
            key="home_btn_eval",
        ):
            st.session_state["navigate_to"] = PAGE_VALUATION
            st.rerun()
        st.caption("부동산 감정 평가 · 5년 실거래 추이 · 요인 분석")

    with col2:
        if st.button(
            "📰  Analyze News",
            use_container_width=True,
            key="home_btn_news",
        ):
            st.session_state["navigate_to"] = PAGE_NEWS
            st.rerun()
        st.caption("뉴스 시장 영향 분석 · 호재/악재 판별 · 영향 단지")


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

    st.set_page_config(
        page_title="LangChainExpo",
        page_icon="🏢",
        layout="centered",
    )

    sidebar = _render_sidebar()

    if sidebar["page"] == PAGE_HOME:
        _render_home_page()
    elif sidebar["page"] == PAGE_VALUATION:
        render_valuation_page()
    elif sidebar["page"] == PAGE_REALESTATE_CHAT:
        render_realestate_chat_page(sidebar)
    elif sidebar["page"] == PAGE_NEWS:
        render_news_page(sidebar)
    else:
        _render_chat_page(sidebar)
