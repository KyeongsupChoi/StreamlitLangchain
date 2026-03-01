"""
Tests for app/context.py — shared application context helpers.
"""

from __future__ import annotations

import pytest

from app.context import (
    AppContext,
    add_to_watchlist,
    get_app_context,
    remove_from_watchlist,
    set_news_analysis,
    set_selected_property,
)


class TestGetAppContext:
    def test_creates_context_when_absent(self):
        state: dict = {}
        ctx = get_app_context(state)
        assert isinstance(ctx, AppContext)

    def test_stores_in_session_state(self):
        state: dict = {}
        get_app_context(state)
        assert "app_context" in state

    def test_returns_same_instance_on_repeated_calls(self):
        state: dict = {}
        ctx1 = get_app_context(state)
        ctx2 = get_app_context(state)
        assert ctx1 is ctx2

    def test_default_fields_are_none(self):
        ctx = get_app_context({})
        assert ctx.selected_complex_name is None
        assert ctx.selected_property is None
        assert ctx.news_analysis is None
        assert ctx.news_query is None

    def test_default_watchlist_is_empty(self):
        ctx = get_app_context({})
        assert ctx.watchlist == []


class TestSetSelectedProperty:
    def test_stores_property(self):
        state: dict = {}
        fake_prop = object()
        set_selected_property(state, fake_prop, complex_name="반포 자이")
        ctx = get_app_context(state)
        assert ctx.selected_property is fake_prop

    def test_stores_complex_name(self):
        state: dict = {}
        set_selected_property(state, object(), complex_name="잠실 엘스")
        assert get_app_context(state).selected_complex_name == "잠실 엘스"

    def test_empty_complex_name_stored_as_empty_string(self):
        state: dict = {}
        set_selected_property(state, object())
        assert get_app_context(state).selected_complex_name == ""

    def test_overwrites_previous_property(self):
        state: dict = {}
        prop1 = object()
        prop2 = object()
        set_selected_property(state, prop1, "단지 A")
        set_selected_property(state, prop2, "단지 B")
        ctx = get_app_context(state)
        assert ctx.selected_property is prop2
        assert ctx.selected_complex_name == "단지 B"


class TestSetNewsAnalysis:
    def test_stores_analysis(self):
        state: dict = {}
        fake_analysis = object()
        set_news_analysis(state, fake_analysis, query="GTX 강남")
        ctx = get_app_context(state)
        assert ctx.news_analysis is fake_analysis

    def test_stores_query(self):
        state: dict = {}
        set_news_analysis(state, object(), query="재건축 뉴스")
        assert get_app_context(state).news_query == "재건축 뉴스"

    def test_empty_query_defaults_to_empty_string(self):
        state: dict = {}
        set_news_analysis(state, object())
        assert get_app_context(state).news_query == ""

    def test_overwrites_previous_analysis(self):
        state: dict = {}
        a1 = object()
        a2 = object()
        set_news_analysis(state, a1, "first")
        set_news_analysis(state, a2, "second")
        ctx = get_app_context(state)
        assert ctx.news_analysis is a2
        assert ctx.news_query == "second"


class TestWatchlist:
    def test_add_to_empty_watchlist(self):
        state: dict = {}
        add_to_watchlist(state, "반포 자이")
        assert "반포 자이" in get_app_context(state).watchlist

    def test_add_multiple(self):
        state: dict = {}
        add_to_watchlist(state, "반포 자이")
        add_to_watchlist(state, "잠실 엘스")
        assert len(get_app_context(state).watchlist) == 2

    def test_no_duplicate_entries(self):
        state: dict = {}
        add_to_watchlist(state, "반포 자이")
        add_to_watchlist(state, "반포 자이")
        assert get_app_context(state).watchlist.count("반포 자이") == 1

    def test_empty_string_not_added(self):
        state: dict = {}
        add_to_watchlist(state, "")
        assert get_app_context(state).watchlist == []

    def test_remove_existing_entry(self):
        state: dict = {}
        add_to_watchlist(state, "반포 자이")
        add_to_watchlist(state, "잠실 엘스")
        remove_from_watchlist(state, "반포 자이")
        ctx = get_app_context(state)
        assert "반포 자이" not in ctx.watchlist
        assert "잠실 엘스" in ctx.watchlist

    def test_remove_nonexistent_is_safe(self):
        state: dict = {}
        add_to_watchlist(state, "반포 자이")
        remove_from_watchlist(state, "없는 단지")
        assert len(get_app_context(state).watchlist) == 1

    def test_remove_all_entries(self):
        state: dict = {}
        add_to_watchlist(state, "반포 자이")
        remove_from_watchlist(state, "반포 자이")
        assert get_app_context(state).watchlist == []

    def test_watchlist_preserved_across_get_app_context_calls(self):
        state: dict = {}
        add_to_watchlist(state, "래미안 대치 팰리스")
        ctx = get_app_context(state)
        assert "래미안 대치 팰리스" in ctx.watchlist
