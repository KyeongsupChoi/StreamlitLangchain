"""
Tests for valuation/factor_rules.py -- base price, floor, age, and size factors.

Covers lookup logic, boundary values, prefix matching, and fallback behavior.
"""

from __future__ import annotations

from datetime import date

import pytest

from valuation.factor_rules import (
    AGE_DEPRECIATION_CAP,
    AGE_DEPRECIATION_RATE_PER_YEAR,
    BASE_PRICE_PER_SQM,
    DEFAULT_BASE_PRICE_PER_SQM,
    FLOOR_FACTOR_MAP,
    SIZE_BAND_RULES,
    get_age_factor,
    get_base_price_per_sqm,
    get_floor_factor,
    get_size_factor,
)


class TestGetBasePricePerSqm:
    """Tests for get_base_price_per_sqm region/type lookup."""

    def test_exact_match_gangnam_apt(self):
        assert get_base_price_per_sqm("서울 강남구", "아파트") == 1_500_000

    def test_exact_match_gangnam_officetel(self):
        assert get_base_price_per_sqm("서울 강남구", "오피스텔") == 1_350_000

    def test_exact_match_seocho_house(self):
        assert get_base_price_per_sqm("서울 서초구", "단독주택") == 1_700_000

    def test_exact_match_busan_apt(self):
        assert get_base_price_per_sqm("부산", "아파트") == 750_000

    def test_exact_match_gyeonggi_officetel(self):
        assert get_base_price_per_sqm("경기", "오피스텔") == 720_000

    def test_prefix_match_gangnam_subdistrict(self):
        """Region that starts with '서울 강남구' should match the specific entry."""
        assert get_base_price_per_sqm("서울 강남구 역삼동", "아파트") == 1_500_000

    def test_prefix_fallback_to_seoul(self):
        """Unknown Seoul district falls back to '서울' prefix."""
        assert get_base_price_per_sqm("서울 종로구", "아파트") == 1_200_000

    def test_prefix_fallback_gyeonggi_seongnam(self):
        """경기 성남시 matches the '경기' prefix."""
        assert get_base_price_per_sqm("경기 성남시", "아파트") == 800_000

    def test_unknown_region_uses_default(self):
        """Completely unknown region falls back to DEFAULT_BASE_PRICE_PER_SQM."""
        assert get_base_price_per_sqm("제주", "아파트") == DEFAULT_BASE_PRICE_PER_SQM["아파트"]

    def test_unknown_region_officetel_default(self):
        assert get_base_price_per_sqm("대전", "오피스텔") == DEFAULT_BASE_PRICE_PER_SQM["오피스텔"]

    def test_unknown_region_house_default(self):
        assert get_base_price_per_sqm("대구", "단독주택") == DEFAULT_BASE_PRICE_PER_SQM["단독주택"]

    def test_empty_region_uses_default(self):
        assert get_base_price_per_sqm("", "아파트") == DEFAULT_BASE_PRICE_PER_SQM["아파트"]

    def test_none_region_uses_default(self):
        assert get_base_price_per_sqm(None, "아파트") == DEFAULT_BASE_PRICE_PER_SQM["아파트"]

    def test_whitespace_region_uses_default(self):
        assert get_base_price_per_sqm("   ", "아파트") == DEFAULT_BASE_PRICE_PER_SQM["아파트"]


class TestGetFloorFactor:
    """Tests for get_floor_factor multiplier lookup."""

    def test_first_floor_discount(self):
        assert get_floor_factor(1) == 0.95

    def test_low_floors(self):
        for floor in (2, 3, 4):
            assert get_floor_factor(floor) == 0.98

    def test_mid_floors_neutral(self):
        for floor in (5, 10, 15):
            assert get_floor_factor(floor) == 1.0

    def test_high_floors_premium(self):
        for floor in (16, 20, 50):
            assert get_floor_factor(floor) == 1.02

    def test_boundary_floor_4_to_5(self):
        assert get_floor_factor(4) == 0.98
        assert get_floor_factor(5) == 1.0

    def test_boundary_floor_15_to_16(self):
        assert get_floor_factor(15) == 1.0
        assert get_floor_factor(16) == 1.02

    def test_invalid_floor_zero_falls_back(self):
        """Floor < 1 returns first band factor."""
        assert get_floor_factor(0) == FLOOR_FACTOR_MAP[0][2]

    def test_invalid_floor_negative(self):
        assert get_floor_factor(-5) == FLOOR_FACTOR_MAP[0][2]


