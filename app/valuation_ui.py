"""
Streamlit valuation page: form input and result breakdown display.

Phase 3 additions:
  • Apartment complex search (Property-First entry point)
  • KPI cards: estimated value, YoY change, latest unit price
  • 5-year price history chart (Plotly line chart)
  • Pyeong ↔ ㎡ area unit toggle (read from st.session_state["unit_mode"])
  • Crossover button → News Analysis page
  • Watchlist bookmarking
  • Korean real estate glossary expander
"""

from __future__ import annotations

import logging
from collections import defaultdict

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from app.context import add_to_watchlist, get_app_context, set_selected_property
from app.property_search_ui import render_complex_search
from valuation.data.comparables import get_price_history
from valuation.engine import run_valuation
from valuation.models import Property

logger = logging.getLogger(__name__)

REGIONS = [
    "서울 강남구", "서울 서초구", "서울 용산구", "서울 송파구",
    "서울 성동구", "서울 마포구", "서울 광진구", "서울 영등포구",
    "서울 노원구", "서울 은평구", "서울 강동구", "서울 동작구",
    "경기 성남시", "경기 수원시", "부산 해운대구",
]
PROPERTY_TYPES = ["아파트", "오피스텔", "단독주택"]

# Korean real estate glossary for the dictionary card expander.
_GLOSSARY: dict[str, str] = {
    "공시지가": "국토교통부가 매년 발표하는 토지의 공식 가격. 시세의 60~80% 수준.",
    "실거래가": "실제로 매매된 가격. 신고 의무로 투명하게 공개됨.",
    "전용면적": "해당 세대만 사용하는 전용 공간의 면적. 공용 면적(계단·복도) 미포함.",
    "용적률(FAR)": "연면적을 대지면적으로 나눈 비율(%). 높을수록 고층 건물이 가능.",
    "LTV": "주택담보인정비율(Loan to Value). 집값 대비 대출 한도 비율.",
    "DSR": "총부채원리금상환비율. 연소득 대비 전체 대출 원리금 비율.",
    "전세": "집주인에게 목돈을 맡기고 월세 없이 거주하는 한국 고유 임대 방식.",
    "갭투자": "전세가와 매매가의 차액만으로 매입하는 투자 방식. 하락장에 위험.",
    "재건축": "낡은 아파트를 허물고 새 아파트를 짓는 절차. 관리처분인가가 핵심 단계.",
    "청약": "새 아파트 분양 신청 절차. 청약통장 보유 기간 등이 당첨 점수에 영향.",
    "GTX": "수도권 광역급행철도. 개통 예정 노선 주변 아파트 가격에 큰 영향.",
}

_SQM_PER_PYEONG = 3.3058


