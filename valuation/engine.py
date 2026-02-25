"""
Deterministic valuation engine for Korean real estate.

Project role:
  Takes a Property specification and returns a ValuationResult with an
  estimated value in KRW and a step-by-step factor breakdown showing how
  each factor (base price, floor, age, size, comparables) contributed to
  the final estimate. No LLM required.
"""

from __future__ import annotations

import logging

from valuation.data.comparables import get_comparables
from valuation.factor_rules import (
    get_age_factor,
    get_base_price_per_sqm,
    get_floor_factor,
    get_size_factor,
)
from valuation.models import FactorContribution, Property, ValuationResult

logger = logging.getLogger(__name__)

COMPARABLES_BLEND_WEIGHT = 0.3


def run_valuation(property_spec: Property) -> ValuationResult:
    """
    Compute an estimated property value with a full factor breakdown.

    The engine applies factors sequentially: base price -> floor -> age -> size,
    then optionally blends in comparable transaction data. Each step is recorded
    as a FactorContribution so the UI can render a transparent breakdown.

    Params:
        property_spec: Property input (region, type, area, floor, year).

    Returns:
        ValuationResult with estimated_value_krw and factor_breakdown.
    """
    breakdown: list[FactorContribution] = []

    # 1. Base price
    base_per_sqm = get_base_price_per_sqm(
        property_spec.region, property_spec.property_type
    )
    base_total = int(base_per_sqm * property_spec.area_sqm)
    breakdown.append(
        FactorContribution(
            name="기준가격",
            multiplier_or_value=float(base_per_sqm),
            contribution_krw=base_total,
            description=f"{base_per_sqm:,} 원/㎡ x {property_spec.area_sqm} ㎡",
        )
    )
    running_total = base_total

    # 2. Floor factor
    floor_factor = get_floor_factor(property_spec.floor)
    floor_adjusted = int(running_total * floor_factor)
    floor_delta = floor_adjusted - running_total
    breakdown.append(
        FactorContribution(
            name="층계수",
            multiplier_or_value=floor_factor,
            contribution_krw=floor_delta,
            description=f"{property_spec.floor}층 -> x{floor_factor}",
        )
    )
    running_total = floor_adjusted

    # 3. Age depreciation
    age_factor = get_age_factor(property_spec.construction_year)
    age_adjusted = int(running_total * age_factor)
    age_delta = age_adjusted - running_total
    breakdown.append(
        FactorContribution(
            name="연도계수",
            multiplier_or_value=age_factor,
            contribution_krw=age_delta,
            description=f"{property_spec.construction_year}년 준공 -> x{age_factor}",
        )
    )
    running_total = age_adjusted

    # 4. Size band
    size_factor = get_size_factor(property_spec.area_sqm)
    size_adjusted = int(running_total * size_factor)
    size_delta = size_adjusted - running_total
    breakdown.append(
        FactorContribution(
            name="면적계수",
            multiplier_or_value=size_factor,
            contribution_krw=size_delta,
            description=f"{property_spec.area_sqm} ㎡ -> x{size_factor}",
        )
    )
    running_total = size_adjusted

    # 5. Comparables blend
    comparables = get_comparables(
        property_spec.region, property_spec.property_type, property_spec.area_sqm
    )
    data_sources = "목데이터"
    if comparables:
        avg_price_per_sqm = sum(
            c["price_krw"] / c["area_sqm"] for c in comparables
        ) / len(comparables)
        comparable_estimate = int(avg_price_per_sqm * property_spec.area_sqm)
        blended = int(
            running_total * (1 - COMPARABLES_BLEND_WEIGHT)
            + comparable_estimate * COMPARABLES_BLEND_WEIGHT
        )
        comp_delta = blended - running_total
        breakdown.append(
            FactorContribution(
                name="실거래가 반영",
                multiplier_or_value=COMPARABLES_BLEND_WEIGHT,
                contribution_krw=comp_delta,
                description=(
                    f"실거래가 {len(comparables)}건 평균 "
                    f"{int(avg_price_per_sqm):,} 원/㎡, "
                    f"반영비중 {COMPARABLES_BLEND_WEIGHT:.0%}"
                ),
            )
        )
        running_total = blended
        data_sources = f"목데이터 (실거래가 {len(comparables)}건)"

    logger.info(
        "Valuation: region=%s type=%s area=%.1f floor=%d year=%d -> %s KRW",
        property_spec.region,
        property_spec.property_type,
        property_spec.area_sqm,
        property_spec.floor,
        property_spec.construction_year,
        f"{running_total:,}",
    )

    return ValuationResult(
        estimated_value_krw=running_total,
        currency="KRW",
        factor_breakdown=tuple(breakdown),
        data_sources_used=data_sources,
    )
