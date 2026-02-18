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
    Search the web for information using a search engine.
    
    Use this tool when the user asks for current information, recent events,
    or data that requires internet access.
    
    Args:
        query: The search query string
        max_results: Maximum number of results to return (default: 5)
        
    Returns:
        A formatted string with search results
    """
    logger.info("Tool called: search_web with query='%s'", query)
    
    # Placeholder implementation - replace with actual search API
    return f"Search results for '{query}':\n1. Result placeholder 1\n2. Result placeholder 2"


@tool
def search_documents(query: str, collection: str = "default") -> str:
    """
    Search through internal document collections or knowledge bases.
    
    Use this tool when the user asks questions about internal documentation,
    company policies, or stored knowledge.
    
    Args:
        query: The search query string
        collection: The document collection to search in (default: "default")
        
    Returns:
        Relevant document excerpts matching the query
    """
    logger.info("Tool called: search_documents with query='%s', collection='%s'", query, collection)
    
    # Placeholder implementation - replace with actual document search
    return f"Document search results from '{collection}' collection for '{query}':\nNo documents found (placeholder)."
