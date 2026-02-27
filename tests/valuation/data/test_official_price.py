"""
Tests for valuation/data/official_price.py -- mock official land prices.

Covers exact matches, prefix matching, fallback behavior, and data integrity.
"""

from __future__ import annotations

import pytest

from valuation.data.official_price import (
    DEFAULT_OFFICIAL_PRICE_PER_SQM,
    MOCK_OFFICIAL_PRICE_PER_SQM,
    get_official_land_price_per_sqm,
)


class TestGetOfficialLandPricePerSqm:
    """Tests for get_official_land_price_per_sqm()."""

    def test_gangnam_exact(self):
        assert get_official_land_price_per_sqm("서울 강남구") == 12_500_000

    def test_seocho_exact(self):
        assert get_official_land_price_per_sqm("서울 서초구") == 10_800_000

    def test_gyeonggi_seongnam(self):
        assert get_official_land_price_per_sqm("경기 성남시") == 4_500_000

    def test_busan_haeundae(self):
        assert get_official_land_price_per_sqm("부산 해운대구") == 3_500_000

    def test_prefix_match_gangnam_subdistrict(self):
        """Longer region that starts with known prefix."""
        assert get_official_land_price_per_sqm("서울 강남구 역삼동") == 12_500_000

    def test_prefix_fallback_to_seoul(self):
        """Unknown Seoul district falls back to '서울'."""
        assert get_official_land_price_per_sqm("서울 중구") == 6_000_000

    def test_prefix_fallback_to_gyeonggi(self):
        """Unknown Gyeonggi city falls back to '경기'."""
        assert get_official_land_price_per_sqm("경기 안양시") == 3_000_000

    def test_prefix_fallback_to_busan(self):
        assert get_official_land_price_per_sqm("부산 사하구") == 2_500_000

    def test_unknown_region_uses_default(self):
        assert get_official_land_price_per_sqm("제주") == DEFAULT_OFFICIAL_PRICE_PER_SQM

    def test_empty_region_uses_default(self):
        assert get_official_land_price_per_sqm("") == DEFAULT_OFFICIAL_PRICE_PER_SQM

    def test_none_region_uses_default(self):
        assert get_official_land_price_per_sqm(None) == DEFAULT_OFFICIAL_PRICE_PER_SQM

    def test_whitespace_region_uses_default(self):
        assert get_official_land_price_per_sqm("   ") == DEFAULT_OFFICIAL_PRICE_PER_SQM

    def test_all_mock_prices_positive(self):
        for region, price in MOCK_OFFICIAL_PRICE_PER_SQM.items():
            assert price > 0, f"Non-positive price for {region}"

    def test_default_price_positive(self):
        assert DEFAULT_OFFICIAL_PRICE_PER_SQM > 0

    def test_specific_regions_higher_than_default(self):
        """All specific Seoul regions should be higher than the global default."""
        for region, price in MOCK_OFFICIAL_PRICE_PER_SQM.items():
            if region.startswith("서울"):
                assert price >= DEFAULT_OFFICIAL_PRICE_PER_SQM
