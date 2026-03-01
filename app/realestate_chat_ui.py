"""
Streamlit chat page for Korean real estate AI consultation.

Phase 3 additions:
  • Expert / Newbie mode: switches system prompt terminology complexity.
  • Dictionary Cards: scans LLM responses for Korean RE terms and renders
    an expandable glossary explaining each detected term in plain language.
"""

from __future__ import annotations

import logging

import streamlit as st

from chat.history import (
    SUMMARY_THRESHOLD,
    append_turn,
    ensure_history_initialized,
    get_conversation_summary,
    get_history,
    should_summarize,
    store_conversation_summary,
    summarize_history,
)
from chat.prompts import APPRAISER_SYSTEM_PROMPT
from chat.respond_with_tools import generate_reply_with_tools
from tools.news_tools import parse_news_article
from tools.realestate_tools import REALESTATE_TOOLS
from tools.tool_manager import bind_tools_to_model

logger = logging.getLogger(__name__)

REALESTATE_SESSION_KEY = "realestate_chat_history"
SUMMARY_STATE_KEY = "realestate_conversation_summary"

# Full tool set: domain tools + news parsing.
_ALL_REALESTATE_TOOLS = REALESTATE_TOOLS + [parse_news_article]

# Suffix appended to system prompt in newbie mode.
_NEWBIE_MODE_SUFFIX = """

## 입문자 모드 활성화
- 전문 용어 대신 쉬운 말을 사용하세요.
  예: LTV → "집값 대비 대출 한도", DSR → "소득 대비 빚 상환 비율",
      분양가 → "새 아파트 판매 가격", 전세가율 → "전세금이 집값에서 차지하는 비율"
- 개념을 처음 접하는 사람도 이해할 수 있도록 비유와 예시를 풍부하게 사용하세요.
- 복잡한 계산보다는 직관적인 설명을 우선하세요."""

# Key Korean real estate terms detected in responses trigger a dictionary card.
_TERM_DEFINITIONS: dict[str, str] = {
    "공시지가": "국토교통부가 매년 발표하는 토지의 공식 가격. 시세의 60~80% 수준.",
    "실거래가": "실제로 매매된 가격. 신고 의무로 투명하게 공개됨.",
    "LTV": "주택담보인정비율(Loan to Value). 집값 대비 대출 한도 비율.",
    "DSR": "총부채원리금상환비율. 연소득 대비 전체 대출 원리금 비율.",
    "전세": "집주인에게 목돈을 맡기고 월세 없이 거주하는 한국 고유 임대 방식.",
    "전세가율": "매매가 대비 전세금의 비율. 갭투자 위험의 척도.",
    "갭투자": "전세가와 매매가의 차액만으로 매입하는 투자 방식. 하락장에 위험.",
    "재건축": "낡은 아파트를 허물고 새 아파트를 짓는 절차. 관리처분인가가 핵심 단계.",
    "관리처분": "재건축 절차에서 조합원 권리를 최종 확정하는 단계. 이후 가격 상승 경향.",
    "청약": "새 아파트 분양 신청 절차. 청약통장 보유 기간 등이 당첨 점수에 영향.",
    "분양가": "새 아파트 최초 판매 가격. 분양가상한제 적용 여부에 따라 규제.",
    "GTX": "수도권 광역급행철도. 개통 예정 노선 주변 아파트 가격에 큰 영향.",
    "용적률": "연면적을 대지면적으로 나눈 비율(%). 높을수록 고층 건물이 가능.",
    "경매": "법원이 채무 변제를 위해 부동산을 강제 매각하는 절차.",
}


def _build_system_prompt(expert_mode: bool) -> str:
    """Return the appropriate system prompt based on the mode toggle."""
    if expert_mode:
        return APPRAISER_SYSTEM_PROMPT
    return APPRAISER_SYSTEM_PROMPT + _NEWBIE_MODE_SUFFIX


def _render_dictionary_card(response_text: str) -> None:
    """
    Scan response_text for known Korean RE terms and render a glossary card.

    Shows an expander only when at least one term is detected.
    """
    detected = {
        term: defn
        for term, defn in _TERM_DEFINITIONS.items()
        if term in response_text
    }
    if not detected:
        return
    with st.expander(f"💡 용어 설명 ({len(detected)}개 용어 감지됨)", expanded=False):
        for term, defn in detected.items():
            st.markdown(f"**{term}**: {defn}")


def render_realestate_chat_page(sidebar_config: dict) -> None:
    """
    Render the real estate AI chatbot page.

    Params:
        sidebar_config: Dict with 'model', 'temperature', and 'expert_mode'
                        from sidebar settings.
    """
    st.title("부동산 AI 상담")
    st.caption("한국 부동산 감정 평가 전문 챗봇 (Streamlit + LangChain + Groq)")

    from config.env import get_groq_settings
    from llm.groq_chat_model import build_groq_chat_model

    expert_mode: bool = sidebar_config.get("expert_mode", True)
    system_prompt = _build_system_prompt(expert_mode)

    if not expert_mode:
        st.info("입문자 모드: 쉬운 언어로 설명합니다.")

    ensure_history_initialized(
        st.session_state,
        system_prompt=system_prompt,
        state_key=REALESTATE_SESSION_KEY,
    )

    groq_settings = get_groq_settings(
        model_default=sidebar_config["model"],
        temperature_default=sidebar_config["temperature"],
    )
    model = build_groq_chat_model(groq_settings)
    model_with_tools = bind_tools_to_model(model, tools=_ALL_REALESTATE_TOOLS)

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

    conversation_summary = get_conversation_summary(
        st.session_state, summary_key=SUMMARY_STATE_KEY
    )

    with st.chat_message("assistant"):
        with st.spinner("분석 중..."):
            try:
                assistant_text = generate_reply_with_tools(
                    history=get_history(
                        st.session_state, state_key=REALESTATE_SESSION_KEY
                    ),
                    model=model_with_tools,
                    tools=_ALL_REALESTATE_TOOLS,
                    conversation_summary=conversation_summary,
                )
            except Exception:
                logger.exception("Failed to generate real estate chat reply")
                st.error(
                    "답변 생성에 실패했습니다. `logs/app.log`에서 상세 내용을 확인하세요."
                )
                return
        st.markdown(assistant_text)
        _render_dictionary_card(assistant_text)

    append_turn(
        st.session_state,
        role="assistant",
        content=assistant_text,
        state_key=REALESTATE_SESSION_KEY,
    )

    # Auto-summarize when conversation exceeds threshold.
    if should_summarize(st.session_state, REALESTATE_SESSION_KEY):
        try:
            summary = summarize_history(
                get_history(st.session_state, state_key=REALESTATE_SESSION_KEY),
                model,
            )
            if summary:
                store_conversation_summary(
                    st.session_state, summary, summary_key=SUMMARY_STATE_KEY
                )
                logger.info("Conversation summary updated (%d chars)", len(summary))
        except Exception:
            logger.warning("Failed to summarize conversation", exc_info=True)
