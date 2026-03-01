"""
Tests for valuation/data/comparables.py -- mock comparable transaction data.

Covers data retrieval, empty results, and record structure.
"""

from __future__ import annotations

import pytest

from valuation.data.comparables import MOCK_COMPARABLES, get_comparables, get_price_history


class TestGetComparables:
    """Tests for get_comparables()."""

    def test_gangnam_apt_returns_data(self):
        result = get_comparables("서울 강남구", "아파트")
        assert len(result) > 0

    def test_gangnam_apt_has_multiple_records(self):
        """Rich mock dataset has many records per district — check for a reasonable minimum."""
        result = get_comparables("서울 강남구", "아파트")
        assert len(result) >= 3

    def test_seocho_apt_returns_data(self):
        result = get_comparables("서울 서초구", "아파트")
        assert len(result) > 0

    def test_busan_officetel_returns_data(self):
        result = get_comparables("부산 해운대구", "오피스텔")
        assert len(result) >= 1

    def test_unknown_region_returns_empty(self):
        result = get_comparables("제주", "아파트")
        assert result == []

    def test_unknown_type_returns_empty(self):
        result = get_comparables("서울 강남구", "빌라")
        assert result == []

    def test_unknown_both_returns_empty(self):
        result = get_comparables("제주", "빌라")
        assert result == []

    def test_returns_list_copy(self):
        """Returned list should be a copy, not the original."""
        result1 = get_comparables("서울 강남구", "아파트")
        result2 = get_comparables("서울 강남구", "아파트")
        assert result1 is not result2

    def test_record_has_required_keys(self):
        records = get_comparables("서울 강남구", "아파트")
        required_keys = {"price_krw", "area_sqm", "date", "floor"}
        for record in records:
            assert required_keys.issubset(record.keys())

    def test_prices_are_positive(self):
        for key, records in MOCK_COMPARABLES.items():
            for record in records:
                assert record["price_krw"] > 0, f"Non-positive price in {key}"

    def test_areas_are_positive(self):
        for key, records in MOCK_COMPARABLES.items():
            for record in records:
                assert record["area_sqm"] > 0, f"Non-positive area in {key}"

    def test_area_sqm_param_accepted(self):
        """area_sqm parameter should be accepted (reserved for future API)."""
        result = get_comparables("서울 강남구", "아파트", area_sqm=100.0)
        assert len(result) > 0

    def test_gangnam_house_no_data(self):
        """단독주택 in Gangnam has no mock comparable data."""
        result = get_comparables("서울 강남구", "단독주택")
        assert result == []

    def test_area_sqm_filter_narrows_results(self):
        """area_sqm filter should return only records within ±15 ㎡."""
        all_records = get_comparables("서울 강남구", "아파트")
        filtered = get_comparables("서울 강남구", "아파트", area_sqm=84.0)
        assert len(filtered) < len(all_records)
        for rec in filtered:
            assert abs(rec["area_sqm"] - 84.0) <= 15

    def test_record_has_enriched_keys(self):
        """New mock data includes complex_name, dong, building_age fields."""
        records = get_comparables("서울 강남구", "아파트")
        enriched_keys = {"complex_name", "dong", "building_age", "price_per_sqm_krw"}
        for record in records:
            assert enriched_keys.issubset(record.keys())


class TestGetPriceHistory:
    """Tests for get_price_history()."""

    def test_known_complex_returns_records(self):
        result = get_price_history("반포 자이")
        assert len(result) > 0

    def test_records_sorted_by_date(self):
        result = get_price_history("반포 자이")
        dates = [r["date"] for r in result]
        assert dates == sorted(dates)

    def test_years_filter_respected(self):
        result_5 = get_price_history("반포 자이", years=5)
        result_2 = get_price_history("반포 자이", years=2)
        assert len(result_5) >= len(result_2)

    def test_unknown_complex_returns_empty(self):
        result = get_price_history("존재하지않는아파트단지")
        assert result == []

    def test_record_has_required_keys(self):
        records = get_price_history("잠실 엘스")
        required = {"date", "price_krw", "area_sqm", "price_per_sqm_krw"}
        for rec in records:
            assert required.issubset(rec.keys())
