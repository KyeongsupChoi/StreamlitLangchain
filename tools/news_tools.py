"""
News parsing tool for Korean real estate market analysis.

Project role:
  Provides NewsAnalysis (Pydantic model) and parse_news_article (LangChain @tool)
  for extracting structured real estate entities and sentiment from news content.
  Used by the ReAct agent loop and by chat/agents/news_agent.py.
"""

from __future__ import annotations

import logging
from typing import Literal

from langchain_core.tools import tool
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class NewsAnalysis(BaseModel):
    """
    Structured output from a Korean real estate news analysis.

    Attributes:
        entities: Named entities — complex names, developers, agencies.
        regions: Impacted administrative regions (e.g. "서울 강남구").
        infrastructure: Key infrastructure or policy type (e.g. "GTX-A", "재건축").
        sentiment: Market impact direction.
        summary: 1-2 sentence Korean summary.
        impacted_complexes: Apartment complex names likely to be affected.
    """

    entities: list[str] = Field(
        default_factory=list,
        description="Named entities: complex names, developers, agencies",
    )
    regions: list[str] = Field(
        default_factory=list,
        description="Impacted administrative regions (e.g. '서울 강남구')",
    )
    infrastructure: str = Field(
        default="",
        description="Key infrastructure or policy type (e.g. 'GTX-A', '재건축', '금리')",
    )
    sentiment: Literal["bullish", "bearish", "neutral"] = Field(
        default="neutral",
        description="Market impact: bullish=호재, bearish=악재, neutral=중립",
    )
    summary: str = Field(
        default="",
        description="Korean 1-2 sentence summary of the article",
    )
    impacted_complexes: list[str] = Field(
        default_factory=list,
        description="Apartment complex names likely to be affected",
    )

    @property
    def sentiment_korean(self) -> str:
        """Return Korean label for the sentiment."""
        return {"bullish": "호재", "bearish": "악재", "neutral": "중립"}.get(
            self.sentiment, "중립"
        )

    def to_report(self) -> str:
        """Format analysis as a human-readable Korean report string."""
        lines = [
            f"**시장 심리:** {self.sentiment_korean} ({self.sentiment})",
            f"**핵심 인프라/이슈:** {self.infrastructure or '없음'}",
            f"**요약:** {self.summary or '요약 없음'}",
            f"**영향 지역:** {', '.join(self.regions) or '없음'}",
            f"**주요 단지:** {', '.join(self.impacted_complexes) or '없음'}",
            f"**언급 엔티티:** {', '.join(self.entities) or '없음'}",
        ]
        return "\n".join(lines)


@tool
def parse_news_article(url_or_keyword: str) -> str:
    """Fetch and return Korean real estate news content for analysis.

    Searches for the given URL or keyword and returns the raw content as a
    formatted string. Use this when a user asks about the impact of news on
    real estate prices, infrastructure projects, or redevelopment plans.

    Args:
        url_or_keyword: A Naver News URL or a Korean search keyword
                        (e.g. "GTX-D 김포 연장", "강남 공시지가 상승").

    Returns:
        Formatted news search results as a string for LLM consumption.
    """
    from tools.search_tools import search_web

    logger.info("Tool called: parse_news_article with input='%s'", url_or_keyword)
    raw = search_web.invoke({"query": url_or_keyword})
    return f"[뉴스 검색 결과: '{url_or_keyword}']\n{raw}"