def render_valuation_page() -> None:
    """Render the valuation page with complex search, form, KPI cards, and chart."""

    st.header("부동산 감정 평가")
    st.caption("Korean Real Estate Valuation (MVP - Mock Data)")

    unit_mode: str = st.session_state.get("unit_mode", "㎡")

    # ── Property-First entry point: complex search ─────────────────────────────
    with st.expander("🔍 단지 검색으로 자동 입력", expanded=False):
        selected_complex = render_complex_search(key_prefix="val_complex")
        if selected_complex:
            st.session_state["prefill_complex"] = selected_complex
            st.caption(
                f"**{selected_complex.name}** | {selected_complex.district} "
                f"{selected_complex.dong} | {selected_complex.building_year}년 준공 | "
                f"{selected_complex.total_units:,}세대"
            )

    prefill = st.session_state.get("prefill_complex")

    # ── Valuation form ─────────────────────────────────────────────────────────
    with st.form("valuation_form"):
        col1, col2 = st.columns(2)
        with col1:
            region_idx = (
                REGIONS.index(prefill.district)
                if prefill and prefill.district in REGIONS
                else 0
            )
            region = st.selectbox("지역", options=REGIONS, index=region_idx)

            type_idx = (
                PROPERTY_TYPES.index(prefill.property_type)
                if prefill and prefill.property_type in PROPERTY_TYPES
                else 0
            )
            property_type = st.selectbox(
                "유형", options=PROPERTY_TYPES, index=type_idx
            )

            if unit_mode == "평":
                area_pyeong = st.number_input(
                    "전용면적 (평)",
                    min_value=3.0,
                    max_value=91.0,
                    value=round(84.0 / _SQM_PER_PYEONG, 1),
                    step=0.5,
                )
                area_sqm = float(area_pyeong * _SQM_PER_PYEONG)
            else:
                area_sqm = st.number_input(
                    "전용면적 (㎡)",
                    min_value=10.0,
                    max_value=300.0,
                    value=84.0,
                    step=1.0,
                )

        with col2:
            floor = st.number_input("층", min_value=1, max_value=70, value=10)
            construction_year = st.number_input(
                "준공연도",
                min_value=1980,
                max_value=2026,
                value=int(prefill.building_year) if prefill else 2015,
            )

        submitted = st.form_submit_button("감정 평가", use_container_width=True)

    if submitted:
        try:
            prop = Property(
                region=region,
                property_type=property_type,
                area_sqm=area_sqm,
                floor=floor,
                construction_year=construction_year,
            )
            result = run_valuation(prop)
            st.session_state["last_valuation_result"] = result
            st.session_state["last_valuation_property"] = prop
            complex_name = prefill.name if prefill else ""
            set_selected_property(st.session_state, prop, complex_name)
        except ValueError as exc:
            st.error(f"입력 오류: {exc}")
            logger.warning("Valuation input error: %s", exc)
            return

    _render_result(unit_mode=unit_mode)


