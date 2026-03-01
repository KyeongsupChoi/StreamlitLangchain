"""
Tests for chat/prompts.py — appraiser prompt templates.
"""

from __future__ import annotations

import pytest

from chat.prompts import (
    APPRAISER_SYSTEM_PROMPT,
    NEWS_EXTRACTION_PROMPT,
    SUMMARY_SYSTEM_PROMPT,
    SUMMARY_USER_TEMPLATE,
    format_appraiser_prompt,
)
from valuation.models import FactorContribution, Property, ValuationResult


@pytest.fixture()
def sample_property() -> Property:
    return Property(
        region="서울 강남구",
        property_type="아파트",
        area_sqm=84.0,
        floor=10,
        construction_year=2015,
    )


@pytest.fixture()
def sample_result() -> ValuationResult:
    return ValuationResult(
        estimated_value_krw=1_500_000_000,
        currency="KRW",
        factor_breakdown=(
            FactorContribution(
                name="기준가격",
                multiplier_or_value=1_200_000,
                contribution_krw=100_800_000,
                description="서울 강남구 아파트 기준",
            ),
        ),
        data_sources_used="목데이터",
    )


class TestAppraiserSystemPrompt:
    def test_is_non_empty_string(self):
        assert isinstance(APPRAISER_SYSTEM_PROMPT, str)
        assert len(APPRAISER_SYSTEM_PROMPT) > 100

    def test_contains_role_section(self):
        assert "역할" in APPRAISER_SYSTEM_PROMPT

    def test_contains_tool_references(self):
        assert "estimate_property_value" in APPRAISER_SYSTEM_PROMPT
        assert "search_comparables" in APPRAISER_SYSTEM_PROMPT
        assert "parse_news_article" in APPRAISER_SYSTEM_PROMPT

    def test_contains_response_format(self):
        assert "응답 형식" in APPRAISER_SYSTEM_PROMPT


class TestFormatAppraiserPrompt:
    def test_returns_string(self, sample_property, sample_result):
        result = format_appraiser_prompt(sample_property, sample_result)
        assert isinstance(result, str)

    def test_contains_region(self, sample_property, sample_result):
        result = format_appraiser_prompt(sample_property, sample_result)
        assert "서울 강남구" in result

    def test_contains_property_type(self, sample_property, sample_result):
        result = format_appraiser_prompt(sample_property, sample_result)
        assert "아파트" in result

    def test_contains_area_sqm(self, sample_property, sample_result):
        result = format_appraiser_prompt(sample_property, sample_result)
        assert "84.0" in result

    def test_contains_pyeong(self, sample_property, sample_result):
        """Should convert ㎡ to 평 (1 pyeong ≈ 3.3058 ㎡)."""
        result = format_appraiser_prompt(sample_property, sample_result)
        assert "평" in result

    def test_contains_estimated_value(self, sample_property, sample_result):
        result = format_appraiser_prompt(sample_property, sample_result)
        assert "1,500,000,000" in result

    def test_contains_factor_name(self, sample_property, sample_result):
        result = format_appraiser_prompt(sample_property, sample_result)
        assert "기준가격" in result

    def test_eok_value_approximate(self, sample_property, sample_result):
        """1,500,000,000 원 = 15억 = 15.00억."""
        result = format_appraiser_prompt(sample_property, sample_result)
        assert "15.00" in result


class TestNewsExtractionPrompt:
    def test_is_non_empty_string(self):
        assert isinstance(NEWS_EXTRACTION_PROMPT, str)

    def test_has_format_placeholder(self):
        assert "{news_content}" in NEWS_EXTRACTION_PROMPT

    def test_can_be_formatted(self):
        formatted = NEWS_EXTRACTION_PROMPT.format(news_content="테스트 뉴스 내용")
        assert "테스트 뉴스 내용" in formatted


class TestSummaryPrompts:
    def test_summary_system_prompt_non_empty(self):
        assert len(SUMMARY_SYSTEM_PROMPT) > 20

    def test_summary_user_template_has_placeholder(self):
        assert "{conversation}" in SUMMARY_USER_TEMPLATE

    def test_summary_user_template_can_be_formatted(self):
        result = SUMMARY_USER_TEMPLATE.format(conversation="USER: 안녕\nASSISTANT: 안녕하세요")
        assert "USER" in result
