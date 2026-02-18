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
      - Placeholder implementation; production needs search API (Google, Bing, SerpAPI)
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
    
    # Placeholder implementation - replace with actual search API
    return f"Search results for '{query}':\n1. Result placeholder 1\n2. Result placeholder 2"


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
    
    # Placeholder implementation - replace with actual document search
    return f"Document search results from '{collection}' collection for '{query}':\nNo documents found (placeholder)."
