"""
Comparable transaction data for Korean real estate valuation.

Project role:
  Returns recent transaction records by region and property type.
  Data is sourced from valuation/data/mock/transactions.py (Phase 1 mock).
  Phase 6.1 will replace the mock source with a live MOLIT API client while
  keeping this module's public interface unchanged.
"""

from __future__ import annotations

from valuation.data.mock.transactions import (
    TRANSACTIONS,
    get_price_history,
    get_transactions_by_region,
)

# Re-export get_price_history so callers can import from this module.
__all__ = ["MOCK_COMPARABLES", "get_comparables", "get_price_history"]

# Build MOCK_COMPARABLES in the legacy (region, property_type) -> list[dict] format
# so existing code and tests that import it directly continue to work.
# Records include the new fields (complex_name, dong, building_age) in addition
# to the original keys (price_krw, area_sqm, date, floor).
MOCK_COMPARABLES: dict[tuple[str, str], list[dict]] = {}
for _rec in TRANSACTIONS:
    _key = (_rec["region"], _rec["property_type"])
    MOCK_COMPARABLES.setdefault(_key, []).append({
        "price_krw": _rec["price_krw"],
        "area_sqm": _rec["area_sqm"],
        "date": _rec["date"],
        "floor": _rec["floor"],
        "complex_name": _rec["complex_name"],
        "dong": _rec["dong"],
        "building_age": _rec["building_age"],
        "price_per_sqm_krw": _rec["price_per_sqm_krw"],
    })


def get_comparables(
    region: str,
    property_type: str,
    area_sqm: float | None = None,
) -> list[dict]:
    """
    Return recent comparable transactions for the given region and property type.

    Params:
        region: Administrative region (e.g. "서울 강남구").
        property_type: One of 아파트, 오피스텔, 단독주택.
        area_sqm: Optional area filter. When provided, returns only records
                  within ±15 ㎡ of the specified area.

    Returns:
        List of dicts with keys: price_krw, area_sqm, date, floor,
        complex_name, dong, building_age, price_per_sqm_krw.
        Empty list if no data for the region/type combination.
    """
    records = list(MOCK_COMPARABLES.get((region, property_type), []))
    if area_sqm is not None:
        records = [r for r in records if abs(r["area_sqm"] - area_sqm) <= 15]
    return records
