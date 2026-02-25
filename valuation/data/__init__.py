"""
Mock data layer for Korean real estate valuation.

Project role:
  Provides comparable transaction data and official land prices for the
  valuation engine. Currently returns mock data; swap implementations for
  real API clients (data.go.kr) in Phase 2.
"""

from valuation.data.comparables import get_comparables
from valuation.data.official_price import get_official_land_price_per_sqm

__all__ = ["get_comparables", "get_official_land_price_per_sqm"]
