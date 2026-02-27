"""
Streamlit chat page for Korean real estate AI consultation.

Project role:
  Provides an LLM-powered conversational interface that calls valuation
  domain tools (estimate, comparables, official price, factor explanation)
  via the ReAct tool-calling loop. Separate session state from the generic
  chat page.
"""

from __future__ import annotations

import logging

import streamlit as st

from chat.history import append_turn, ensure_history_initialized, get_history
from chat.respond_with_tools import generate_reply_with_tools
from config.env import get_groq_settings
from llm.groq_chat_model import build_groq_chat_model
from tools.realestate_tools import REALESTATE_TOOLS
from tools.tool_manager import bind_tools_to_model

logger = logging.getLogger(__name__)

REALESTATE_SESSION_KEY = "realestate_chat_history"

REALESTATE_SYSTEM_PROMPT = """\
당신은 한국 부동산 전문 AI 상담사입니다.
사용자의 부동산 관련 질문에 정확하고 유용한 답변을 제공합니다.

## 역할
- 부동산 감정 평가 및 시세 분석
- 실거래가 조회 및 비교 분석
- 공시지가 조회
- 감정 평가 요인(기준가격, 층계수, 연도계수, 면적계수) 설명

## 사용 가능한 도구
- estimate_property_value: 매물의 시장 가치를 추정합니다.
- search_comparables: 해당 지역의 최근 실거래 사례를 조회합니다.
- lookup_official_land_price: 해당 지역의 공시지가를 조회합니다.
- explain_valuation_factors: 감정 평가에 사용되는 요인과 규칙을 설명합니다.

## 지원 지역
서울 강남구, 서울 서초구, 경기 성남시, 부산 해운대구

## 지원 유형
아파트, 오피스텔, 단독주택

## 응답 규칙
1. 특정 매물에 대해 질문하면 반드시 도구를 사용하여 데이터 기반 답변을 제공하세요.
2. 금액은 원(KRW) 단위, 천 단위 구분자(,) 사용.
3. 감정 평가 결과를 설명할 때 각 요인이 최종 가격에 어떻게 기여했는지 설명하세요.
4. 지원하지 않는 지역/유형에 대해 질문받으면 현재 지원 범위를 안내하세요.
5. 한국어로 답변하되 전문 용어는 설명을 제공하세요.
6. 데이터는 목(mock) 데이터임을 필요 시 안내하세요.
7. 부동산과 관련 없는 질문에는 정중히 부동산 상담 범위임을 안내하세요."""


def render_realestate_chat_page(sidebar_config: dict) -> None:
    """
    Render the real estate AI chatbot page.

    Params:
        sidebar_config: Dict with 'model' and 'temperature' from sidebar settings.
    """
    st.title("부동산 AI 상담")
    st.caption("한국 부동산 감정 평가 전문 챗봇 (Streamlit + LangChain + Groq)")

    ensure_history_initialized(
        st.session_state,
        system_prompt=REALESTATE_SYSTEM_PROMPT,
        state_key=REALESTATE_SESSION_KEY,
    )

    groq_settings = get_groq_settings(
        model_default=sidebar_config["model"],
        temperature_default=sidebar_config["temperature"],
    )
    model = build_groq_chat_model(groq_settings)
    model_with_tools = bind_tools_to_model(model, tools=REALESTATE_TOOLS)

    history = get_history(st.session_state, state_key=REALESTATE_SESSION_KEY)

    for turn in history:
        if turn["role"] == "system":
            continue
        with st.chat_message("user" if turn["role"] == "user" else "assistant"):
            st.markdown(turn["content"])

    prompt = st.chat_input("부동산에 대해 질문하세요...")
    if not prompt:
        return

    append_turn(
        st.session_state,
        role="user",
        content=prompt,
        state_key=REALESTATE_SESSION_KEY,
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            try:
                assistant_text = generate_reply_with_tools(
                    history=get_history(
                        st.session_state, state_key=REALESTATE_SESSION_KEY
                    ),
                    model=model_with_tools,
                    tools=REALESTATE_TOOLS,
                )
            except Exception:
                logger.exception("Failed to generate real estate chat reply")
                st.error(
                    "답변 생성에 실패했습니다. `logs/app.log`에서 상세 내용을 확인하세요."
                )
                return
        st.markdown(assistant_text)

    append_turn(
        st.session_state,
        role="assistant",
        content=assistant_text,
        state_key=REALESTATE_SESSION_KEY,
    )
