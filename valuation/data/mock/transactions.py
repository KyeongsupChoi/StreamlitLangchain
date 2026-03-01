"""
Rich mock comparable transaction dataset for Korean real estate.

Contains 500+ synthetic transactions across 13 districts and 6 years (2019-2024).
Prices reflect realistic Seoul/Gyeonggi/Busan market tiers with year-over-year
growth and the 2022 correction pattern.

Used by valuation/data/comparables.py as the default data source.
Phase 6.1 will replace this with live MOLIT API data.
"""

from __future__ import annotations

import random

_rng = random.Random(42)  # fixed seed — output is always identical

# Market index relative to 2024 prices.
# Captures the 2019-2021 boom, 2022 correction, and 2023-2024 recovery.
_YEAR_FACTOR: dict[int, float] = {
    2019: 0.58,
    2020: 0.68,
    2021: 0.88,
    2022: 0.80,
    2023: 0.90,
    2024: 1.00,
}

_MONTHS = [f"{m:02d}" for m in range(1, 13)]

# Each entry: (region, property_type, complex_name, dong, building_year, base_price_per_sqm, [area_sqm, ...])
# base_price_per_sqm is the 2024 market price per ㎡ in KRW.
_COMPLEX_SPECS: list[tuple] = [
    # ── 서울 강남구 (premium tier) ──────────────────────────────────────────
    ("서울 강남구", "아파트", "래미안 대치 팰리스", "대치동", 2015, 21_000_000, [84, 114]),
    ("서울 강남구", "아파트", "타워팰리스 3차", "도곡동", 2004, 19_500_000, [84, 165]),
    ("서울 강남구", "아파트", "아크로 리버 파크", "개포동", 2016, 22_000_000, [59, 84]),
    ("서울 강남구", "오피스텔", "강남 센트럴 아이파크", "역삼동", 2018, 13_000_000, [30, 45]),
    ("서울 강남구", "오피스텔", "강남 파크자이", "삼성동", 2012, 12_000_000, [28, 42]),
    # ── 서울 서초구 ─────────────────────────────────────────────────────────
    ("서울 서초구", "아파트", "반포 자이", "반포동", 2009, 20_000_000, [84, 132]),
    ("서울 서초구", "아파트", "래미안 퍼스티지", "반포동", 2009, 21_000_000, [84, 115]),
    ("서울 서초구", "아파트", "아크로 반포", "반포동", 2020, 22_500_000, [84, 115]),
    ("서울 서초구", "오피스텔", "서초 SK HUB", "서초동", 2015, 11_000_000, [30, 48]),
    # ── 서울 용산구 ─────────────────────────────────────────────────────────
    ("서울 용산구", "아파트", "한남 더 힐", "한남동", 2011, 19_000_000, [84, 200]),
    ("서울 용산구", "아파트", "파크 한남", "한남동", 2021, 21_000_000, [84, 145]),
    ("서울 용산구", "아파트", "이촌 현대아파트", "이촌동", 1994, 14_000_000, [76, 95]),
    # ── 서울 송파구 ─────────────────────────────────────────────────────────
    ("서울 송파구", "아파트", "잠실 엘스", "잠실동", 2008, 14_500_000, [84, 120]),
    ("서울 송파구", "아파트", "리센츠", "잠실동", 2008, 13_500_000, [84, 102]),
    ("서울 송파구", "아파트", "헬리오시티", "가락동", 2018, 12_000_000, [59, 84]),
    ("서울 송파구", "오피스텔", "잠실 트리지움", "잠실동", 2007, 9_000_000, [30, 55]),
    # ── 서울 성동구 ─────────────────────────────────────────────────────────
    ("서울 성동구", "아파트", "아크로 서울 포레스트", "성수동", 2020, 13_000_000, [84, 150]),
    ("서울 성동구", "아파트", "왕십리 텐즈힐", "하왕십리동", 2013, 9_000_000, [59, 84]),
    ("서울 성동구", "아파트", "서울숲 리버뷰 자이", "성수동", 2023, 14_000_000, [84, 114]),
    # ── 서울 마포구 ─────────────────────────────────────────────────────────
    ("서울 마포구", "아파트", "마포 래미안 푸르지오", "공덕동", 2014, 9_500_000, [59, 84]),
    ("서울 마포구", "아파트", "e편한세상 공덕", "공덕동", 2019, 10_000_000, [84, 102]),
    ("서울 마포구", "아파트", "공덕 자이", "공덕동", 2016, 9_200_000, [59, 84]),
    ("서울 마포구", "오피스텔", "공덕 SK 리더스 뷰", "공덕동", 2010, 7_000_000, [28, 40]),
    # ── 서울 광진구 ─────────────────────────────────────────────────────────
    ("서울 광진구", "아파트", "광장 현대아파트", "광장동", 1999, 7_000_000, [76, 115]),
    ("서울 광진구", "아파트", "더샵 스타리버", "광장동", 2021, 9_500_000, [84, 114]),
    # ── 서울 영등포구 ────────────────────────────────────────────────────────
    ("서울 영등포구", "아파트", "여의도 삼부아파트", "여의도동", 1982, 11_000_000, [76, 115]),
    ("서울 영등포구", "아파트", "여의도 파크원 자이", "여의도동", 2021, 15_000_000, [84, 150]),
    ("서울 영등포구", "오피스텔", "영등포 센트럴 자이", "영등포동", 2018, 7_500_000, [30, 48]),
    # ── 서울 노원구 ─────────────────────────────────────────────────────────
    ("서울 노원구", "아파트", "상계 주공아파트 5단지", "상계동", 1988, 4_000_000, [49, 59]),
    ("서울 노원구", "아파트", "중계 그린아파트", "중계동", 1992, 4_500_000, [59, 76]),
    ("서울 노원구", "아파트", "노원 꿈에그린", "월계동", 2007, 5_000_000, [59, 84]),
    # ── 서울 은평구 ─────────────────────────────────────────────────────────
    ("서울 은평구", "아파트", "불광 미성아파트", "불광동", 1985, 4_200_000, [54, 76]),
    ("서울 은평구", "아파트", "은평 래미안", "응암동", 2018, 5_500_000, [59, 84]),
    # ── 서울 강동구 ─────────────────────────────────────────────────────────
    ("서울 강동구", "아파트", "고덕 래미안 힐스테이트", "고덕동", 2019, 8_000_000, [59, 84]),
    ("서울 강동구", "아파트", "올림픽파크 포레온", "둔촌동", 2023, 10_000_000, [59, 84]),
    # ── 서울 동작구 ─────────────────────────────────────────────────────────
    ("서울 동작구", "아파트", "흑석 아크로 리버하임", "흑석동", 2019, 10_500_000, [59, 84]),
    ("서울 동작구", "아파트", "사당 래미안 이수", "사당동", 2009, 8_000_000, [59, 84]),
    # ── 경기 성남시 ─────────────────────────────────────────────────────────
    ("경기 성남시", "아파트", "파크뷰 자이", "분당구 정자동", 2006, 8_000_000, [84, 114]),
    ("경기 성남시", "아파트", "서판교 산운마을", "수정구 고등동", 2010, 7_500_000, [84, 114]),
    ("경기 성남시", "아파트", "분당 파크뷰 삼성", "분당구 야탑동", 2000, 6_500_000, [76, 101]),
    ("경기 성남시", "오피스텔", "판교 더샵 퍼스트파크", "분당구 판교동", 2014, 6_000_000, [32, 48]),
    # ── 경기 수원시 ─────────────────────────────────────────────────────────
    ("경기 수원시", "아파트", "광교 자이 더 명작", "영통구 이의동", 2019, 6_000_000, [84, 115]),
    ("경기 수원시", "아파트", "영통 롯데캐슬", "영통구 영통동", 2015, 4_500_000, [59, 84]),
    ("경기 수원시", "오피스텔", "수원 SK VIEW", "팔달구 인계동", 2016, 3_500_000, [30, 45]),
    # ── 부산 해운대구 ────────────────────────────────────────────────────────
    ("부산 해운대구", "아파트", "해운대 엘시티", "우동", 2019, 8_500_000, [84, 200]),
    ("부산 해운대구", "아파트", "센텀 리버사이드 자이", "재송동", 2018, 6_500_000, [84, 114]),
    ("부산 해운대구", "아파트", "해운대 아이파크", "우동", 2011, 7_000_000, [84, 138]),
    ("부산 해운대구", "오피스텔", "해운대 마린시티 자이", "중동", 2016, 5_500_000, [30, 50]),
]


