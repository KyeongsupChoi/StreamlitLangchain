"""
Shared application context for cross-page state management.

Stores selected property, news analysis result, and user watchlist in
st.session_state["app_context"] for seamless handoff between the
Property-First (Evaluator) and News-First (Trend Hunter) entry points.
"""

from __future__ import annotations

from dataclasses import dataclass, field

_CONTEXT_KEY = "app_context"


@dataclass
class AppContext:
    """
    Shared context object persisted in st.session_state across all pages.

    Attributes:
        selected_complex_name: Name of the apartment complex chosen in the Evaluator.
        selected_property: Property dataclass instance built from the chosen complex.
        news_analysis: NewsAnalysis result from the most recent news agent run.
        news_query: The keyword / URL that produced news_analysis.
        watchlist: List of complex names the user has bookmarked.
    """

    selected_complex_name: str | None = None
    selected_property: object | None = None   # valuation.models.Property
    news_analysis: object | None = None        # tools.news_tools.NewsAnalysis
    news_query: str | None = None
    watchlist: list[str] = field(default_factory=list)


def get_app_context(session_state: dict) -> AppContext:
    """
    Return the AppContext from session_state, creating it if absent.

    Params:
        session_state: Streamlit st.session_state dict.

    Returns:
        The AppContext instance stored in session_state.
    """
    if _CONTEXT_KEY not in session_state:
        session_state[_CONTEXT_KEY] = AppContext()
    return session_state[_CONTEXT_KEY]


def set_selected_property(
    session_state: dict,
    prop: object,
    complex_name: str = "",
) -> None:
    """
    Store a selected property in the shared context.

    Params:
        session_state: Streamlit st.session_state dict.
        prop: The Property dataclass instance.
        complex_name: Optional apartment complex name.
    """
    ctx = get_app_context(session_state)
    ctx.selected_property = prop
    ctx.selected_complex_name = complex_name or ""


def set_news_analysis(
    session_state: dict,
    analysis: object,
    query: str = "",
) -> None:
    """
    Store a news analysis result in the shared context.

    Params:
        session_state: Streamlit st.session_state dict.
        analysis: The NewsAnalysis dataclass instance.
        query: The keyword or URL used to generate the analysis.
    """
    ctx = get_app_context(session_state)
    ctx.news_analysis = analysis
    ctx.news_query = query


def add_to_watchlist(session_state: dict, complex_name: str) -> None:
    """
    Add a complex name to the watchlist if not already present.

    Params:
        session_state: Streamlit st.session_state dict.
        complex_name: Name of the apartment complex to bookmark.
    """
    ctx = get_app_context(session_state)
    if complex_name and complex_name not in ctx.watchlist:
        ctx.watchlist.append(complex_name)


def remove_from_watchlist(session_state: dict, complex_name: str) -> None:
    """
    Remove a complex name from the watchlist.

    Params:
        session_state: Streamlit st.session_state dict.
        complex_name: Name of the complex to remove.
    """
    ctx = get_app_context(session_state)
    ctx.watchlist = [n for n in ctx.watchlist if n != complex_name]
