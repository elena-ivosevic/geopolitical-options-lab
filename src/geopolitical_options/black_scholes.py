"""
black_scholes.py
=================

The Black-Scholes-Merton pricing engine (Phase 1). Prices European options
with a continuous dividend yield. Used directly by Phase 1's own notebook,
and imported by every later notebook and by ``geopolitical_options.hedging``
and ``geopolitical_options.model_risk`` rather than being redefined.

All functions are pure and vectorization-friendly (they accept plain floats;
callers who want vectorized behavior can pass numpy arrays, since every
operation used here is a numpy ufunc).
"""

from __future__ import annotations

import numpy as np
from scipy.stats import norm


def d1_d2(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0) -> tuple[float, float]:
    """Compute the Black-Scholes-Merton d1 and d2 terms.

    Parameters
    ----------
    S : current price of the underlying.
    K : strike price.
    T : time to expiration, in years.
    r : continuously compounded risk-free rate (annualized).
    sigma : annualized volatility of the underlying.
    q : continuous dividend yield (annualized). Defaults to 0.

    Returns
    -------
    (d1, d2)

    Raises
    ------
    ValueError
        If T or sigma is not strictly positive (the formula is undefined
        there, and division by zero would otherwise raise an opaque error).
    """
    if T <= 0 or sigma <= 0:
        raise ValueError("T and sigma must be positive.")
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    return d1, d2


def bs_price(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0,
             right: str = "call") -> float:
    """Black-Scholes-Merton price of a European call or put.

    Parameters
    ----------
    right : "call" or "put".

    Returns
    -------
    The option's theoretical price.
    """
    if right not in ("call", "put"):
        raise ValueError(f"right must be 'call' or 'put', got {right!r}")

    d1, d2 = d1_d2(S, K, T, r, sigma, q)
    if right == "call":
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
