"""
Data models for Korean real estate valuation.

Project role:
  Defines the property input spec, factor contribution record, and valuation
  result structure used by the valuation engine and UI.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

PropertyType = Literal["아파트", "오피스텔", "단독주택"]


@dataclass(frozen=True)
class Property:
    """
    Property specification used as input to the valuation engine.

    Attributes:
        region: Administrative region (e.g. "서울 강남구", "경기 성남시").
        property_type: One of 아파트, 오피스텔, 단독주택.
        area_sqm: Exclusive use area in square meters.
        floor: Floor number (1-based).
        construction_year: Year the building was completed.

    Raises:
        ValueError: If area_sqm <= 0 or construction_year is out of reasonable range.
    """

    region: str
    property_type: PropertyType
    area_sqm: float
    floor: int
    construction_year: int

    def __post_init__(self) -> None:
        if self.area_sqm <= 0:
            raise ValueError("area_sqm must be positive")
        if not (1980 <= self.construction_year <= 2030):
            raise ValueError("construction_year must be between 1980 and 2030")
        if self.floor < 1:
            raise ValueError("floor must be at least 1")
        if not self.region or not self.region.strip():
            raise ValueError("region must be non-empty")
        if self.property_type not in ("아파트", "오피스텔", "단독주택"):
            raise ValueError(
                "property_type must be one of: 아파트, 오피스텔, 단독주택"
            )


@dataclass(frozen=True)
class FactorContribution:
    """
    Single factor's contribution to the valuation total.

    Attributes:
        name: Korean label for the factor (e.g. "기준가격", "층계수").
        multiplier_or_value: Factor applied (e.g. unit price per ㎡ or multiplier).
        contribution_krw: This factor's contribution in KRW.
        description: Optional short explanation (e.g. "15층 기준 1.0").
    """

    name: str
    multiplier_or_value: float
    contribution_krw: int
    description: str | None = None


@dataclass(frozen=True)
class ValuationResult:
    """
    Full result of a valuation run, including factor breakdown.

    Attributes:
        estimated_value_krw: Total estimated value in Korean won.
        currency: Currency code (e.g. "KRW").
        factor_breakdown: Ordered list of factor contributions.
        data_sources_used: Human-readable summary (e.g. "목데이터 (실거래가 3건)").
    """

    estimated_value_krw: int
    currency: str
    factor_breakdown: tuple[FactorContribution, ...]
    data_sources_used: str

    def __post_init__(self) -> None:
        if self.estimated_value_krw < 0:
            raise ValueError("estimated_value_krw must be non-negative")
        if not self.currency or not self.currency.strip():
            raise ValueError("currency must be non-empty")
