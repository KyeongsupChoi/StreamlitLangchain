"""
Mock official land price data (공시지가) for Korean real estate valuation.

Project role:
  Returns official land price per square meter by region. Mock data for MVP;
  replace with data.go.kr API client in Phase 2.
"""

from __future__ import annotations

MOCK_OFFICIAL_PRICE_PER_SQM: dict[str, int] = {
    "서울 강남구": 12_500_000,
    "서울 서초구": 10_800_000,
    "서울 송파구": 8_500_000,
    "서울 마포구": 7_200_000,
    "서울": 6_000_000,
    "경기 성남시": 4_500_000,
    "경기 수원시": 3_800_000,
    "경기": 3_000_000,
    "부산 해운대구": 3_500_000,
    "부산": 2_500_000,
}

DEFAULT_OFFICIAL_PRICE_PER_SQM = 2_000_000

_REGION_ORDER = sorted(MOCK_OFFICIAL_PRICE_PER_SQM.keys(), key=len, reverse=True)


def get_official_land_price_per_sqm(region: str) -> int:
    """
    Return official land price per square meter (KRW/㎡) for the given region.

    Region is matched by longest prefix first, falling back to a default.

    Params:
        region: Administrative region (e.g. "서울 강남구", "경기 성남시").

    Returns:
        Official land price in KRW per ㎡.
    """
    region = (region or "").strip()
    for prefix in _REGION_ORDER:
        if region.startswith(prefix):
            return MOCK_OFFICIAL_PRICE_PER_SQM[prefix]
    return DEFAULT_OFFICIAL_PRICE_PER_SQM
