"""
Official land price (공시지가) data for Korean real estate valuation.

Project role:
  Returns official land price per square meter by region and optional year.
  Data is sourced from valuation/data/mock/official_prices.py (Phase 1 mock).
  Phase 6.2 will replace the mock source with a live data.go.kr API client
  while keeping this module's public interface unchanged.
"""

from __future__ import annotations

from valuation.data.mock.official_prices import (
    DEFAULT_BY_YEAR,
    LATEST_YEAR,
    OFFICIAL_PRICE_TABLE,
    _PREFIX_ORDER,
    lookup,
)

# ── Backward-compatible exports ───────────────────────────────────────────────
# These dicts use the same values as before so existing tests pass unchanged.

MOCK_OFFICIAL_PRICE_PER_SQM: dict[str, int] = {
    prefix: year_data[LATEST_YEAR]
    for prefix, year_data in OFFICIAL_PRICE_TABLE.items()
}

DEFAULT_OFFICIAL_PRICE_PER_SQM: int = DEFAULT_BY_YEAR[LATEST_YEAR]

_REGION_ORDER = _PREFIX_ORDER


def get_official_land_price_per_sqm(region: str, year: int | None = None) -> int:
    """
    Return official land price per square meter (KRW/㎡) for the given region.

    Region is matched by longest prefix first (e.g. "서울 강남구" beats "서울"),
    falling back to a default for unrecognised regions.

    Params:
        region: Administrative region (e.g. "서울 강남구", "경기 성남시").
        year: Reference year (2019-2024). Defaults to the latest available year.

    Returns:
        Official land price in KRW per ㎡.
    """
    return lookup(region, year)
