"""
Search-related tools for web and document searching.

Tool naming conventions:
  - verb_noun format (search_web, search_documents)
  - Descriptive and specific
  - snake_case for consistency
  - Concise but unambiguous
"""

from __future__ import annotations

import logging
import os

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the internet for current information, news, and web content.

    When to use:
      - User asks about recent events or breaking news
      - Questions requiring up-to-date information (stock prices, weather, sports scores)
      - Finding websites, articles, or online resources
      - Fact-checking or verifying current information
      - Topics outside the model's knowledge cutoff date

    Why use this tool:
      - LLMs have knowledge cutoff dates; this provides current information
      - Answers questions about recent events and real-time data
      - Retrieves specific facts and figures that change frequently

    Constraints:
      - Falls back to mock Korean real estate news when NAVER_CLIENT_ID is absent
      - API rate limits apply (e.g., 100 queries/day for free tier)
      - Search results may include ads or sponsored content
      - Result quality depends on query formulation
      - No deep web or authentication-required content access
      - Response time: typically 1-3 seconds per search

    Args:
        query: Search query string. Use specific keywords for better results.
               Natural language queries work but may be less precise.
        max_results: Maximum number of results to return (1-10). Default is 5.
                    More results = longer processing time.

    Returns:
        Formatted list of search results with titles, snippets, and URLs
    """
    logger.info("Tool called: search_web with query='%s'", query)

    if not os.getenv("NAVER_CLIENT_ID"):
        return _search_mock_news(query, max_results)

    # Phase 6.4: replace with live Naver Search API call.
    return f"Search results for '{query}':\n1. Result placeholder 1\n2. Result placeholder 2"


def _search_mock_news(query: str, max_results: int) -> str:
    """Return mock Korean real estate news formatted as a search result string."""
    from tools.mock.news_articles import search_mock_news

    articles = search_mock_news(query, max_results)
    if not articles:
        return f"[Mock] 검색 결과 없음: '{query}'"

    lines = [f"[Mock] '{query}' 검색 결과:"]
    for i, art in enumerate(articles, 1):
        lines.append(
            f"{i}. {art.title}\n"
            f"   {art.description}\n"
            f"   출처: {art.url} ({art.published_date})"
        )
    return "\n".join(lines)


@tool
def search_documents(query: str, collection: str = "default") -> str:
    """
    Search internal document repositories and knowledge bases for relevant information.

    When to use:
      - User asks about company policies, procedures, or internal guidelines
      - Questions about product documentation or technical specs
      - Retrieving information from uploaded documents or knowledge bases
      - Finding specific sections in large document collections
      - Compliance, HR, or legal document lookups

    Why use this tool:
      - Provides accurate, source-attributed information from trusted documents
      - Searches private/internal content not available via web search
      - Maintains document version control and freshness
      - Enables RAG (Retrieval-Augmented Generation) workflows

    Constraints:
      - Placeholder implementation; production needs vector DB (Pinecone, Weaviate, ChromaDB)
      - Search quality depends on document indexing and embedding quality
      - Only searches indexed documents; recent uploads may not be available (indexing lag: 5-15 min)
      - Collection names must exist; invalid collections return no results
      - Maximum query length: 500 characters
      - Results limited to top semantic matches (no exhaustive search)

    Args:
        query: Natural language search query. More specific queries yield better results.
               Include key terms, names, or concepts for precise matching.
        collection: Document collection name to search (e.g., "policies", "technical-docs", "hr-handbook").
                   Default is "default" collection. Must be pre-configured.

    Returns:
        Relevant document excerpts with source attribution (document name, page/section).
        Returns up to 5 most relevant passages.
    """
    logger.info("Tool called: search_documents with query='%s', collection='%s'", query, collection)

    try:
        from knowledge.retriever import retrieve

        docs = retrieve(query, k=5)
        if not docs:
            return f"'{query}'에 대한 문서를 찾지 못했습니다. (knowledge base가 비어 있거나 관련 문서가 없습니다.)"

        lines = [f"[지식베이스] '{query}' 검색 결과 ({len(docs)}건):"]
        for i, doc in enumerate(docs, 1):
            lines.append(f"\n{i}. [출처: {doc['source']}]\n{doc['content']}")
        return "\n".join(lines)

    except ImportError:
        logger.debug("chromadb not installed — returning placeholder for search_documents")
        return (
            f"문서 검색 기능을 사용하려면 chromadb를 설치하세요: pip install chromadb\n"
            f"(쿼리: '{query}')"
        )
    except Exception as exc:
        logger.warning("search_documents error: %s", exc)
        return f"문서 검색 중 오류가 발생했습니다: {exc}"