def _floor_adj(floor: int) -> float:
    """Return price multiplier based on floor number."""
    if floor <= 1:
        return 0.95
    if floor <= 4:
        return 0.98
    if floor <= 15:
        return 1.00
    return 1.02


def _build_transactions() -> list[dict]:
    records: list[dict] = []
    for region, ptype, complex_name, dong, building_year, base_price_m2, areas in _COMPLEX_SPECS:
        for year, year_factor in _YEAR_FACTOR.items():
            for area_sqm in areas:
                # 2 transactions per (complex, year, size) for density
                for _ in range(2):
                    month = _rng.choice(_MONTHS)
                    floor = _rng.randint(3, 25)
                    noise = _rng.uniform(0.97, 1.03)
                    price_m2 = int(base_price_m2 * year_factor * _floor_adj(floor) * noise)
                    records.append({
                        "region": region,
                        "property_type": ptype,
                        "complex_name": complex_name,
                        "dong": dong,
                        "area_sqm": float(area_sqm),
                        "floor": floor,
                        "price_krw": int(price_m2 * area_sqm),
                        "price_per_sqm_krw": price_m2,
                        "date": f"{year}-{month}",
                        "building_age": year - building_year,
                    })
    return records


# Generated once at import time. ~1,100 records total.
TRANSACTIONS: list[dict] = _build_transactions()


def get_transactions_by_region(region: str, property_type: str) -> list[dict]:
    """
    Return all transactions for the given region and property type.

    Params:
        region: Administrative region (e.g. "서울 강남구").
        property_type: One of 아파트, 오피스텔, 단독주택.

    Returns:
        List of transaction dicts. Empty list if no data found.
    """
    return [
        r for r in TRANSACTIONS
        if r["region"] == region and r["property_type"] == property_type
    ]


def get_price_history(complex_name: str, years: int = 5) -> list[dict]:
    """
    Return price history records for a named apartment complex.

    Params:
        complex_name: Exact complex name (e.g. "반포 자이").
        years: Number of years of history to return (counting back from 2024).

    Returns:
        List of dicts sorted by date with keys:
        date, price_per_sqm_krw, price_krw, area_sqm, floor, dong.
        Empty list if complex not found.
    """
    cutoff_year = 2024 - years + 1
    records = [
        r for r in TRANSACTIONS
        if r["complex_name"] == complex_name and int(r["date"][:4]) >= cutoff_year
    ]
    return sorted(records, key=lambda r: r["date"])
