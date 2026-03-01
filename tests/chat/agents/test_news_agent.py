"""
Tests for chat/agents/news_agent.py — structured news analysis agent.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from chat.agents.news_agent import run_news_agent
from tools.news_tools import NewsAnalysis


def _make_model(return_value=None, raises=None):
    """Build a mock model that returns return_value or raises raises."""
    model = MagicMock()
    structured = MagicMock()
    if raises:
        structured.invoke.side_effect = raises
    else:
        structured.invoke.return_value = return_value or NewsAnalysis(
            entities=["GTX"],
            regions=["서울 강남구"],
            infrastructure="GTX-A",
            sentiment="bullish",
            summary="GTX-A 개통 호재",
            impacted_complexes=["래미안 대치 팰리스"],
        )
    model.with_structured_output.return_value = structured
    return model


class TestRunNewsAgent:
    def test_returns_news_analysis(self):
        model = _make_model()
        result = run_news_agent("GTX 강남", model)
        assert isinstance(result, NewsAnalysis)

    def test_calls_with_structured_output(self):
        model = _make_model()
        run_news_agent("GTX 강남", model)
        model.with_structured_output.assert_called_once_with(NewsAnalysis)

    def test_returns_correct_sentiment(self):
        model = _make_model(NewsAnalysis(sentiment="bullish", summary="호재"))
        result = run_news_agent("GTX", model)
        assert result.sentiment == "bullish"

    def test_returns_correct_regions(self):
        model = _make_model(
            NewsAnalysis(regions=["서울 강남구", "경기 성남시"], sentiment="neutral", summary="")
        )
        result = run_news_agent("분당 개발", model)
        assert "서울 강남구" in result.regions

    def test_fallback_on_extraction_failure(self):
        """When structured output raises, agent returns a neutral fallback."""
        model = _make_model(raises=RuntimeError("API error"))
        result = run_news_agent("GTX", model)
        assert isinstance(result, NewsAnalysis)
        assert result.sentiment == "neutral"
        assert "분석 실패" in result.summary

    def test_fallback_has_empty_lists(self):
        model = _make_model(raises=ValueError("bad output"))
        result = run_news_agent("anything", model)
        assert result.entities == []
        assert result.regions == []
        assert result.impacted_complexes == []
