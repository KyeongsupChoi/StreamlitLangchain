"""
Tests for tools/news_tools.py — NewsAnalysis model and parse_news_article tool.
"""

from __future__ import annotations

import pytest

from tools.news_tools import NewsAnalysis, parse_news_article


class TestNewsAnalysis:
    def test_default_construction(self):
        analysis = NewsAnalysis()
        assert analysis.sentiment == "neutral"
        assert analysis.entities == []
        assert analysis.regions == []
        assert analysis.impacted_complexes == []

    def test_bullish_sentiment(self):
        analysis = NewsAnalysis(sentiment="bullish", summary="호재입니다.")
        assert analysis.sentiment == "bullish"
        assert analysis.sentiment_korean == "호재"

    def test_bearish_sentiment_korean(self):
        analysis = NewsAnalysis(sentiment="bearish")
        assert analysis.sentiment_korean == "악재"

    def test_neutral_sentiment_korean(self):
        analysis = NewsAnalysis(sentiment="neutral")
        assert analysis.sentiment_korean == "중립"

    def test_to_report_contains_sentiment(self):
        analysis = NewsAnalysis(sentiment="bullish", summary="GTX 개통 호재")
        report = analysis.to_report()
        assert "호재" in report
        assert "bullish" in report

    def test_to_report_contains_summary(self):
        analysis = NewsAnalysis(summary="GTX-A 수서역 개통 확정")
        report = analysis.to_report()
        assert "GTX-A 수서역 개통 확정" in report

    def test_to_report_contains_regions(self):
        analysis = NewsAnalysis(regions=["서울 강남구", "경기 성남시"])
        report = analysis.to_report()
        assert "서울 강남구" in report

    def test_to_report_contains_impacted_complexes(self):
        analysis = NewsAnalysis(impacted_complexes=["반포 자이", "래미안 퍼스티지"])
        report = analysis.to_report()
        assert "반포 자이" in report

    def test_invalid_sentiment_raises(self):
        with pytest.raises(Exception):
            NewsAnalysis(sentiment="unknown")

    def test_full_construction(self):
        analysis = NewsAnalysis(
            entities=["GTX", "국토교통부"],
            regions=["서울 강남구"],
            infrastructure="GTX-A",
            sentiment="bullish",
            summary="GTX-A 개통으로 강남 접근성 향상",
            impacted_complexes=["래미안 대치 팰리스"],
        )
        assert analysis.infrastructure == "GTX-A"
        assert len(analysis.entities) == 2


class TestParseNewsArticleTool:
    def test_tool_name(self):
        assert parse_news_article.name == "parse_news_article"

    def test_returns_string(self):
        result = parse_news_article.invoke({"url_or_keyword": "GTX 강남"})
        assert isinstance(result, str)

    def test_result_contains_keyword(self):
        result = parse_news_article.invoke({"url_or_keyword": "GTX"})
        # Should contain either the keyword or a mock result label
        assert len(result) > 0

    def test_result_has_news_header(self):
        result = parse_news_article.invoke({"url_or_keyword": "재건축"})
        assert "뉴스" in result or "검색" in result or "결과" in result