def _render_result(unit_mode: str = "㎡") -> None:
    """Display KPI cards, price history chart, factor breakdown, and actions."""

    result = st.session_state.get("last_valuation_result")
    prop = st.session_state.get("last_valuation_property")
    if result is None or prop is None:
        return

    ctx = get_app_context(st.session_state)
    complex_name: str = ctx.selected_complex_name or ""

    st.divider()

    # ── KPI cards ─────────────────────────────────────────────────────────────
    history = get_price_history(complex_name, years=5) if complex_name else []

    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        area_label = (
            f"{prop.area_sqm / _SQM_PER_PYEONG:.1f}평"
            if unit_mode == "평"
            else f"{prop.area_sqm}㎡"
        )
        st.metric(
            label="감정가 (예상)",
            value=f"{result.estimated_value_krw / 1e8:.2f} 억",
            help=f"{result.estimated_value_krw:,} 원 · {area_label}",
        )

    with kpi2:
        if history:
            records_2024 = [r for r in history if r["date"].startswith("2024")]
            records_2023 = [r for r in history if r["date"].startswith("2023")]
            if records_2024 and records_2023:
                avg_2024 = sum(r["price_per_sqm_krw"] for r in records_2024) / len(records_2024)
                avg_2023 = sum(r["price_per_sqm_krw"] for r in records_2023) / len(records_2023)
                yoy = (avg_2024 - avg_2023) / avg_2023 * 100
                st.metric(label="YoY 변동 (2024 vs 2023)", value=f"{yoy:+.1f}%")
            else:
                st.metric(label="YoY 변동", value="데이터 없음")
        else:
            building_age = 2024 - prop.construction_year
            st.metric(label="건물 연식", value=f"{building_age}년차")

    with kpi3:
        if history:
            last = max(history, key=lambda r: r["date"])
            price_per = last["price_per_sqm_krw"]
            if unit_mode == "평":
                st.metric(
                    label="최근 거래 단가",
                    value=f"{price_per * _SQM_PER_PYEONG / 1e4:.0f} 만원/평",
                )
            else:
                st.metric(
                    label="최근 거래 단가",
                    value=f"{price_per / 1e4:.0f} 만원/㎡",
                )
        else:
            st.metric(label="요인 수", value=f"{len(result.factor_breakdown)}개")

    st.caption(
        f"{prop.region} / {prop.property_type} / "
        f"{area_label} / {prop.floor}층 / {prop.construction_year}년"
    )

    # ── 5-year price history chart ─────────────────────────────────────────────
    if history:
        st.subheader("5년 실거래 단가 추이")
        _render_price_chart(history, unit_mode=unit_mode)

    # ── Factor breakdown table ─────────────────────────────────────────────────
    st.subheader("산정 내역")
    rows = []
    running = 0
    for factor in result.factor_breakdown:
        running += factor.contribution_krw
        rows.append(
            {
                "요인": factor.name,
                "계수/단가": (
                    f"{factor.multiplier_or_value:,.0f}"
                    if factor.multiplier_or_value > 10
                    else f"{factor.multiplier_or_value}"
                ),
                "기여금액 (원)": f"{factor.contribution_krw:+,}",
                "누적 (원)": f"{running:,}",
                "비고": factor.description or "",
            }
        )
    rows.append(
        {
            "요인": "합계",
            "계수/단가": "",
            "기여금액 (원)": "",
            "누적 (원)": f"{result.estimated_value_krw:,}",
            "비고": "",
        }
    )
    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"데이터 출처: {result.data_sources_used}")

    # ── Crossover + watchlist actions ──────────────────────────────────────────
    act1, act2 = st.columns(2)
    with act1:
        if complex_name and complex_name not in ctx.watchlist:
            if st.button("★ 관심 목록에 추가", use_container_width=True):
                add_to_watchlist(st.session_state, complex_name)
                st.success(f"'{complex_name}'을 관심 목록에 추가했습니다.")
    with act2:
        if st.button("📰 관련 뉴스 분석", use_container_width=True):
            query = f"{complex_name or prop.region} 부동산 개발 GTX 재건축"
            st.session_state["news_crossover_query"] = query
            st.session_state["navigate_to"] = "뉴스 분석"
            st.rerun()

    # ── 3D building visualization ──────────────────────────────────────────────
    st.subheader("건물 구조")
    from valuation.building_visualization import build_building_figure

    fig = build_building_figure(
        floor=prop.floor,
        area_sqm=prop.area_sqm,
        property_type=prop.property_type,
    )
    st.plotly_chart(fig, use_container_width=True)

    # ── Dictionary card ────────────────────────────────────────────────────────
    with st.expander("💡 부동산 용어 사전", expanded=False):
        for term, definition in _GLOSSARY.items():
            st.markdown(f"**{term}**: {definition}")


def _render_price_chart(history: list[dict], unit_mode: str = "㎡") -> None:
    """
    Render a Plotly line chart showing average price per unit by year.

    Params:
        history: List of transaction dicts from get_price_history().
        unit_mode: "㎡" or "평". Determines the y-axis unit.
    """
    yearly: dict[str, list[int]] = defaultdict(list)
    for rec in history:
        year = rec["date"][:4]
        yearly[year].append(rec["price_per_sqm_krw"])

    years_sorted = sorted(yearly.keys())
    if unit_mode == "평":
        avgs = [
            sum(yearly[y]) / len(yearly[y]) * _SQM_PER_PYEONG / 10_000
            for y in years_sorted
        ]
        y_label = "만원/평"
    else:
        avgs = [
            sum(yearly[y]) / len(yearly[y]) / 10_000
            for y in years_sorted
        ]
        y_label = "만원/㎡"

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=years_sorted,
            y=avgs,
            mode="lines+markers",
            name="평균 거래 단가",
            line=dict(color="#1f77b4", width=2),
            marker=dict(size=7),
            hovertemplate=f"%{{x}}년: %{{y:,.0f}} {y_label}<extra></extra>",
        )
    )
    fig.update_layout(
        xaxis_title="연도",
        yaxis_title=y_label,
        height=280,
        margin=dict(l=10, r=10, t=20, b=30),
        showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
