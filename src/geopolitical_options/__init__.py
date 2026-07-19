"""
geopolitical_options
=====================

Core, reusable calculations for the "From Hormuz to the Portfolio" project.

This package holds the pricing engine, Greeks, implied-volatility solver,
event-study helpers, hedging simulation, and model-risk utilities that the
project notebooks import rather than redefine. Extracting these from the
notebooks keeps a single source of truth for the math and makes it testable
with pytest (see ``tests/``) independent of any notebook execution.
"""

from .black_scholes import d1_d2, bs_price
from .greeks import bs_greeks
from .implied_volatility import implied_volatility

__all__ = [
    "d1_d2",
    "bs_price",
    "bs_greeks",
    "implied_volatility",
]

__version__ = "0.1.0"
