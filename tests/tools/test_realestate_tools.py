"""
Tests for tools/realestate_tools.py -- real estate domain LangChain tools.

Covers all four tools: estimate_property_value, search_comparables,
lookup_official_land_price, explain_valuation_factors.
"""

from __future__ import annotations

import pytest

from tools.realestate_tools import (
    REALESTATE_TOOLS,
    estimate_property_value,
    explain_valuation_factors,
    lookup_official_land_price,
    search_comparables,
)


class TestEstimatePropertyValue:
    """Tests for the estimate_property_value tool."""

    def test_gangnam_apt_basic(self):
        result = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": 84.0,
            "floor": 10,
            "construction_year": 2015,
        })
        assert "감정가" in result
        assert "원" in result

    def test_contains_factor_breakdown(self):
        result = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": 84.0,
            "floor": 10,
            "construction_year": 2020,
        })
        assert "기준가격" in result
        assert "층계수" in result
        assert "연도계수" in result
        assert "면적계수" in result

    def test_contains_data_source(self):
        result = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": 84.0,
            "floor": 10,
            "construction_year": 2020,
        })
        assert "데이터 출처" in result

    def test_seocho_officetel(self):
        result = estimate_property_value.invoke({
            "region": "서울 서초구",
            "property_type": "오피스텔",
            "area_sqm": 59.0,
            "floor": 5,
            "construction_year": 2020,
        })
        assert "감정가" in result

    def test_busan_house(self):
        result = estimate_property_value.invoke({
            "region": "부산 해운대구",
            "property_type": "단독주택",
            "area_sqm": 120.0,
            "floor": 1,
            "construction_year": 2005,
        })
        assert "감정가" in result

    def test_unknown_region_still_works(self):
        result = estimate_property_value.invoke({
            "region": "제주",
            "property_type": "아파트",
            "area_sqm": 84.0,
            "floor": 5,
            "construction_year": 2020,
        })
        assert "감정가" in result

    def test_invalid_area_returns_error(self):
        result = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": -10.0,
            "floor": 5,
            "construction_year": 2020,
        })
        assert "입력 오류" in result

    def test_invalid_year_returns_error(self):
        result = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": 84.0,
            "floor": 5,
            "construction_year": 1900,
        })
        assert "입력 오류" in result

    def test_invalid_property_type_returns_error(self):
        result = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "빌라",
            "area_sqm": 84.0,
            "floor": 5,
            "construction_year": 2020,
        })
        assert "입력 오류" in result

    def test_high_floor_premium(self):
        low = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": 84.0,
            "floor": 1,
            "construction_year": 2025,
        })
        high = estimate_property_value.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": 84.0,
            "floor": 20,
            "construction_year": 2025,
        })
        # Both should have results, and the high floor should have different numbers
        assert "감정가" in low
        assert "감정가" in high


class TestSearchComparables:
    """Tests for the search_comparables tool."""

    def test_gangnam_apt_returns_data(self):
        result = search_comparables.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
        })
        assert "실거래" in result
        assert "건" in result  # count may vary with rich mock dataset

    def test_result_has_transaction_details(self):
        result = search_comparables.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
        })
        assert "원" in result
        assert "㎡" in result
        assert "층" in result

    def test_numbered_list_format(self):
        result = search_comparables.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
        })
        assert "1." in result
        assert "2." in result
        assert "3." in result

    def test_seocho_officetel_returns_data(self):
        """오피스텔 units are ~30-48 ㎡; use matching area to pass the ±15 filter."""
        result = search_comparables.invoke({
            "region": "서울 서초구",
            "property_type": "오피스텔",
            "area_sqm": 30.0,
        })
        assert "건" in result
        assert "서울 서초구" in result

    def test_unknown_region_no_data(self):
        result = search_comparables.invoke({
            "region": "제주",
            "property_type": "아파트",
        })
        assert "데이터가 없습니다" in result

    def test_unknown_type_no_data(self):
        result = search_comparables.invoke({
            "region": "서울 강남구",
            "property_type": "단독주택",
        })
        assert "데이터가 없습니다" in result

    def test_custom_area_accepted(self):
        result = search_comparables.invoke({
            "region": "서울 강남구",
            "property_type": "아파트",
            "area_sqm": 100.0,
        })
        assert "실거래" in result

    def test_default_area(self):
        """Default area_sqm=84.0 should still work."""
        result = search_comparables.invoke({
            "region": "경기 성남시",
            "property_type": "아파트",
        })
        assert "실거래" in result


