"""
General utility tools for time, conversion, and formatting.

Tool naming conventions:
  - verb_noun format (get_current_time, convert_currency)
  - Descriptive and specific
  - snake_case for consistency
  - Concise but unambiguous
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_current_time(timezone_name: str = "UTC") -> str:
    """
    Get the current date and time in a specified timezone.
    
    Use this tool when the user asks about the current time, date,
    or needs time-related information.
    
    Args:
        timezone_name: Timezone name (e.g., "UTC", "America/New_York", "Europe/London")
        
    Returns:
        Current date and time in the specified timezone
    """
    logger.info("Tool called: get_current_time for timezone='%s'", timezone_name)
    
    try:
        # For simplicity, using UTC. In production, use pytz or zoneinfo for proper timezone handling
        current_time = datetime.now(timezone.utc)
        formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S %Z")
        return f"Current time in {timezone_name}: {formatted_time}"
    except Exception as e:
        logger.warning("Failed to get time for timezone '%s': %s", timezone_name, e)
        return f"Error getting time for timezone '{timezone_name}': {str(e)}"


@tool
def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str
) -> str:
    """
    Convert an amount from one currency to another using current exchange rates.
    
    Use this tool when the user asks about currency conversion, exchange rates,
    or monetary value in different currencies.
    
    Args:
        amount: The monetary amount to convert
        from_currency: Source currency code (e.g., "USD", "EUR", "GBP")
        to_currency: Target currency code (e.g., "USD", "EUR", "GBP")
        
    Returns:
        Converted amount with currency codes
    """
    logger.info(
        "Tool called: convert_currency %.2f %s to %s",
        amount, from_currency, to_currency
    )
    
    # Placeholder exchange rates - replace with actual currency API
    exchange_rates = {
        ("USD", "EUR"): 0.92,
        ("USD", "GBP"): 0.79,
        ("EUR", "USD"): 1.09,
        ("GBP", "USD"): 1.27,
    }
    
    rate_key = (from_currency.upper(), to_currency.upper())
    
    if rate_key in exchange_rates:
        converted = amount * exchange_rates[rate_key]
        return f"{amount:.2f} {from_currency} = {converted:.2f} {to_currency}"
    else:
        return f"Exchange rate not available for {from_currency} to {to_currency} (placeholder implementation)"
