"""
Apartment complex search component.

Renders a text input + selectbox pair for searching the mock complex
directory. Returns the selected Complex object or None if no match.
"""

from __future__ import annotations

import streamlit as st

from valuation.data.complex_directory import search_complexes
from valuation.data.mock.complexes import Complex


def render_complex_search(key_prefix: str = "complex_search") -> Complex | None:
    """
    Render a complex search text input and result selectbox.

    Params:
        key_prefix: Unique prefix for Streamlit widget keys to avoid
                    DuplicateWidgetID errors when embedded multiple times.

    Returns:
        Selected Complex object, or None if the query is empty or yields
        no results.
    """
    query = st.text_input(
        "단지명 검색 (예: 반포 자이, 잠실 엘스, 판교)",
        placeholder="단지명 또는 지역명 입력...",
        key=f"{key_prefix}_query",
    )

    if not query or not query.strip():
        return None

    results = search_complexes(query.strip(), limit=10)
    if not results:
        st.caption("검색 결과가 없습니다. 다른 키워드를 시도해 보세요.")
        return None

    options = {c.name: c for c in results}
    chosen_name = st.selectbox(
        "단지 선택",
        options=list(options.keys()),
        key=f"{key_prefix}_select",
    )
    return options.get(chosen_name)
