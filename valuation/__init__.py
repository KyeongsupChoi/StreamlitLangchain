"""
Korean real estate valuation domain.

Project role:
  Provides property models, valuation result types, and (in later steps)
  the valuation engine and factor rules. Used by the Streamlit valuation
  UI and optionally by chat tools.
"""

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
]
