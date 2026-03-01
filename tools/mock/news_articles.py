"""
Mock Korean real estate news articles for offline development and testing.

Contains 24 synthetic news snippets covering GTX routes, 공시지가 changes,
금리 decisions, 재건축 progress, 청약 results, and regulatory changes.

Used by tools/search_tools.py when NAVER_CLIENT_ID is not configured.
Phase 6.4 will replace this with live Naver Search API results.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class NewsArticle:
    """
    A single news article entry.

    Attributes:
        title: Article headline.
        url: Source URL (mock).
        description: 1-2 sentence summary.
        published_date: ISO date string (YYYY-MM-DD).
        keywords: List of searchable Korean keywords.
    """

    title: str
    url: str
    description: str
    published_date: str
    keywords: list[str] = field(default_factory=list)


MOCK_NEWS_ARTICLES: list[NewsArticle] = [
    # ── GTX 노선 ────────────────────────────────────────────────────────────
    NewsArticle(
        title="GTX-A 수서역 2025년 3월 개통 확정…강남·판교 30분대 연결",
        url="https://mock-news.example.com/gtx-a-suseo-opening",
        description=(
            "국토교통부는 GTX-A 노선 수서~동탄 구간이 2025년 3월 개통 예정임을 확정했다. "
            "개통 후 수서에서 동탄까지 20분, 판교까지 10분으로 단축된다."
        ),
        published_date="2024-11-15",
        keywords=["GTX", "GTX-A", "수서", "동탄", "판교", "강남", "교통", "개통"],
    ),
    NewsArticle(
        title="GTX-B 노선 인천 송도~서울역 전 구간 착공…2030년 완공 목표",
        url="https://mock-news.example.com/gtx-b-incheon-launch",
        description=(
            "인천 송도부터 서울역을 거쳐 마석까지 이어지는 GTX-B 노선이 본격 착공에 들어갔다. "
            "완공 시 송도에서 서울역까지 27분으로 단축될 전망이다."
        ),
        published_date="2024-09-03",
        keywords=["GTX", "GTX-B", "인천", "송도", "서울역", "마석", "교통"],
    ),
    NewsArticle(
        title="GTX-C 왕십리역 공사 지연…2027년으로 개통 연기",
        url="https://mock-news.example.com/gtx-c-wangsimni-delay",
        description=(
            "GTX-C 노선 왕십리 정차역 공사가 지하 문화재 발굴로 지연되어 "
            "당초 2026년에서 2027년으로 개통이 연기됐다. 성동구 일대 분양 시장에 영향이 예상된다."
        ),
        published_date="2024-08-22",
        keywords=["GTX", "GTX-C", "왕십리", "성동구", "공사 지연", "개통"],
    ),
    NewsArticle(
        title="GTX-D 김포~강남 노선 예비타당성 조사 통과",
        url="https://mock-news.example.com/gtx-d-gimpo-pass",
        description=(
            "GTX-D 김포~부천~강남 노선이 예비타당성 조사를 통과했다. "
            "김포골드라인 혼잡 해소와 강남 접근성 개선으로 김포·부천 부동산 시장 호재로 작용할 전망이다."
        ),
        published_date="2024-07-10",
        keywords=["GTX", "GTX-D", "김포", "부천", "강남", "광역교통", "예타"],
    ),
    # ── 공시지가 ────────────────────────────────────────────────────────────
    NewsArticle(
        title="2025년 공동주택 공시가격 강남 4구 평균 12% 상승",
        url="https://mock-news.example.com/official-price-2025",
        description=(
            "국토교통부가 발표한 2025년 공동주택 공시가격에서 강남·서초·송파·용산구가 "
            "평균 12% 상승했다. 재산세·종합부동산세 부담 증가로 이어질 전망이다."
        ),
        published_date="2025-01-24",
        keywords=["공시가격", "공시지가", "강남", "서초", "송파", "용산", "세금", "재산세"],
    ),
    NewsArticle(
        title="정부, 공시가격 현실화율 동결…2025년 69% 유지",
        url="https://mock-news.example.com/official-price-freeze",
        description=(
            "정부가 2025년 공시가격 현실화율을 전년과 동일한 69%로 동결하기로 했다. "
            "부동산 시장 안정과 세 부담 완화를 동시에 고려한 결정이라고 설명했다."
        ),
        published_date="2024-11-05",
        keywords=["공시가격", "현실화율", "세금", "부동산", "정책"],
    ),
    # ── 금리 ────────────────────────────────────────────────────────────────
    NewsArticle(
        title="한국은행, 기준금리 0.25%p 인하…연 3.25%로",
        url="https://mock-news.example.com/bok-rate-cut-2024",
        description=(
            "한국은행 금융통화위원회가 기준금리를 3.50%에서 3.25%로 0.25%p 인하했다. "
            "주택담보대출 금리 하락으로 부동산 거래량 회복 기대감이 높아지고 있다."
        ),
        published_date="2024-10-11",
        keywords=["금리", "한국은행", "기준금리", "대출", "주택담보대출", "부동산"],
    ),
    NewsArticle(
        title="시중은행 주담대 금리 4%대로 하락…30년 만기 월 상환액 줄어",
        url="https://mock-news.example.com/mortgage-rate-4pct",
        description=(
            "기준금리 인하에 따라 4대 시중은행의 주택담보대출 금리가 연 4%대 초반으로 내려왔다. "
            "6억짜리 아파트 30년 만기 대출 시 월 상환액이 약 15만 원 감소한다."
        ),
        published_date="2024-10-20",
        keywords=["금리", "주담대", "대출", "LTV", "DSR", "아파트", "월상환액"],
    ),
    # ── 재건축·재개발 ────────────────────────────────────────────────────────
    NewsArticle(
        title="대치동 은마아파트 재건축 관리처분인가 승인…이주 본격화",
        url="https://mock-news.example.com/eunma-management-disposal",
        description=(
            "서울시가 강남구 대치동 은마아파트 재건축 관리처분계획을 인가했다. "
            "조합원 이주가 내년 초 시작될 예정이며 주변 전세 시장에 영향을 줄 것으로 보인다."
        ),
        published_date="2024-12-03",
        keywords=["재건축", "관리처분인가", "대치동", "강남구", "은마아파트", "이주"],
    ),
    NewsArticle(
        title="잠실 MICE 복합개발 최종 승인…2030년 완공 목표",
        url="https://mock-news.example.com/jamsil-mice",
        description=(
            "서울시가 잠실 국제교류복합지구 MICE 개발 사업을 최종 승인했다. "
            "컨벤션·호텔·주거 복합 개발로 잠실·가락동 일대 지가 상승 기대감이 높다."
        ),
        published_date="2024-06-18",
        keywords=["잠실", "MICE", "개발", "송파구", "복합개발", "부동산"],
    ),
    NewsArticle(
        title="용산 국제업무지구 개발 마스터플랜 공개…2026년 착공",
        url="https://mock-news.example.com/yongsan-ibd-plan",
        description=(
            "서울시가 용산 철도정비창 부지 개발 마스터플랜을 공개했다. "
            "업무·주거·상업 복합 개발로 용산구 아파트값에 추가 상승 압력이 예상된다."
        ),
        published_date="2024-05-28",
        keywords=["용산", "국제업무지구", "개발", "용산구", "철도", "부동산"],
    ),
    NewsArticle(
        title="반포 자이 재건축 추진위 설립 인가…주민 80% 동의 확보",
        url="https://mock-news.example.com/banpo-jai-redev",
        description=(
            "서초구 반포동 반포 자이 아파트가 재건축 추진위원회 설립 인가를 받았다. "
            "주민 80.2%의 동의로 사업이 순항 중이며 시공사 선정은 내년 상반기 예정이다."
        ),
        published_date="2024-09-11",
        keywords=["재건축", "반포", "서초구", "반포동", "추진위", "안전진단"],
    ),
    NewsArticle(
        title="노원구 상계 주공 5단지 재건축 안전진단 D등급…사업 탄력",
        url="https://mock-news.example.com/sanggye-safety-test",
        description=(
            "노원구 상계동 주공 5단지가 정밀 안전진단에서 D등급을 받아 재건축 사업에 청신호가 켜졌다. "
            "1988년 준공 이후 36년 된 노후 단지로 추진위 설립이 임박했다는 평가다."
        ),
        published_date="2024-04-07",
        keywords=["재건축", "안전진단", "노원구", "상계동", "주공아파트", "노후"],
    ),
    NewsArticle(
        title="은평 뉴타운 3지구 재개발 이주 시작…2027년 새 아파트 입주",
        url="https://mock-news.example.com/eunpyeong-newtown-relocation",
        description=(
            "은평구 뉴타운 3지구 재개발 조합이 이주를 시작했다. "
            "총 2,400세대 규모로 2027년 입주 예정이며 이주 수요로 인근 전세가 상승이 우려된다."
        ),
        published_date="2024-03-14",
        keywords=["재개발", "은평구", "뉴타운", "이주", "전세", "공급"],
    ),
    # ── 마포구 학군 ─────────────────────────────────────────────────────────
    NewsArticle(
        title="마포구 공덕동 초등학교 신설 확정…2026년 개교 예정",
        url="https://mock-news.example.com/gongdeok-elementary-school",
        description=(
            "서울시교육청이 마포구 공덕동에 초등학교 신설을 확정했다. "
            "학교 반경 500m 내 아파트 단지들의 학군 수요 증가로 매매가 상승이 기대된다."
        ),
        published_date="2024-10-30",
        keywords=["마포구", "공덕동", "초등학교", "학군", "신설학교", "아파트"],
    ),
    # ── LTV / DSR 규제 ──────────────────────────────────────────────────────
    NewsArticle(
        title="금융위, 생애최초 주택구입자 LTV 90% 허용…한도 5억",
        url="https://mock-news.example.com/ltv-first-home-90pct",
        description=(
            "금융위원회가 생애 최초 주택구입자에 한해 LTV를 90%까지 허용하기로 했다. "
            "규제지역에서도 최대 5억 원까지 대출이 가능하며 내년 1월부터 시행된다."
        ),
        published_date="2024-11-20",
        keywords=["LTV", "생애최초", "대출", "규제완화", "주택구입", "금융위"],
    ),
    NewsArticle(
        title="스트레스 DSR 2단계 시행…차주 대출한도 평균 5% 축소",
        url="https://mock-news.example.com/stress-dsr-2",
        description=(
            "금융당국이 스트레스 DSR 2단계를 시행해 가계대출 총량 규제를 강화했다. "
            "차주별 대출 한도가 평균 5% 줄어들어 고가 아파트 매수 여력이 감소할 전망이다."
        ),
        published_date="2024-09-01",
        keywords=["DSR", "스트레스DSR", "대출", "규제", "가계부채", "주택"],
    ),
    # ── 청약 ────────────────────────────────────────────────────────────────
    NewsArticle(
        title="올림픽파크 포레온 특별공급 최고 경쟁률 847:1 기록",
        url="https://mock-news.example.com/olympic-foeron-subscription",
        description=(
            "둔촌주공 재건축 올림픽파크 포레온 특별공급 청약에서 장애인 특공이 847:1의 "
            "최고 경쟁률을 보였다. 일반공급 1순위 최고 경쟁률은 188:1이었다."
        ),
        published_date="2024-01-29",
        keywords=["청약", "특별공급", "경쟁률", "강동구", "올림픽파크", "재건축"],
    ),
    NewsArticle(
        title="청약통장 가입자 2,550만 명 돌파…역대 최고치 경신",
        url="https://mock-news.example.com/subscription-account-record",
        description=(
            "주택청약종합저축 가입자가 2,550만 명을 돌파해 역대 최고를 기록했다. "
            "신혼부부와 사회초년생을 중심으로 청약 준비 열기가 여전함을 보여준다."
        ),
        published_date="2024-08-12",
        keywords=["청약", "청약통장", "주택청약", "신혼부부", "분양"],
    ),
    # ── 전세 시장 ────────────────────────────────────────────────────────────
    NewsArticle(
        title="서울 아파트 전세가율 52%로 하락…갭투자 위험 감소",
        url="https://mock-news.example.com/jeonse-ratio-drop",
        description=(
            "서울 아파트 평균 전세가율이 52%로 낮아지며 갭투자 리스크가 줄어들었다는 분석이 나왔다. "
            "전문가들은 매매가 대비 전세가가 안정적인 수준으로 접어들고 있다고 평가했다."
        ),
        published_date="2024-07-05",
        keywords=["전세", "전세가율", "갭투자", "아파트", "서울", "부동산"],
    ),
    # ── 경기·지방 ────────────────────────────────────────────────────────────
    NewsArticle(
        title="판교 IT 클러스터 확장…카카오·네이버 추가 입주로 분당 수요 증가",
        url="https://mock-news.example.com/pangyo-it-expansion",
        description=(
            "경기 성남시 판교테크노밸리 3지구 개발이 확정되며 카카오·네이버 등 주요 IT 기업의 "
            "추가 입주가 예정됐다. 분당·판교 일대 아파트 임차 수요 증가가 예상된다."
        ),
        published_date="2024-06-25",
        keywords=["판교", "경기 성남시", "IT", "분당", "카카오", "네이버", "임차"],
    ),
    NewsArticle(
        title="광교신도시 광역버스 환승센터 신설…수원 영통구 교통 개선",
        url="https://mock-news.example.com/gwanggyo-bus-hub",
        description=(
            "경기도가 수원시 영통구 광교신도시에 광역버스 환승센터를 신설한다. "
            "강남까지 직결 버스 노선이 추가돼 광교 아파트 가격 상승 동력이 될 전망이다."
        ),
        published_date="2024-05-15",
        keywords=["광교", "수원", "경기 수원시", "버스", "교통", "환승센터"],
    ),
    NewsArticle(
        title="해운대 엘시티 랜드마크 효과…부산 해운대구 매매가 연 8% 상승",
        url="https://mock-news.example.com/haeundae-elcity-effect",
        description=(
            "해운대 엘시티 입주 이후 인근 아파트 매매가가 연 8% 상승한 것으로 나타났다. "
            "관광 인프라와 고급 주거 이미지가 결합돼 해운대구 전반에 프리미엄이 형성됐다."
        ),
        published_date="2024-04-22",
        keywords=["해운대", "엘시티", "부산 해운대구", "매매가", "프리미엄"],
    ),
    NewsArticle(
        title="서울 토지거래허가구역 강남·송파 일부 구역 해제 검토",
        url="https://mock-news.example.com/land-transaction-zone-review",
        description=(
            "서울시가 강남·송파구 일부 아파트 단지의 토지거래허가구역 지정 해제를 검토 중이다. "
            "해제 시 갭투자 수요 유입이 우려되며 시장 과열 가능성이 있다는 우려도 제기됐다."
        ),
        published_date="2024-12-10",
        keywords=["토지거래허가", "강남", "송파", "규제", "갭투자", "해제"],
    ),
]


def search_mock_news(query: str, max_results: int = 5) -> list[NewsArticle]:
    """
    Search mock news articles for Korean real estate keywords.

    Matches articles whose title, description, or keywords contain any word
    from the query (case-insensitive, whitespace-split).

    Params:
        query: Search query string.
        max_results: Maximum number of articles to return.

    Returns:
        List of matching NewsArticle objects, ordered by score then date.
    """
    query_terms = [t.strip() for t in query.split() if t.strip()]
    if not query_terms:
        return MOCK_NEWS_ARTICLES[:max_results]

    scored: list[tuple[int, NewsArticle]] = []
    for article in MOCK_NEWS_ARTICLES:
        searchable = " ".join([
            article.title,
            article.description,
            " ".join(article.keywords),
        ])
        score = sum(1 for term in query_terms if term in searchable)
        if score > 0:
            scored.append((score, article))

    scored.sort(key=lambda x: (-x[0], x[1].published_date), reverse=False)
    # sort descending by score, then descending by date
    scored.sort(key=lambda x: (-x[0], x[1].published_date))
    return [article for _, article in scored[:max_results]]