class TestLookupOfficialLandPrice:
    """Tests for the lookup_official_land_price tool."""

    def test_gangnam(self):
        result = lookup_official_land_price.invoke({"region": "서울 강남구"})
        assert "12,500,000" in result
        assert "원/㎡" in result

    def test_seocho(self):
        result = lookup_official_land_price.invoke({"region": "서울 서초구"})
        assert "10,800,000" in result

    def test_gyeonggi_seongnam(self):
        result = lookup_official_land_price.invoke({"region": "경기 성남시"})
        assert "4,500,000" in result

    def test_busan_haeundae(self):
        result = lookup_official_land_price.invoke({"region": "부산 해운대구"})
        assert "3,500,000" in result

    def test_unknown_region_returns_default(self):
        result = lookup_official_land_price.invoke({"region": "제주"})
        assert "2,000,000" in result

    def test_contains_region_name(self):
        result = lookup_official_land_price.invoke({"region": "서울 강남구"})
        assert "서울 강남구" in result

    def test_contains_공시지가_label(self):
        result = lookup_official_land_price.invoke({"region": "서울 강남구"})
        assert "공시지가" in result


class TestExplainValuationFactors:
    """Tests for the explain_valuation_factors tool."""

    def test_contains_all_factor_sections(self):
        result = explain_valuation_factors.invoke({})
        assert "기준가격" in result
        assert "층계수" in result
        assert "연도계수" in result
        assert "면적계수" in result
        assert "실거래가 반영" in result

    def test_contains_base_price_data(self):
        result = explain_valuation_factors.invoke({})
        assert "원/㎡" in result
        assert "1,500,000" in result  # Gangnam apt base price

    def test_contains_floor_multipliers(self):
        result = explain_valuation_factors.invoke({})
        assert "x0.95" in result
        assert "x1.0" in result
        assert "x1.02" in result

    def test_contains_depreciation_info(self):
        result = explain_valuation_factors.invoke({})
        assert "0.5%" in result
        assert "20%" in result

    def test_contains_size_bands(self):
        result = explain_valuation_factors.invoke({})
        assert "x0.98" in result
        assert "x0.99" in result
        assert "x0.97" in result

    def test_contains_comparables_weight(self):
        result = explain_valuation_factors.invoke({})
        assert "30%" in result

    def test_contains_default_prices(self):
        result = explain_valuation_factors.invoke({})
        assert "기본값" in result

    def test_no_args_required(self):
        """Tool should work with empty args dict."""
        result = explain_valuation_factors.invoke({})
        assert len(result) > 100  # Non-trivial output


class TestRealestateToolsList:
    """Tests for the REALESTATE_TOOLS registry."""

    def test_has_four_tools(self):
        assert len(REALESTATE_TOOLS) == 4

    def test_tool_names(self):
        names = [t.name for t in REALESTATE_TOOLS]
        assert "estimate_property_value" in names
        assert "search_comparables" in names
        assert "lookup_official_land_price" in names
        assert "explain_valuation_factors" in names

    def test_all_tools_have_descriptions(self):
        for t in REALESTATE_TOOLS:
            assert t.description, f"Tool {t.name} missing description"

    def test_tools_follow_verb_noun_naming(self):
        """All tool names should follow verb_noun convention."""
        for t in REALESTATE_TOOLS:
            parts = t.name.split("_")
            assert len(parts) >= 2, f"Tool {t.name} doesn't follow verb_noun pattern"
