"""
Tools module for LangChain tool calling.

Project role:
  Defines callable tools that the LLM can use to perform actions beyond text generation.
  Each tool follows LangChain naming conventions (verb_noun format, snake_case).
"""

from tools.search_tools import search_web, search_documents
from tools.data_tools import fetch_weather, calculate_math
from tools.utility_tools import get_current_time, convert_currency

__all__ = [
    "search_web",
    "search_documents",
    "fetch_weather",
    "calculate_math",
    "get_current_time",
    "convert_currency",
]
