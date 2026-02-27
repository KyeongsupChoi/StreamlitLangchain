"""
LangChain tools for Korean real estate valuation domain.

Project role:
  Exposes the valuation engine, comparable transactions, official land prices,
  and factor rules as LangChain @tool functions for use in a ReAct agent loop.
  Each tool returns a formatted Korean string suitable for LLM consumption.
"""

from __future__ import annotations

import logging

from langchain_core.tools import tool

from valuation.data.comparables import get_comparables
from valuation.data.official_price import get_official_land_price_per_sqm
from valuation.engine import COMPARABLES_BLEND_WEIGHT, run_valuation
from valuation.factor_rules import (
    AGE_DEPRECIATION_CAP,
    AGE_DEPRECIATION_RATE_PER_YEAR,
    BASE_PRICE_PER_SQM,
    DEFAULT_BASE_PRICE_PER_SQM,
    FLOOR_FACTOR_MAP,
    SIZE_BAND_RULES,
)
from valuation.models import Property

logger = logging.getLogger(__name__)


@tool
def estimate_property_value(
    region: str,
    property_type: str,
    area_sqm: float,
    floor: int,
    construction_year: int,
) -> str:
    """Estimate the market value of a Korean property using the valuation engine.

    Args:
        region: Administrative region (e.g. "서울 강남구", "경기 성남시").
        property_type: One of 아파트, 오피스텔, 단독주택.
        area_sqm: Exclusive use area in square meters.
        floor: Floor number (1-based).
        construction_year: Year the building was completed (1980-2030).

    Returns:
        Formatted Korean text with estimated value and factor breakdown.
    """
    try:
        prop = Property(
            region=region,
            property_type=property_type,
            area_sqm=area_sqm,
            floor=floor,
            construction_year=construction_year,
        )
        result = run_valuation(prop)
    except ValueError as exc:
        logger.warning("Valuation input error: %s", exc)
        return f"입력 오류: {exc}"

    lines = [
        f"감정가: {result.estimated_value_krw:,} 원",
        f"데이터 출처: {result.data_sources_used}",
        "",
        "요인 분석:",
    ]
    for factor in result.factor_breakdown:
        lines.append(
            f"  - {factor.name}: {factor.contribution_krw:+,} 원 "
            f"({factor.description})"
        )

    logger.info(
        "estimate_property_value: %s %s %.1f sqm -> %s KRW",
        region, property_type, area_sqm, f"{result.estimated_value_krw:,}",
    )
    return "\n".join(lines)


@tool
def search_comparables(
    region: str,
    property_type: str,
    area_sqm: float = 84.0,
) -> str:
    """Search recent comparable transactions for a Korean property.

    Args:
        region: Administrative region (e.g. "서울 강남구").
        property_type: One of 아파트, 오피스텔, 단독주택.
        area_sqm: Optional area filter in square meters (default 84.0).

    Returns:
        Formatted list of comparable transactions or a no-data message.
    """
    comparables = get_comparables(region, property_type, area_sqm)

    if not comparables:
        return "해당 지역의 실거래 데이터가 없습니다."

    lines = [f"{region} {property_type} 최근 실거래 사례 ({len(comparables)}건):"]
    for idx, comp in enumerate(comparables, 1):
        lines.append(
            f"  {idx}. {comp['price_krw']:,} 원 | "
            f"{comp['area_sqm']} ㎡ | "
            f"{comp['date']} | "
            f"{comp['floor']}층"
        )

    logger.info("search_comparables: %s %s -> %d results", region, property_type, len(comparables))
    return "\n".join(lines)


@tool
def lookup_official_land_price(region: str) -> str:
    """Look up the official land price (공시지가) for a Korean region.

    Args:
        region: Administrative region (e.g. "서울 강남구", "경기 성남시").

    Returns:
        Formatted official land price per square meter.
    """
    price = get_official_land_price_per_sqm(region)
    logger.info("lookup_official_land_price: %s -> %s KRW/sqm", region, f"{price:,}")
    return f"{region} 공시지가: {price:,} 원/㎡"


@tool
def explain_valuation_factors() -> str:
    """Explain all factors and rules used in the Korean real estate valuation engine.

    Returns:
        Korean explanation of base prices, floor factors, age depreciation,
        size bands, and comparables blending weight.
    """
    # Base prices
    base_lines = []
    for (reg, ptype), price in sorted(BASE_PRICE_PER_SQM.items()):
        base_lines.append(f"    {reg} / {ptype}: {price:,} 원/㎡")
    default_lines = []
    for ptype, price in sorted(DEFAULT_BASE_PRICE_PER_SQM.items()):
        default_lines.append(f"    {ptype}: {price:,} 원/㎡")

    # Floor factors
    floor_lines = []
    for low, high, factor in FLOOR_FACTOR_MAP:
        high_label = f"{high}" if high < 999 else "이상"
        if low == high:
            floor_lines.append(f"    {low}층: x{factor}")
        else:
            floor_lines.append(f"    {low}-{high_label}층: x{factor}")

    # Size bands
    size_lines = []
    for low, high, factor in SIZE_BAND_RULES:
        high_label = f"{high}" if high < 9999 else "이상"
        size_lines.append(f"    {low}-{high_label} ㎡: x{factor}")

    return "\n".join([
        "한국 부동산 감정 평가 요인:",
        "",
        "1. 기준가격 (원/㎡):",
        *base_lines,
        "  기본값:",
        *default_lines,
        "",
        "2. 층계수:",
        *floor_lines,
        "",
        f"3. 연도계수: 연간 감가율 {AGE_DEPRECIATION_RATE_PER_YEAR:.1%}, "
        f"최대 {AGE_DEPRECIATION_CAP:.0%} 감가",
        "",
        "4. 면적계수:",
        *size_lines,
        "",
        f"5. 실거래가 반영: 비중 {COMPARABLES_BLEND_WEIGHT:.0%} "
        f"(실거래 데이터가 있는 경우)",
    ])


REALESTATE_TOOLS = [
    estimate_property_value,
    search_comparables,
    lookup_official_land_price,
    explain_valuation_factors,
]
