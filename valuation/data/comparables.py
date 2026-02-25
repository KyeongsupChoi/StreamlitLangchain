"""
Mock comparable transaction data for Korean real estate valuation.

Project role:
  Returns recent transaction records by region and property type. Mock data
  for MVP; replace with data.go.kr API client in Phase 2.
"""

from __future__ import annotations

MOCK_COMPARABLES: dict[tuple[str, str], list[dict]] = {
    ("서울 강남구", "아파트"): [
        {"price_krw": 1_680_000_000, "area_sqm": 84.0, "date": "2025-09", "floor": 12},
        {"price_krw": 1_520_000_000, "area_sqm": 84.0, "date": "2025-07", "floor": 8},
        {"price_krw": 1_750_000_000, "area_sqm": 84.0, "date": "2025-11", "floor": 18},
    ],
    ("서울 강남구", "오피스텔"): [
        {"price_krw": 680_000_000, "area_sqm": 59.0, "date": "2025-10", "floor": 5},
        {"price_krw": 720_000_000, "area_sqm": 62.0, "date": "2025-08", "floor": 10},
    ],
    ("서울 서초구", "아파트"): [
        {"price_krw": 1_450_000_000, "area_sqm": 84.0, "date": "2025-10", "floor": 15},
        {"price_krw": 1_380_000_000, "area_sqm": 76.0, "date": "2025-08", "floor": 7},
        {"price_krw": 1_500_000_000, "area_sqm": 84.0, "date": "2025-12", "floor": 22},
    ],
    ("서울 서초구", "오피스텔"): [
        {"price_krw": 620_000_000, "area_sqm": 55.0, "date": "2025-09", "floor": 3},
    ],
    ("경기 성남시", "아파트"): [
        {"price_krw": 780_000_000, "area_sqm": 84.0, "date": "2025-10", "floor": 10},
        {"price_krw": 720_000_000, "area_sqm": 76.0, "date": "2025-07", "floor": 5},
    ],
    ("경기 성남시", "오피스텔"): [
        {"price_krw": 380_000_000, "area_sqm": 59.0, "date": "2025-11", "floor": 8},
    ],
    ("부산 해운대구", "아파트"): [
        {"price_krw": 650_000_000, "area_sqm": 84.0, "date": "2025-09", "floor": 14},
        {"price_krw": 580_000_000, "area_sqm": 76.0, "date": "2025-06", "floor": 6},
    ],
    ("부산 해운대구", "오피스텔"): [
        {"price_krw": 320_000_000, "area_sqm": 55.0, "date": "2025-10", "floor": 4},
    ],
}


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
        area_sqm: Optional area filter (unused in mock; reserved for API).

    Returns:
        List of dicts with keys: price_krw, area_sqm, date, floor.
        Empty list if no data for the region/type combination.
    """
    return list(MOCK_COMPARABLES.get((region, property_type), []))
