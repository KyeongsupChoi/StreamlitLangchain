"""
Streamlit valuation page: form input and result breakdown display.

Project role:
  Renders the Korean real estate valuation form (region, type, area, floor,
  construction year), runs the valuation engine on submit, and displays the
  estimated value with a factor-by-factor breakdown table.
"""

from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

from valuation.engine import run_valuation
from valuation.models import Property

logger = logging.getLogger(__name__)

REGIONS = ["서울 강남구", "서울 서초구", "경기 성남시", "부산 해운대구"]
PROPERTY_TYPES = ["아파트", "오피스텔", "단독주택"]


def render_valuation_page() -> None:
    """Render the valuation form and result breakdown."""

    st.header("부동산 감정 평가")
    st.caption("Korean Real Estate Valuation (MVP - Mock Data)")

    with st.form("valuation_form"):
        col1, col2 = st.columns(2)
        with col1:
            region = st.selectbox("지역", options=REGIONS)
            property_type = st.selectbox("유형", options=PROPERTY_TYPES)
            area_sqm = st.number_input(
                "전용면적 (㎡)",
                min_value=10.0,
                max_value=300.0,
                value=84.0,
                step=1.0,
            )
        with col2:
            floor = st.number_input(
                "층", min_value=1, max_value=70, value=10
            )
            construction_year = st.number_input(
                "준공연도", min_value=1980, max_value=2026, value=2015
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
        except ValueError as exc:
            st.error(f"입력 오류: {exc}")
            logger.warning("Valuation input error: %s", exc)
            return

    _render_result()


def _render_result() -> None:
    """Display the valuation result and factor breakdown table."""

    result = st.session_state.get("last_valuation_result")
    prop = st.session_state.get("last_valuation_property")
    if result is None or prop is None:
        return

    st.divider()

    # Headline metric
    st.metric(
        label="감정가 (예상)",
        value=f"{result.estimated_value_krw:,} 원",
    )
    st.caption(
        f"{prop.region} / {prop.property_type} / "
        f"{prop.area_sqm}㎡ / {prop.floor}층 / {prop.construction_year}년"
    )

    # Factor breakdown table
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
    # Total row
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

    # 3D building visualization
    st.subheader("건물 구조")
    from valuation.building_visualization import build_building_figure

    fig = build_building_figure(
        floor=prop.floor,
        area_sqm=prop.area_sqm,
        property_type=prop.property_type,
    )
    st.plotly_chart(fig, use_container_width=True)
