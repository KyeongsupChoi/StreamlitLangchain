"""
Streamlit News Analysis page — the "Trend Hunter" entry point.

Accepts a Naver News URL or keyword, runs the news agent, and displays:
  • Sentiment badge (Bullish / Bearish / Neutral) with Hojae Score (1–10)
  • Extracted entities, infrastructure type, and geographic regions
  • Impacted apartment complexes with crossover links to the Evaluator
  • Korean plain-language summary
  • Crossover: clicking "감정 평가 시작" on a complex pre-fills the valuation form
"""

from __future__ import annotations

import logging

import streamlit as st

from app.context import get_app_context, set_news_analysis
from tools.news_tools import NewsAnalysis
from valuation.data.complex_directory import get_complex

logger = logging.getLogger(__name__)

# Sentiment display config: (Korean label, colour hex, background hex)
_SENTIMENT_UI: dict[str, tuple[str, str, str]] = {
    "bullish": ("📈 호재 (Bullish)", "#155724", "#d4edda"),
    "bearish": ("📉 악재 (Bearish)", "#721c24", "#f8d7da"),
    "neutral": ("➡️ 중립 (Neutral)", "#856404", "#fff3cd"),
}


def _compute_hojae_score(analysis: NewsAnalysis) -> int:
    """
    Compute a 1–10 Hojae Score rating the news impact on property prices.

    Higher score = more significant price impact (positive or negative).

    Scoring:
      Base:                        4
      Non-neutral sentiment:      +2
      Each impacted complex:      +0.5 (max 3)
      Each region:                +0.3 (max 2)
      Infrastructure mentioned:   +1
    """
    score = 4.0
    if analysis.sentiment != "neutral":
        score += 2.0
    score += min(len(analysis.impacted_complexes) * 0.5, 3.0)
    score += min(len(analysis.regions) * 0.3, 2.0)
    if analysis.infrastructure:
        score += 1.0
    return min(int(round(score)), 10)


def render_news_page(sidebar_config: dict) -> None:
    """
    Render the News Analysis (Trend Hunter) page.

    Params:
        sidebar_config: Dict with 'model' and 'temperature' from sidebar settings.
    """
    st.title("뉴스 분석")
    st.caption("부동산 뉴스 키워드 또는 URL을 입력하면 시장 영향을 분석합니다.")

    # ── Input: crossover query from Evaluator or manual input ─────────────────
    crossover_q = st.session_state.pop("news_crossover_query", "")
    if crossover_q and "news_input_value" not in st.session_state:
        st.session_state["news_input_value"] = crossover_q

    query = st.text_input(
        "뉴스 키워드 또는 URL",
        placeholder="예: GTX-D 연장, 강남 재건축, 공시지가 상승...",
        key="news_input_value",
    )

    run_btn = st.button("분석 시작", type="primary", disabled=not bool(query and query.strip()))

    # ── Previous result (from session_state) ───────────────────────────────────
    ctx = get_app_context(st.session_state)
    previous_analysis = ctx.news_analysis
    previous_query = ctx.news_query

    analysis: NewsAnalysis | None = None

    if run_btn and query.strip():
        from chat.agents.news_agent import run_news_agent
        from config.env import get_groq_settings
        from llm.groq_chat_model import build_groq_chat_model

        groq_settings = get_groq_settings(
            model_default=sidebar_config.get("model", "llama-3.3-70b-versatile"),
            temperature_default=sidebar_config.get("temperature", 0.2),
        )
        model = build_groq_chat_model(groq_settings)

        with st.spinner("뉴스를 분석 중입니다..."):
            try:
                analysis = run_news_agent(query.strip(), model)
                set_news_analysis(st.session_state, analysis, query=query.strip())
                logger.info("News analysis complete: sentiment=%s", analysis.sentiment)
            except Exception:
                logger.exception("News agent failed")
                st.error("분석에 실패했습니다. 잠시 후 다시 시도해 주세요.")
                return

    elif not run_btn and previous_analysis is not None:
        # Show the previous result while the user hasn't triggered a new run.
        analysis = previous_analysis
        if previous_query:
            st.caption(f"이전 분석 결과 — 키워드: **{previous_query}**")

    if analysis is None:
        st.info("키워드 또는 URL을 입력하고 '분석 시작'을 클릭하세요.")
        return

    _render_analysis(analysis, sidebar_config=sidebar_config)


def _render_analysis(analysis: NewsAnalysis, sidebar_config: dict) -> None:
    """Render the full NewsAnalysis result card."""

    # ── Hojae Score + Sentiment badge ─────────────────────────────────────────
    score = _compute_hojae_score(analysis)
    label, fg, bg = _SENTIMENT_UI.get(
        analysis.sentiment, _SENTIMENT_UI["neutral"]
    )

    badge_html = (
        f'<span style="background-color:{bg};color:{fg};'
        f'padding:4px 12px;border-radius:6px;font-weight:600;">'
        f"{label}</span>"
    )
    st.markdown(badge_html, unsafe_allow_html=True)

    score_col, _ = st.columns([1, 3])
    with score_col:
        st.metric(
            label="호재 지수 (Hojae Score)",
            value=f"{score} / 10",
            help=(
                "뉴스가 부동산 가격에 미치는 영향의 크기를 1~10으로 환산. "
                "방향(호재/악재)은 위 배지를 참조."
            ),
        )

    # ── Summary ───────────────────────────────────────────────────────────────
    st.subheader("핵심 요약")
    st.write(analysis.summary or "요약 없음")

    # ── Extracted entities ─────────────────────────────────────────────────────
    col_left, col_right = st.columns(2)
    with col_left:
        if analysis.infrastructure:
            st.markdown(f"**핵심 인프라/이슈:** `{analysis.infrastructure}`")
        if analysis.regions:
            st.markdown("**영향 지역:**")
            for r in analysis.regions:
                st.markdown(f"  - {r}")
    with col_right:
        if analysis.entities:
            st.markdown("**언급 기관/단체:**")
            for e in analysis.entities:
                st.markdown(f"  - {e}")

    # ── Impacted complexes with crossover ─────────────────────────────────────
    if analysis.impacted_complexes:
        st.subheader("영향받는 아파트 단지")
        st.caption("단지명을 클릭하면 감정 평가 페이지로 이동합니다.")
        for complex_name in analysis.impacted_complexes:
            _render_complex_card(complex_name)
    else:
        st.info("영향받는 구체적인 단지가 식별되지 않았습니다.")


def _render_complex_card(complex_name: str) -> None:
    """
    Render a single impacted complex card with a crossover button.

    Params:
        complex_name: Name of the apartment complex.
    """
    found = get_complex(complex_name)
    with st.container(border=True):
        card_col, btn_col = st.columns([3, 1])
        with card_col:
            if found:
                st.markdown(
                    f"**{found.name}**  \n"
                    f"{found.district} {found.dong} | "
                    f"{found.building_year}년 준공 | "
                    f"{found.total_units:,}세대"
                )
            else:
                st.markdown(f"**{complex_name}**  \n(상세 정보 없음)")
        with btn_col:
            btn_key = f"goto_val_{complex_name.replace(' ', '_')}"
            if st.button("감정 평가", key=btn_key, use_container_width=True):
                if found:
                    st.session_state["prefill_complex"] = found
                st.session_state["navigate_to"] = "부동산 감정 평가"
                st.rerun()
