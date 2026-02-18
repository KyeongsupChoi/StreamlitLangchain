"""
Data retrieval and calculation tools.

Tool naming conventions:
  - verb_noun format (fetch_weather, calculate_math)
  - Descriptive and specific
  - snake_case for consistency
  - Concise but unambiguous
"""

from __future__ import annotations

import logging
from typing import Literal

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def fetch_weather(
    location: str,
    units: Literal["celsius", "fahrenheit"] = "celsius"
) -> str:
    """
    Fetch current weather information for a specific location.
    
    Use this tool when the user asks about weather conditions, temperature,
    or atmospheric data for a location.
    
    Args:
        location: City name or location (e.g., "San Francisco" or "New York, NY")
        units: Temperature units - either "celsius" or "fahrenheit" (default: "celsius")
        
    Returns:
        Current weather information including temperature and conditions
    """
    logger.info("Tool called: fetch_weather for location='%s', units='%s'", location, units)
    
    # Placeholder implementation - replace with actual weather API
    temp = "22°C" if units == "celsius" else "72°F"
    return f"Weather in {location}: Sunny, {temp}, humidity 65%, wind 10 km/h"


@tool
def calculate_math(expression: str) -> str:
    """
    Calculate mathematical expressions and return the result.
    
    Use this tool when the user asks for mathematical calculations,
    arithmetic operations, or numerical computations.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2 + 2", "sqrt(16)", "10 * 5")
        
    Returns:
        The calculated result or an error message
        
    Note:
        For security, this uses a safe evaluation method. Complex expressions
        involving variables or custom functions may not be supported.
    """
    logger.info("Tool called: calculate_math with expression='%s'", expression)
    
    try:
        # Safe evaluation using Python's eval with restricted builtins
        # In production, use a safer math parser like py_expression_eval or sympy
        allowed_names = {"abs": abs, "round": round, "min": min, "max": max}
        result = eval(expression, {"__builtins__": {}}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        logger.warning("Math calculation failed for '%s': %s", expression, e)
        return f"Error calculating '{expression}': {str(e)}"
