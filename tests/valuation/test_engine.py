"""
Tests for valuation/engine.py -- run_valuation() end-to-end.

Covers full valuation pipeline, factor breakdown correctness, and
comparables blending behavior.
"""

from __future__ import annotations

import pytest

from valuation.engine import COMPARABLES_BLEND_WEIGHT, run_valuation
from valuation.models import Property, ValuationResult


class TestRunValuation:
    """End-to-end tests for the valuation engine."""

    def test_returns_valuation_result(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        assert isinstance(result, ValuationResult)

    def test_positive_estimated_value(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        assert result.estimated_value_krw > 0

    def test_currency_is_krw(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        assert result.currency == "KRW"

    def test_breakdown_contains_base_price(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        names = [f.name for f in result.factor_breakdown]
        assert "기준가격" in names

    def test_breakdown_contains_floor_factor(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        names = [f.name for f in result.factor_breakdown]
        assert "층계수" in names

    def test_breakdown_contains_age_factor(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        names = [f.name for f in result.factor_breakdown]
        assert "연도계수" in names

    def test_breakdown_contains_size_factor(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        names = [f.name for f in result.factor_breakdown]
        assert "면적계수" in names

    def test_breakdown_has_comparables_when_data_exists(self, gangnam_apt):
        """Gangnam apartment has mock comparable data."""
        result = run_valuation(gangnam_apt)
        names = [f.name for f in result.factor_breakdown]
        assert "실거래가 반영" in names

    def test_breakdown_no_comparables_for_unknown_region(self):
        """Region with no comparable data should have no comparables factor."""
        prop = Property(
            region="제주", property_type="아파트",
            area_sqm=84.0, floor=5, construction_year=2020,
        )
        result = run_valuation(prop)
        names = [f.name for f in result.factor_breakdown]
        assert "실거래가 반영" not in names

    def test_data_sources_mentions_comparables(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        assert "실거래가" in result.data_sources_used

    def test_data_sources_mock_for_unknown_region(self):
        prop = Property(
            region="제주", property_type="아파트",
            area_sqm=84.0, floor=5, construction_year=2020,
        )
        result = run_valuation(prop)
        assert result.data_sources_used == "목데이터"

    def test_base_price_contributes_correctly(self, gangnam_apt):
        result = run_valuation(gangnam_apt)
        base_factor = result.factor_breakdown[0]
        assert base_factor.name == "기준가격"
        expected = int(1_500_000 * 84.0)
        assert base_factor.contribution_krw == expected

    def test_floor_10_neutral_contribution(self, gangnam_apt):
        """Floor 10 is in the 5-15 band (factor 1.0), so contribution is 0."""
        result = run_valuation(gangnam_apt)
        floor_factor = result.factor_breakdown[1]
        assert floor_factor.name == "층계수"
        assert floor_factor.contribution_krw == 0

    def test_first_floor_discount(self):
        prop = Property(
            region="서울 강남구", property_type="아파트",
            area_sqm=84.0, floor=1, construction_year=2026,
        )
        result = run_valuation(prop)
        floor_factor = result.factor_breakdown[1]
        assert floor_factor.contribution_krw < 0

    def test_high_floor_premium(self):
        prop = Property(
            region="서울 강남구", property_type="아파트",
            area_sqm=84.0, floor=20, construction_year=2026,
        )
        result = run_valuation(prop)
        floor_factor = result.factor_breakdown[1]
        assert floor_factor.contribution_krw > 0

    def test_different_regions_different_values(self):
        gangnam = Property(
            region="서울 강남구", property_type="아파트",
            area_sqm=84.0, floor=10, construction_year=2020,
        )
        busan = Property(
            region="부산 해운대구", property_type="아파트",
            area_sqm=84.0, floor=10, construction_year=2020,
        )
        assert run_valuation(gangnam).estimated_value_krw != run_valuation(busan).estimated_value_krw

    def test_different_types_different_values(self):
        apt = Property(
            region="서울 강남구", property_type="아파트",
            area_sqm=84.0, floor=5, construction_year=2020,
        )
        officetel = Property(
            region="서울 강남구", property_type="오피스텔",
            area_sqm=84.0, floor=5, construction_year=2020,
        )
        assert run_valuation(apt).estimated_value_krw != run_valuation(officetel).estimated_value_krw

    def test_older_building_lower_value(self):
        new = Property(
            region="서울 강남구", property_type="아파트",
            area_sqm=84.0, floor=10, construction_year=2025,
        )
        old = Property(
            region="서울 강남구", property_type="아파트",
            area_sqm=84.0, floor=10, construction_year=1990,
        )
        assert run_valuation(new).estimated_value_krw > run_valuation(old).estimated_value_krw

    def test_seocho_officetel(self, seocho_officetel):
        result = run_valuation(seocho_officetel)
        assert result.estimated_value_krw > 0
        assert len(result.factor_breakdown) >= 4

    def test_busan_house(self, busan_house):
        result = run_valuation(busan_house)
        assert result.estimated_value_krw > 0


class TestComparablesBlendWeight:
    """Tests for the COMPARABLES_BLEND_WEIGHT constant."""

    def test_weight_between_0_and_1(self):
        assert 0 < COMPARABLES_BLEND_WEIGHT < 1

    def test_weight_is_thirty_percent(self):
        assert COMPARABLES_BLEND_WEIGHT == 0.3
