"""
Tests for app/news_ui.py — Hojae Score computation and sentiment helpers.
"""

from __future__ import annotations

import pytest

from app.news_ui import _compute_hojae_score
from tools.news_tools import NewsAnalysis


class TestComputeHojaeScore:
    def test_neutral_no_extras_returns_four(self):
        analysis = NewsAnalysis(sentiment="neutral", summary="")
        score = _compute_hojae_score(analysis)
        assert score == 4

    def test_bullish_increases_score(self):
        neutral = _compute_hojae_score(NewsAnalysis(sentiment="neutral", summary=""))
        bullish = _compute_hojae_score(NewsAnalysis(sentiment="bullish", summary="호재"))
        assert bullish > neutral

    def test_bearish_increases_score(self):
        neutral = _compute_hojae_score(NewsAnalysis(sentiment="neutral", summary=""))
        bearish = _compute_hojae_score(NewsAnalysis(sentiment="bearish", summary="악재"))
        assert bearish > neutral

    def test_impacted_complexes_increase_score(self):
        base = NewsAnalysis(sentiment="neutral", summary="")
        with_complexes = NewsAnalysis(
            sentiment="neutral",
            summary="",
            impacted_complexes=["반포 자이", "잠실 엘스", "헬리오시티"],
        )
        assert _compute_hojae_score(with_complexes) > _compute_hojae_score(base)

    def test_infrastructure_increases_score(self):
        base = NewsAnalysis(sentiment="neutral", summary="")
        with_infra = NewsAnalysis(sentiment="neutral", summary="", infrastructure="GTX-A")
        assert _compute_hojae_score(with_infra) > _compute_hojae_score(base)

    def test_regions_increase_score(self):
        base = NewsAnalysis(sentiment="neutral", summary="")
        with_regions = NewsAnalysis(
            sentiment="neutral", summary="", regions=["서울 강남구", "경기 성남시"]
        )
        assert _compute_hojae_score(with_regions) > _compute_hojae_score(base)

    def test_score_capped_at_ten(self):
        analysis = NewsAnalysis(
            sentiment="bullish",
            summary="대규모 호재",
            regions=["서울 강남구", "서울 서초구", "서울 용산구"],
            impacted_complexes=["반포 자이", "잠실 엘스", "헬리오시티", "래미안 대치 팰리스"],
            infrastructure="GTX-A",
        )
        assert _compute_hojae_score(analysis) <= 10

    def test_score_is_int(self):
        analysis = NewsAnalysis(sentiment="bullish", summary="호재")
        assert isinstance(_compute_hojae_score(analysis), int)

    def test_score_at_least_four(self):
        analysis = NewsAnalysis(sentiment="neutral", summary="")
        assert _compute_hojae_score(analysis) >= 4


class TestBuildSystemPrompt:
    def test_expert_mode_returns_base_prompt(self):
        from app.realestate_chat_ui import _build_system_prompt
        from chat.prompts import APPRAISER_SYSTEM_PROMPT

        result = _build_system_prompt(expert_mode=True)
        assert result == APPRAISER_SYSTEM_PROMPT

    def test_newbie_mode_appends_suffix(self):
        from app.realestate_chat_ui import _build_system_prompt, _NEWBIE_MODE_SUFFIX

        result = _build_system_prompt(expert_mode=False)
        assert _NEWBIE_MODE_SUFFIX in result

    def test_newbie_mode_still_contains_base_prompt(self):
        from app.realestate_chat_ui import _build_system_prompt
        from chat.prompts import APPRAISER_SYSTEM_PROMPT

        result = _build_system_prompt(expert_mode=False)
        assert APPRAISER_SYSTEM_PROMPT in result

    def test_newbie_mode_longer_than_expert(self):
        from app.realestate_chat_ui import _build_system_prompt

        expert = _build_system_prompt(expert_mode=True)
        newbie = _build_system_prompt(expert_mode=False)
        assert len(newbie) > len(expert)


class TestRenderDictionaryCard:
    """Test the term-detection logic (not the Streamlit rendering)."""

    def test_detects_known_term(self):
        from app.realestate_chat_ui import _TERM_DEFINITIONS

        response = "현재 LTV 제한으로 대출이 어렵습니다."
        detected = {t for t in _TERM_DEFINITIONS if t in response}
        assert "LTV" in detected

    def test_no_terms_in_plain_text(self):
        from app.realestate_chat_ui import _TERM_DEFINITIONS

        response = "안녕하세요. 날씨가 맑습니다."
        detected = {t for t in _TERM_DEFINITIONS if t in response}
        assert len(detected) == 0

    def test_multiple_terms_detected(self):
        from app.realestate_chat_ui import _TERM_DEFINITIONS

        response = "LTV와 DSR 규제로 전세 시장이 위축됩니다."
        detected = {t for t in _TERM_DEFINITIONS if t in response}
        assert len(detected) >= 3
