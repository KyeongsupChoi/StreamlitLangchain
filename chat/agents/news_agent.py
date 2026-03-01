"""
News analysis agent for Korean real estate market intelligence.

Project role:
  Runs a two-step structured chain: web search → LLM structured extraction.
  Returns a NewsAnalysis object with entities, sentiment, and impacted complexes.
  Called by the News-First UI entry point (Phase 3.1).
"""

from __future__ import annotations

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from chat.prompts import NEWS_EXTRACTION_PROMPT
from tools.news_tools import NewsAnalysis
from tools.search_tools import search_web

logger = logging.getLogger(__name__)


def run_news_agent(input_text: str, model) -> NewsAnalysis:
    """
    Run the news analysis agent on a URL or keyword.

    Fetches news content via search_web, then calls the LLM with structured
    output (Pydantic) to extract entities, sentiment, and impacted complexes.

    Params:
        input_text: Naver News URL or Korean search keyword
                    (e.g. "GTX-D 김포 연장", "은마아파트 재건축").
        model: A LangChain chat model that supports with_structured_output().

    Returns:
        NewsAnalysis with entities, regions, infrastructure, sentiment,
        summary, and impacted_complexes populated.
    """
    logger.info("run_news_agent: input='%s'", input_text)

    # Step 1 — Fetch news content via search_web (mock or live)
    news_content = search_web.invoke({"query": input_text})
    logger.info("run_news_agent: fetched %d chars of news content", len(news_content))

    # Step 2 — Structured extraction via LLM
    structured_model = model.with_structured_output(NewsAnalysis)
    prompt_text = NEWS_EXTRACTION_PROMPT.format(news_content=news_content)

    try:
        result: NewsAnalysis = structured_model.invoke([
            SystemMessage(content="You are a Korean real estate news analyst."),
            HumanMessage(content=prompt_text),
        ])
        logger.info(
            "run_news_agent: sentiment=%s regions=%s complexes=%s",
            result.sentiment, result.regions, result.impacted_complexes,
        )
        return result

    except Exception as exc:
        logger.warning(
            "run_news_agent: structured extraction failed (%s) — returning neutral fallback",
            exc,
        )
        return NewsAnalysis(
            entities=[],
            regions=[],
            infrastructure="unknown",
            sentiment="neutral",
            summary=f"분석 실패: {exc}",
            impacted_complexes=[],
        )
