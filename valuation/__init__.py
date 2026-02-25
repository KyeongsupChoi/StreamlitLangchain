"""
Korean real estate valuation domain.

Project role:
  Provides property models, factor rules, mock data, and a deterministic
  valuation engine. Used by the Streamlit valuation UI and optionally by
  chat tools.
"""

from valuation.engine import run_valuation
from valuation.models import (
    FactorContribution,
    Property,
    PropertyType,
    ValuationResult,
)

__all__ = [
    "FactorContribution",
    "Property",
    "PropertyType",
    "ValuationResult",
    "run_valuation",
]
