"""
greeks.py
=========

Black-Scholes-Merton Greeks (Phase 1): Delta, Gamma, Vega, Theta, Rho, for
both calls and puts. Depends only on ``black_scholes.d1_d2`` so there is a
single implementation of d1/d2 shared across pricing and Greeks.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import norm

from .black_scholes import d1_d2


def bs_greeks(S: float, K: float, T: float, r: float, sigma: float, q: float = 0.0,
              right: str = "call") -> dict[str, float]:
    """Compute all five core Greeks for a European call or put.

    Returns
    -------
    dict with keys: "delta", "gamma", "vega", "theta", "rho".

    Notes
    -----
    - Vega is scaled per 1 percentage point of volatility (market convention),
      not per 1.00 (100%).
    - Theta is per calendar day, not per year.
    - Rho is scaled per 1 percentage point of the risk-free rate.
    """
    if right not in ("call", "put"):
        raise ValueError(f"right must be 'call' or 'put', got {right!r}")

    d1, d2 = d1_d2(S, K, T, r, sigma, q)
    pdf_d1 = norm.pdf(d1)
    disc_q = np.exp(-q * T)
    disc_r = np.exp(-r * T)

    gamma = disc_q * pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * disc_q * pdf_d1 * np.sqrt(T) / 100

    if right == "call":
        delta = disc_q * norm.cdf(d1)
        theta = (
            -S * disc_q * pdf_d1 * sigma / (2 * np.sqrt(T))
            - r * K * disc_r * norm.cdf(d2)
            + q * S * disc_q * norm.cdf(d1)
        ) / 365
        rho = K * T * disc_r * norm.cdf(d2) / 100
    else:
        delta = disc_q * (norm.cdf(d1) - 1)
        theta = (
            -S * disc_q * pdf_d1 * sigma / (2 * np.sqrt(T))
            + r * K * disc_r * norm.cdf(-d2)
            - q * S * disc_q * norm.cdf(-d1)
        ) / 365
        rho = -K * T * disc_r * norm.cdf(-d2) / 100

    return {"delta": delta, "gamma": gamma, "vega": vega, "theta": theta, "rho": rho}
