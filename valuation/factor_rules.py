"""
Factor rules and constants for Korean real estate valuation.

Project role:
  Central place for base prices, floor/age/size multipliers used by the
  valuation engine. All values are mock rules for MVP; replace with
  real data or config in later phases.
"""

from __future__ import annotations

from datetime import date

# ---------------------------------------------------------------------------
# Base price per ㎡ (원/㎡) by region and property type. Mock data for MVP.
# Key: (region_prefix, property_type). Region matched by startswith.
# Fallback: default base when no region match.
# ---------------------------------------------------------------------------

BASE_PRICE_PER_SQM: dict[tuple[str, str], int] = {
    ("서울 강남구", "아파트"): 1_500_000,
    ("서울 강남구", "오피스텔"): 1_350_000,
    ("서울 강남구", "단독주택"): 1_800_000,
    ("서울 서초구", "아파트"): 1_450_000,
    ("서울 서초구", "오피스텔"): 1_300_000,
    ("서울 서초구", "단독주택"): 1_700_000,
    ("서울", "아파트"): 1_200_000,
    ("서울", "오피스텔"): 1_050_000,
    ("서울", "단독주택"): 1_400_000,
    ("경기", "아파트"): 800_000,
    ("경기", "오피스텔"): 720_000,
    ("경기", "단독주택"): 950_000,
    ("부산", "아파트"): 750_000,
    ("부산", "오피스텔"): 680_000,
    ("부산", "단독주택"): 900_000,
}

DEFAULT_BASE_PRICE_PER_SQM: dict[str, int] = {
    "아파트": 800_000,
    "오피스텔": 720_000,
    "단독주택": 950_000,
}

# Region match order: longest prefix first (강남구 before 서울).
_REGION_ORDER = sorted(
    (r for r, _ in BASE_PRICE_PER_SQM.keys() if r != "서울"),
    key=len,
    reverse=True,
)


def get_base_price_per_sqm(region: str, property_type: str) -> int:
    """
    Return base price per ㎡ (KRW) for the given region and property type.

    Region is matched by prefix (longest match first). Unmatched regions
    use DEFAULT_BASE_PRICE_PER_SQM by property type.

    Params:
        region: Administrative region (e.g. "서울 강남구", "경기 성남시").
        property_type: One of 아파트, 오피스텔, 단독주택.

    Returns:
        Base price in KRW per ㎡.
    """
    region = (region or "").strip()
    for prefix in _REGION_ORDER:
        if region.startswith(prefix):
            key = (prefix, property_type)
            if key in BASE_PRICE_PER_SQM:
                return BASE_PRICE_PER_SQM[key]
    if region.startswith("서울"):
        return BASE_PRICE_PER_SQM.get(
            ("서울", property_type),
            DEFAULT_BASE_PRICE_PER_SQM[property_type],
        )
    return DEFAULT_BASE_PRICE_PER_SQM.get(
        property_type,
        DEFAULT_BASE_PRICE_PER_SQM["아파트"],
    )


# ---------------------------------------------------------------------------
# Floor factor: multiplier applied to base. 1F discount, mid floors neutral,
# high floors slight premium. Mock rules for MVP.
# ---------------------------------------------------------------------------

FLOOR_FACTOR_MAP: list[tuple[int, int, float]] = [
    (1, 1, 0.95),
    (2, 4, 0.98),
    (5, 15, 1.0),
    (16, 999, 1.02),
]


def get_floor_factor(floor: int) -> float:
    """
    Return the floor adjustment multiplier for the given floor number.

    Params:
        floor: Floor number (1-based).

    Returns:
        Multiplier (e.g. 0.95 for 1F, 1.0 for 5-15F, 1.02 for 16F+).
    """
    if floor < 1:
        return FLOOR_FACTOR_MAP[0][2]
    for low, high, factor in FLOOR_FACTOR_MAP:
        if low <= floor <= high:
            return factor
    return FLOOR_FACTOR_MAP[-1][2]


# ---------------------------------------------------------------------------
# Age depreciation: 0.5% per year after construction, cap at 20%.
# ---------------------------------------------------------------------------

AGE_DEPRECIATION_RATE_PER_YEAR = 0.005
AGE_DEPRECIATION_CAP = 0.20


def get_age_factor(construction_year: int) -> float:
    """
    Return the age depreciation multiplier (1.0 = no depreciation).

    Formula: 1 - min(cap, years_since_build * rate). Mock: 0.5% per year, cap 20%.

    Params:
        construction_year: Year the building was completed.

    Returns:
        Multiplier in (0.8, 1.0] (e.g. 0.95 for 10 years old).
    """
    current = date.today().year
    years = max(0, current - construction_year)
    depreciation = min(AGE_DEPRECIATION_CAP, years * AGE_DEPRECIATION_RATE_PER_YEAR)
    return round(1.0 - depreciation, 4)


# ---------------------------------------------------------------------------
# Size band: optional discount for very small or very large units.
# 85-100 ㎡ band 1.0; smaller/larger slight discount. Mock for MVP.
# ---------------------------------------------------------------------------

SIZE_BAND_RULES: list[tuple[float, float, float]] = [
    (0, 84.99, 0.98),
    (85, 100, 1.0),
    (100.01, 130, 0.99),
    (130.01, 9999, 0.97),
]


def get_size_factor(area_sqm: float) -> float:
    """
    Return the size band multiplier (1.0 for standard 85-100 ㎡ band).

    Params:
        area_sqm: Exclusive use area in ㎡.

    Returns:
        Multiplier (e.g. 0.98 for < 85 ㎡, 1.0 for 85-100 ㎡).
    """
    if area_sqm <= 0:
        return SIZE_BAND_RULES[0][2]
    for low, high, factor in SIZE_BAND_RULES:
        if low <= area_sqm <= high:
            return factor
    return SIZE_BAND_RULES[-1][2]