class TestGetAgeFactor:
    """Tests for get_age_factor depreciation calculation."""

    def test_brand_new_building(self):
        current_year = date.today().year
        assert get_age_factor(current_year) == 1.0

    def test_future_year_no_depreciation(self):
        future = date.today().year + 5
        assert get_age_factor(future) == 1.0

    def test_ten_years_old(self):
        year = date.today().year - 10
        expected = round(1.0 - 10 * AGE_DEPRECIATION_RATE_PER_YEAR, 4)
        assert get_age_factor(year) == expected

    def test_one_year_old(self):
        year = date.today().year - 1
        expected = round(1.0 - 1 * AGE_DEPRECIATION_RATE_PER_YEAR, 4)
        assert get_age_factor(year) == expected

    def test_depreciation_cap(self):
        """Very old buildings hit the 20% cap."""
        year = date.today().year - 100
        expected = round(1.0 - AGE_DEPRECIATION_CAP, 4)
        assert get_age_factor(year) == expected

    def test_exactly_at_cap_boundary(self):
        """Exactly at the cap boundary (40 years at 0.5%/year = 20%)."""
        years_to_cap = int(AGE_DEPRECIATION_CAP / AGE_DEPRECIATION_RATE_PER_YEAR)
        year = date.today().year - years_to_cap
        expected = round(1.0 - AGE_DEPRECIATION_CAP, 4)
        assert get_age_factor(year) == expected

    def test_just_below_cap(self):
        years_to_cap = int(AGE_DEPRECIATION_CAP / AGE_DEPRECIATION_RATE_PER_YEAR)
        year = date.today().year - (years_to_cap - 1)
        expected = round(1.0 - (years_to_cap - 1) * AGE_DEPRECIATION_RATE_PER_YEAR, 4)
        assert get_age_factor(year) == expected

    def test_result_within_valid_range(self):
        """Age factor should always be in (1-cap, 1.0]."""
        for years_ago in range(0, 80):
            factor = get_age_factor(date.today().year - years_ago)
            assert 1.0 - AGE_DEPRECIATION_CAP <= factor <= 1.0


class TestGetSizeFactor:
    """Tests for get_size_factor size band lookup."""

    def test_small_unit_discount(self):
        assert get_size_factor(60.0) == 0.98

    def test_boundary_small_to_neutral(self):
        assert get_size_factor(84.99) == 0.98
        assert get_size_factor(85.0) == 1.0

    def test_neutral_band(self):
        for area in (85.0, 90.0, 100.0):
            assert get_size_factor(area) == 1.0

    def test_boundary_neutral_to_large(self):
        assert get_size_factor(100.0) == 1.0
        assert get_size_factor(100.01) == 0.99

    def test_large_unit_slight_discount(self):
        assert get_size_factor(120.0) == 0.99

    def test_very_large_unit_discount(self):
        assert get_size_factor(150.0) == 0.97

    def test_boundary_large_to_very_large(self):
        assert get_size_factor(130.0) == 0.99
        assert get_size_factor(130.01) == 0.97

    def test_zero_area_fallback(self):
        assert get_size_factor(0) == SIZE_BAND_RULES[0][2]

    def test_negative_area_fallback(self):
        assert get_size_factor(-10.0) == SIZE_BAND_RULES[0][2]


class TestConstants:
    """Verify constants have expected structure and values."""

    def test_base_price_dict_not_empty(self):
        assert len(BASE_PRICE_PER_SQM) > 0

    def test_base_price_all_positive(self):
        for key, val in BASE_PRICE_PER_SQM.items():
            assert val > 0, f"Non-positive price for {key}"

    def test_default_base_price_covers_all_types(self):
        for ptype in ("아파트", "오피스텔", "단독주택"):
            assert ptype in DEFAULT_BASE_PRICE_PER_SQM

    def test_floor_factor_map_sorted(self):
        lows = [low for low, _, _ in FLOOR_FACTOR_MAP]
        assert lows == sorted(lows)

    def test_floor_factor_map_no_gaps(self):
        for i in range(len(FLOOR_FACTOR_MAP) - 1):
            _, high, _ = FLOOR_FACTOR_MAP[i]
            next_low, _, _ = FLOOR_FACTOR_MAP[i + 1]
            assert next_low == high + 1, f"Gap between {high} and {next_low}"

    def test_size_band_rules_sorted(self):
        lows = [low for low, _, _ in SIZE_BAND_RULES]
        assert lows == sorted(lows)

    def test_depreciation_rate_positive(self):
        assert AGE_DEPRECIATION_RATE_PER_YEAR > 0

    def test_depreciation_cap_between_0_and_1(self):
        assert 0 < AGE_DEPRECIATION_CAP < 1
