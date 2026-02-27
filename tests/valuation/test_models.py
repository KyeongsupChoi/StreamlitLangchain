"""
Tests for valuation/models.py -- Property, FactorContribution, ValuationResult.

Covers construction validation, boundary values, and frozen dataclass behavior.
"""

from __future__ import annotations

import pytest

from valuation.models import FactorContribution, Property, ValuationResult


class TestProperty:
    """Tests for the Property dataclass."""

    def test_valid_construction(self, gangnam_apt):
        assert gangnam_apt.region == "서울 강남구"
        assert gangnam_apt.property_type == "아파트"
        assert gangnam_apt.area_sqm == 84.0
        assert gangnam_apt.floor == 10
        assert gangnam_apt.construction_year == 2015

    def test_all_property_types(self):
        for ptype in ("아파트", "오피스텔", "단독주택"):
            p = Property(
                region="서울 강남구",
                property_type=ptype,
                area_sqm=50.0,
                floor=1,
                construction_year=2020,
            )
            assert p.property_type == ptype

    def test_boundary_construction_year_min(self):
        p = Property(
            region="서울", property_type="아파트",
            area_sqm=50.0, floor=1, construction_year=1980,
        )
        assert p.construction_year == 1980

    def test_boundary_construction_year_max(self):
        p = Property(
            region="서울", property_type="아파트",
            area_sqm=50.0, floor=1, construction_year=2030,
        )
        assert p.construction_year == 2030

    def test_boundary_floor_min(self):
        p = Property(
            region="서울", property_type="아파트",
            area_sqm=50.0, floor=1, construction_year=2020,
        )
        assert p.floor == 1

    def test_boundary_area_small(self):
        p = Property(
            region="서울", property_type="아파트",
            area_sqm=0.01, floor=1, construction_year=2020,
        )
        assert p.area_sqm == 0.01

    def test_frozen_immutability(self, gangnam_apt):
        with pytest.raises(AttributeError):
            gangnam_apt.region = "서울 서초구"

    # --- Validation errors ---

    def test_invalid_area_zero(self):
        with pytest.raises(ValueError, match="area_sqm must be positive"):
            Property(
                region="서울", property_type="아파트",
                area_sqm=0, floor=1, construction_year=2020,
            )

    def test_invalid_area_negative(self):
        with pytest.raises(ValueError, match="area_sqm must be positive"):
            Property(
                region="서울", property_type="아파트",
                area_sqm=-10.0, floor=1, construction_year=2020,
            )

    def test_invalid_construction_year_too_old(self):
        with pytest.raises(ValueError, match="construction_year must be between"):
            Property(
                region="서울", property_type="아파트",
                area_sqm=50.0, floor=1, construction_year=1979,
            )

    def test_invalid_construction_year_too_new(self):
        with pytest.raises(ValueError, match="construction_year must be between"):
            Property(
                region="서울", property_type="아파트",
                area_sqm=50.0, floor=1, construction_year=2031,
            )

    def test_invalid_floor_zero(self):
        with pytest.raises(ValueError, match="floor must be at least 1"):
            Property(
                region="서울", property_type="아파트",
                area_sqm=50.0, floor=0, construction_year=2020,
            )

    def test_invalid_floor_negative(self):
        with pytest.raises(ValueError, match="floor must be at least 1"):
            Property(
                region="서울", property_type="아파트",
                area_sqm=50.0, floor=-1, construction_year=2020,
            )

    def test_invalid_empty_region(self):
        with pytest.raises(ValueError, match="region must be non-empty"):
            Property(
                region="", property_type="아파트",
                area_sqm=50.0, floor=1, construction_year=2020,
            )

    def test_invalid_whitespace_region(self):
        with pytest.raises(ValueError, match="region must be non-empty"):
            Property(
                region="   ", property_type="아파트",
                area_sqm=50.0, floor=1, construction_year=2020,
            )

    def test_invalid_property_type(self):
        with pytest.raises(ValueError, match="property_type must be one of"):
            Property(
                region="서울", property_type="빌라",
                area_sqm=50.0, floor=1, construction_year=2020,
            )


class TestFactorContribution:
    """Tests for the FactorContribution dataclass."""

    def test_basic_construction(self):
        fc = FactorContribution(
            name="기준가격",
            multiplier_or_value=1_500_000.0,
            contribution_krw=126_000_000,
            description="1,500,000 원/㎡ x 84.0 ㎡",
        )
        assert fc.name == "기준가격"
        assert fc.contribution_krw == 126_000_000
        assert fc.multiplier_or_value == 1_500_000.0

    def test_negative_contribution(self):
        fc = FactorContribution(
            name="연도계수",
            multiplier_or_value=0.95,
            contribution_krw=-6_300_000,
        )
        assert fc.contribution_krw == -6_300_000

    def test_optional_description_default(self):
        fc = FactorContribution(
            name="test", multiplier_or_value=1.0, contribution_krw=0,
        )
        assert fc.description is None

    def test_frozen(self):
        fc = FactorContribution(
            name="test", multiplier_or_value=1.0, contribution_krw=0,
        )
        with pytest.raises(AttributeError):
            fc.name = "changed"


class TestValuationResult:
    """Tests for the ValuationResult dataclass."""

    def test_basic_construction(self):
        result = ValuationResult(
            estimated_value_krw=500_000_000,
            currency="KRW",
            factor_breakdown=(
                FactorContribution(
                    name="기준가격", multiplier_or_value=1_000_000.0,
                    contribution_krw=84_000_000,
                ),
            ),
            data_sources_used="목데이터",
        )
        assert result.estimated_value_krw == 500_000_000
        assert result.currency == "KRW"
        assert len(result.factor_breakdown) == 1

    def test_zero_value_allowed(self):
        result = ValuationResult(
            estimated_value_krw=0, currency="KRW",
            factor_breakdown=(), data_sources_used="none",
        )
        assert result.estimated_value_krw == 0

    def test_invalid_negative_value(self):
        with pytest.raises(ValueError, match="estimated_value_krw must be non-negative"):
            ValuationResult(
                estimated_value_krw=-1, currency="KRW",
                factor_breakdown=(), data_sources_used="none",
            )

    def test_invalid_empty_currency(self):
        with pytest.raises(ValueError, match="currency must be non-empty"):
            ValuationResult(
                estimated_value_krw=100, currency="",
                factor_breakdown=(), data_sources_used="none",
            )

    def test_invalid_whitespace_currency(self):
        with pytest.raises(ValueError, match="currency must be non-empty"):
            ValuationResult(
                estimated_value_krw=100, currency="   ",
                factor_breakdown=(), data_sources_used="none",
            )

    def test_frozen(self):
        result = ValuationResult(
            estimated_value_krw=100, currency="KRW",
            factor_breakdown=(), data_sources_used="none",
        )
        with pytest.raises(AttributeError):
            result.estimated_value_krw = 200
