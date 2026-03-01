"""
Apartment complex directory for Korean real estate.

Provides name-based search and lookup over the mock complex dataset.
Phase 6.3 will replace address resolution with live Kakao/Naver Geocoding API,
but search_complexes and get_complex interfaces remain the same.
"""

from __future__ import annotations

from valuation.data.mock.complexes import COMPLEXES, Complex


def search_complexes(query: str, limit: int = 10) -> list[Complex]:
    """
    Search for apartment complexes by name or dong.

    Matches any complex whose name or dong contains any whitespace-separated
    token from the query (case-insensitive).

    Params:
        query: Free-text search string (e.g. "반포", "잠실 아파트", "강남").
        limit: Maximum number of results to return.

    Returns:
        List of matching Complex objects, ordered by name.
    """
    tokens = [t.strip() for t in query.split() if t.strip()]
    if not tokens:
        return list(COMPLEXES[:limit])

    results = [
        c for c in COMPLEXES
        if any(tok in c.name or tok in c.dong or tok in c.district for tok in tokens)
    ]
    return sorted(results, key=lambda c: c.name)[:limit]


def get_complex(name: str) -> Complex | None:
    """
    Return a Complex by exact or partial name match.

    Tries exact match first, then returns the first complex whose name
    contains the query string.

    Params:
        name: Complex name or partial name (e.g. "반포 자이").

    Returns:
        Matching Complex, or None if not found.
    """
    name = (name or "").strip()
    if not name:
        return None
    # Exact match first
    for c in COMPLEXES:
        if c.name == name:
            return c
    # Partial match fallback
    for c in COMPLEXES:
        if name in c.name:
            return c
    return None
