"""
Mock apartment complex directory for Korean real estate.

Contains 52 named complexes across 13 districts with building specs
(location, age, units, parking ratio, FAR).

Used by valuation/data/complex_directory.py.
Phase 6.3 will replace address lookup with live Kakao/Naver Geocoding API.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Complex:
    """
    Specification for a named apartment complex.

    Attributes:
        name: Complex display name (e.g. "반포 자이").
        district: Administrative district (e.g. "서울 서초구").
        dong: Sub-district (e.g. "반포동").
        lat: Approximate latitude (WGS84).
        lng: Approximate longitude (WGS84).
        building_year: Year construction completed.
        total_units: Number of residential units.
        parking_ratio: Parking spaces per unit (e.g. 1.3).
        far: Floor Area Ratio in percent (e.g. 250.0).
        canonical_address: Full human-readable address string.
        property_type: One of 아파트, 오피스텔, 단독주택.
    """

    name: str
    district: str
    dong: str
    lat: float
    lng: float
    building_year: int
    total_units: int
    parking_ratio: float
    far: float
    canonical_address: str
    property_type: str


COMPLEXES: list[Complex] = [
    # ── 서울 강남구 ─────────────────────────────────────────────────────────
    Complex(
        name="래미안 대치 팰리스",
        district="서울 강남구", dong="대치동",
        lat=37.4936, lng=127.0609,
        building_year=2015, total_units=1278, parking_ratio=1.5, far=249.9,
        canonical_address="서울특별시 강남구 대치동 1008",
        property_type="아파트",
    ),
    Complex(
        name="타워팰리스 3차",
        district="서울 강남구", dong="도곡동",
        lat=37.4893, lng=127.0466,
        building_year=2004, total_units=480, parking_ratio=2.1, far=999.0,
        canonical_address="서울특별시 강남구 도곡동 467",
        property_type="아파트",
    ),
    Complex(
        name="아크로 리버 파크",
        district="서울 강남구", dong="개포동",
        lat=37.4818, lng=127.0528,
        building_year=2016, total_units=1612, parking_ratio=1.6, far=299.9,
        canonical_address="서울특별시 강남구 개포동 12",
        property_type="아파트",
    ),
    Complex(
        name="강남 센트럴 아이파크",
        district="서울 강남구", dong="역삼동",
        lat=37.5004, lng=127.0365,
        building_year=2018, total_units=342, parking_ratio=1.0, far=800.0,
        canonical_address="서울특별시 강남구 역삼동 823",
        property_type="오피스텔",
    ),
    Complex(
        name="강남 파크자이",
        district="서울 강남구", dong="삼성동",
        lat=37.5140, lng=127.0571,
        building_year=2012, total_units=258, parking_ratio=1.1, far=750.0,
        canonical_address="서울특별시 강남구 삼성동 72",
        property_type="오피스텔",
    ),
    # ── 서울 서초구 ─────────────────────────────────────────────────────────
    Complex(
        name="반포 자이",
        district="서울 서초구", dong="반포동",
        lat=37.5055, lng=126.9996,
        building_year=2009, total_units=3410, parking_ratio=1.4, far=249.9,
        canonical_address="서울특별시 서초구 반포동 19",
        property_type="아파트",
    ),
    Complex(
        name="래미안 퍼스티지",
        district="서울 서초구", dong="반포동",
        lat=37.5062, lng=127.0012,
        building_year=2009, total_units=2444, parking_ratio=1.5, far=249.9,
        canonical_address="서울특별시 서초구 반포동 3",
        property_type="아파트",
    ),
    Complex(
        name="아크로 반포",
        district="서울 서초구", dong="반포동",
        lat=37.5041, lng=126.9979,
        building_year=2020, total_units=1088, parking_ratio=1.8, far=299.9,
        canonical_address="서울특별시 서초구 반포동 1-1",
        property_type="아파트",
    ),
    Complex(
        name="서초 SK HUB",
        district="서울 서초구", dong="서초동",
        lat=37.4834, lng=127.0322,
        building_year=2015, total_units=196, parking_ratio=1.0, far=700.0,
        canonical_address="서울특별시 서초구 서초동 1308",
        property_type="오피스텔",
    ),
    # ── 서울 용산구 ─────────────────────────────────────────────────────────
    Complex(
        name="한남 더 힐",
        district="서울 용산구", dong="한남동",
        lat=37.5375, lng=126.9963,
        building_year=2011, total_units=600, parking_ratio=2.5, far=199.9,
        canonical_address="서울특별시 용산구 한남동 810",
        property_type="아파트",
    ),
    Complex(
        name="파크 한남",
        district="서울 용산구", dong="한남동",
        lat=37.5388, lng=126.9981,
        building_year=2021, total_units=305, parking_ratio=2.8, far=249.9,
        canonical_address="서울특별시 용산구 한남동 독서당로 294",
        property_type="아파트",
    ),
    Complex(
        name="이촌 현대아파트",
        district="서울 용산구", dong="이촌동",
        lat=37.5231, lng=126.9680,
        building_year=1994, total_units=1066, parking_ratio=0.8, far=199.9,
        canonical_address="서울특별시 용산구 이촌동 302-126",
        property_type="아파트",
    ),
    # ── 서울 송파구 ─────────────────────────────────────────────────────────
    Complex(
        name="잠실 엘스",
        district="서울 송파구", dong="잠실동",
        lat=37.5108, lng=127.0879,
        building_year=2008, total_units=5678, parking_ratio=1.2, far=249.9,
        canonical_address="서울특별시 송파구 잠실동 6",
        property_type="아파트",
    ),
    Complex(
        name="리센츠",
        district="서울 송파구", dong="잠실동",
        lat=37.5115, lng=127.0863,
        building_year=2008, total_units=5563, parking_ratio=1.2, far=249.9,
        canonical_address="서울특별시 송파구 잠실동 20",
        property_type="아파트",
    ),
    Complex(
        name="헬리오시티",
        district="서울 송파구", dong="가락동",
        lat=37.4946, lng=127.1200,
        building_year=2018, total_units=9510, parking_ratio=1.3, far=299.9,
        canonical_address="서울특별시 송파구 가락동 98",
        property_type="아파트",
    ),
    Complex(
        name="잠실 트리지움",
        district="서울 송파구", dong="잠실동",
        lat=37.5129, lng=127.0901,
        building_year=2007, total_units=302, parking_ratio=1.0, far=700.0,
        canonical_address="서울특별시 송파구 잠실동 올림픽로 212",
        property_type="오피스텔",
    ),
    # ── 서울 성동구 ─────────────────────────────────────────────────────────
    Complex(
        name="아크로 서울 포레스트",
        district="서울 성동구", dong="성수동",
        lat=37.5445, lng=127.0553,
        building_year=2020, total_units=280, parking_ratio=2.0, far=399.9,
        canonical_address="서울특별시 성동구 성수동1가 685",
        property_type="아파트",
    ),
    Complex(
        name="왕십리 텐즈힐",
        district="서울 성동구", dong="하왕십리동",
        lat=37.5601, lng=127.0236,
        building_year=2013, total_units=1703, parking_ratio=1.3, far=249.9,
        canonical_address="서울특별시 성동구 하왕십리동 1000",
        property_type="아파트",
    ),
    Complex(
        name="서울숲 리버뷰 자이",
        district="서울 성동구", dong="성수동",
        lat=37.5460, lng=127.0570,
        building_year=2023, total_units=452, parking_ratio=1.6, far=299.9,
        canonical_address="서울특별시 성동구 성수동2가 289",
        property_type="아파트",
    ),
    # ── 서울 마포구 ─────────────────────────────────────────────────────────
    Complex(
        name="마포 래미안 푸르지오",
        district="서울 마포구", dong="공덕동",
        lat=37.5469, lng=126.9507,
        building_year=2014, total_units=3885, parking_ratio=1.3, far=249.9,
        canonical_address="서울특별시 마포구 공덕동 255",
        property_type="아파트",
    ),
    Complex(
        name="e편한세상 공덕",
        district="서울 마포구", dong="공덕동",
        lat=37.5480, lng=126.9520,
        building_year=2019, total_units=826, parking_ratio=1.4, far=249.9,
        canonical_address="서울특별시 마포구 공덕동 아현로 238",
        property_type="아파트",
    ),
    Complex(
        name="공덕 자이",
        district="서울 마포구", dong="공덕동",
        lat=37.5462, lng=126.9495,
        building_year=2016, total_units=1009, parking_ratio=1.3, far=249.9,
        canonical_address="서울특별시 마포구 공덕동 독막로 266",
        property_type="아파트",
    ),
    Complex(
        name="공덕 SK 리더스 뷰",
        district="서울 마포구", dong="공덕동",
        lat=37.5455, lng=126.9488,
        building_year=2010, total_units=412, parking_ratio=1.0, far=700.0,
        canonical_address="서울특별시 마포구 공덕동 716",
        property_type="오피스텔",
    ),
    # ── 서울 광진구 ─────────────────────────────────────────────────────────
    Complex(
        name="광장 현대아파트",
        district="서울 광진구", dong="광장동",
        lat=37.5551, lng=127.0986,
        building_year=1999, total_units=1152, parking_ratio=0.9, far=199.9,
        canonical_address="서울특별시 광진구 광장동 451",
        property_type="아파트",
    ),
    Complex(
        name="더샵 스타리버",
        district="서울 광진구", dong="광장동",
        lat=37.5562, lng=127.1001,
        building_year=2021, total_units=595, parking_ratio=1.5, far=299.9,
        canonical_address="서울특별시 광진구 광장동 아차산로 533",
        property_type="아파트",
    ),
    # ── 서울 영등포구 ────────────────────────────────────────────────────────
    Complex(
        name="여의도 삼부아파트",
        district="서울 영등포구", dong="여의도동",
        lat=37.5219, lng=126.9245,
        building_year=1982, total_units=1584, parking_ratio=0.5, far=149.9,
        canonical_address="서울특별시 영등포구 여의도동 14",
        property_type="아파트",
    ),
    Complex(
        name="여의도 파크원 자이",
        district="서울 영등포구", dong="여의도동",
        lat=37.5226, lng=126.9258,
        building_year=2021, total_units=486, parking_ratio=2.0, far=499.9,
        canonical_address="서울특별시 영등포구 여의도동 36",
        property_type="아파트",
    ),
    Complex(
        name="영등포 센트럴 자이",
        district="서울 영등포구", dong="영등포동",
        lat=37.5180, lng=126.9041,
        building_year=2018, total_units=388, parking_ratio=1.1, far=700.0,
        canonical_address="서울특별시 영등포구 영등포동 경인로 855",
        property_type="오피스텔",
    ),
    # ── 서울 노원구 ─────────────────────────────────────────────────────────
    Complex(
        name="상계 주공아파트 5단지",
        district="서울 노원구", dong="상계동",
        lat=37.6561, lng=127.0651,
        building_year=1988, total_units=1980, parking_ratio=0.4, far=149.9,
        canonical_address="서울특별시 노원구 상계동 541",
        property_type="아파트",
    ),
    Complex(
        name="중계 그린아파트",
        district="서울 노원구", dong="중계동",
        lat=37.6422, lng=127.0694,
        building_year=1992, total_units=744, parking_ratio=0.5, far=149.9,
        canonical_address="서울특별시 노원구 중계동 301-6",
        property_type="아파트",
    ),
    Complex(
        name="노원 꿈에그린",
        district="서울 노원구", dong="월계동",
        lat=37.6190, lng=127.0576,
        building_year=2007, total_units=620, parking_ratio=1.1, far=199.9,
        canonical_address="서울특별시 노원구 월계동 광운로 53",
        property_type="아파트",
    ),
    # ── 서울 은평구 ─────────────────────────────────────────────────────────
    Complex(
        name="불광 미성아파트",
        district="서울 은평구", dong="불광동",
        lat=37.6087, lng=126.9279,
        building_year=1985, total_units=960, parking_ratio=0.4, far=149.9,
        canonical_address="서울특별시 은평구 불광동 산 70",
        property_type="아파트",
    ),
    Complex(
        name="은평 래미안",
        district="서울 은평구", dong="응암동",
        lat=37.5993, lng=126.9132,
        building_year=2018, total_units=1028, parking_ratio=1.2, far=199.9,
        canonical_address="서울특별시 은평구 응암동 증산로 71",
        property_type="아파트",
    ),
    # ── 서울 강동구 ─────────────────────────────────────────────────────────
    Complex(
        name="고덕 래미안 힐스테이트",
        district="서울 강동구", dong="고덕동",
        lat=37.5567, lng=127.1533,
        building_year=2019, total_units=4066, parking_ratio=1.3, far=249.9,
        canonical_address="서울특별시 강동구 고덕동 고덕로 272",
        property_type="아파트",
    ),
    Complex(
        name="올림픽파크 포레온",
        district="서울 강동구", dong="둔촌동",
        lat=37.5269, lng=127.1345,
        building_year=2023, total_units=12032, parking_ratio=1.5, far=299.9,
        canonical_address="서울특별시 강동구 둔촌동 올림픽로 435",
        property_type="아파트",
    ),
    # ── 서울 동작구 ─────────────────────────────────────────────────────────
    Complex(
        name="흑석 아크로 리버하임",
        district="서울 동작구", dong="흑석동",
        lat=37.5091, lng=126.9620,
        building_year=2019, total_units=1073, parking_ratio=1.5, far=299.9,
        canonical_address="서울특별시 동작구 흑석동 노량진로 235",
        property_type="아파트",
    ),
    Complex(
        name="사당 래미안 이수",
        district="서울 동작구", dong="사당동",
        lat=37.4872, lng=126.9811,
        building_year=2009, total_units=1070, parking_ratio=1.2, far=249.9,
        canonical_address="서울특별시 동작구 사당동 사당로 301",
        property_type="아파트",
    ),
    # ── 경기 성남시 ─────────────────────────────────────────────────────────
    Complex(
        name="파크뷰 자이",
        district="경기 성남시", dong="분당구 정자동",
        lat=37.3618, lng=127.1101,
        building_year=2006, total_units=1388, parking_ratio=1.5, far=249.9,
        canonical_address="경기도 성남시 분당구 정자동 210",
        property_type="아파트",
    ),
    Complex(
        name="서판교 산운마을",
        district="경기 성남시", dong="수정구 고등동",
        lat=37.4354, lng=127.1432,
        building_year=2010, total_units=1640, parking_ratio=1.4, far=199.9,
        canonical_address="경기도 성남시 수정구 고등동 산운로 15",
        property_type="아파트",
    ),
    Complex(
        name="분당 파크뷰 삼성",
        district="경기 성남시", dong="분당구 야탑동",
        lat=37.4117, lng=127.1261,
        building_year=2000, total_units=814, parking_ratio=1.0, far=199.9,
        canonical_address="경기도 성남시 분당구 야탑동 야탑로 81",
        property_type="아파트",
    ),
    Complex(
        name="판교 더샵 퍼스트파크",
        district="경기 성남시", dong="분당구 판교동",
        lat=37.3943, lng=127.1113,
        building_year=2014, total_units=510, parking_ratio=1.3, far=600.0,
        canonical_address="경기도 성남시 분당구 판교동 삼평로 53",
        property_type="오피스텔",
    ),
    # ── 경기 수원시 ─────────────────────────────────────────────────────────
    Complex(
        name="광교 자이 더 명작",
        district="경기 수원시", dong="영통구 이의동",
        lat=37.2815, lng=127.0452,
        building_year=2019, total_units=2529, parking_ratio=1.5, far=249.9,
        canonical_address="경기도 수원시 영통구 이의동 광교중앙로 145",
        property_type="아파트",
    ),
    Complex(
        name="영통 롯데캐슬",
        district="경기 수원시", dong="영통구 영통동",
        lat=37.2562, lng=127.0535,
        building_year=2015, total_units=1002, parking_ratio=1.3, far=249.9,
        canonical_address="경기도 수원시 영통구 영통동 영통로 107",
        property_type="아파트",
    ),
    Complex(
        name="수원 SK VIEW",
        district="경기 수원시", dong="팔달구 인계동",
        lat=37.2659, lng=127.0125,
        building_year=2016, total_units=618, parking_ratio=1.1, far=600.0,
        canonical_address="경기도 수원시 팔달구 인계동 월드컵로 310",
        property_type="오피스텔",
    ),
    # ── 부산 해운대구 ────────────────────────────────────────────────────────
    Complex(
        name="해운대 엘시티",
        district="부산 해운대구", dong="우동",
        lat=35.1661, lng=129.1618,
        building_year=2019, total_units=885, parking_ratio=2.0, far=999.0,
        canonical_address="부산광역시 해운대구 우동 마린시티2로 33",
        property_type="아파트",
    ),
    Complex(
        name="센텀 리버사이드 자이",
        district="부산 해운대구", dong="재송동",
        lat=35.1892, lng=129.1401,
        building_year=2018, total_units=2004, parking_ratio=1.3, far=249.9,
        canonical_address="부산광역시 해운대구 재송동 센텀중앙로 55",
        property_type="아파트",
    ),
    Complex(
        name="해운대 아이파크",
        district="부산 해운대구", dong="우동",
        lat=35.1640, lng=129.1592,
        building_year=2011, total_units=2631, parking_ratio=1.4, far=299.9,
        canonical_address="부산광역시 해운대구 우동 해운대해변로 298",
        property_type="아파트",
    ),
    Complex(
        name="해운대 마린시티 자이",
        district="부산 해운대구", dong="중동",
        lat=35.1584, lng=129.1605,
        building_year=2016, total_units=784, parking_ratio=1.2, far=700.0,
        canonical_address="부산광역시 해운대구 중동 마린시티1로 55",
        property_type="오피스텔",
    ),
]
