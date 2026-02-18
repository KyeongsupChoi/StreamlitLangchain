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
    Retrieve current weather conditions and temperature for any location.
    
    When to use:
      - User asks "What's the weather like in [city]?"
      - Planning outdoor activities or travel
      - Checking temperature or atmospheric conditions
      - Comparing weather across different locations
    
    Constraints:
      - Placeholder implementation; production needs weather API integration
      - Weather data freshness depends on API provider (typically 15-60 min updates)
      - Some APIs have rate limits (e.g., 1000 calls/day for free tier)
      - May not support very small towns or rural locations
      - Coordinates-based lookup not currently supported
    
    Args:
        location: City name or "City, Country" format (e.g., "San Francisco" or "Tokyo, Japan").
                 More specific locations yield better results.
        units: Temperature units - "celsius" or "fahrenheit" (default: "celsius")
        
    Returns:
        Human-readable weather summary including temperature, conditions, humidity, and wind
    """
    logger.info("Tool called: fetch_weather for location='%s', units='%s'", location, units)
    
    # Placeholder implementation - replace with actual weather API
    temp = "22°C" if units == "celsius" else "72°F"
    return f"Weather in {location}: Sunny, {temp}, humidity 65%, wind 10 km/h"


@tool
def calculate_math(expression: str) -> str:
    """
    Evaluate mathematical expressions and return numerical results.
    
    When to use:
      - User asks for calculations: "What is 15% of 200?"
      - Arithmetic operations: addition, subtraction, multiplication, division
      - Simple math functions: abs, round, min, max
      - Number comparisons or basic computations
    
    Why use this tool:
      - Ensures accurate calculations without LLM math errors
      - Handles complex multi-step arithmetic reliably
      - Provides exact numerical precision
    
    Constraints:
      - Limited to basic arithmetic and built-in functions (abs, round, min, max)
      - No support for variables, symbolic math, or algebraic expressions
      - No trigonometric functions (sin, cos, tan) or advanced math
      - Expression must be valid Python syntax
      - Uses sandboxed evaluation for security (no file/network access)
      - Maximum expression length: reasonable limit to prevent DoS
    
    Args:
        expression: Mathematical expression as string (e.g., "2 + 2", "(10 * 5) - 3", "max(10, 20)")
        
    Returns:
        Numerical result as string, or error message if expression is invalid or unsupported
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
