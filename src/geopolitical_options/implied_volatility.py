"""
implied_volatility.py
======================

Numerical implied-volatility solver (Phase 3): recovers the Black-Scholes
volatility that reproduces an observed market price, via bisection
(``scipy.optimize.brentq``). Includes no-arbitrage bound checks and never
raises on bad input -- it reports a structured failure instead, since a
market-data pipeline will inevitably contain quotes the model can't invert.
"""

from __future__ import annotations

from typing import NamedTuple

import numpy as np
from scipy.optimize import brentq

from .black_scholes import bs_price


class ImpliedVolResult(NamedTuple):
    iv: float
    success: bool
    message: str


def implied_volatility(market_price: float, S: float, K: float, T: float, r: float,
                        q: float, right: str, low: float = 0.005,
                        high: float = 5.0) -> ImpliedVolResult:
    """Solve for the Black-Scholes implied volatility that reproduces ``market_price``.

    Parameters
    ----------
    market_price : the observed option price.
    S, K, T, r, q, right : the other Black-Scholes-Merton inputs (see ``black_scholes.bs_price``).
    low, high : the volatility search bracket (annualized). Widened defaults
        (0.5% to 500%) accommodate stale or illiquid quotes that occasionally
        require extreme implied vols to match.

    Returns
    -------
    ImpliedVolResult(iv, success, message)
        ``iv`` is ``nan`` when ``success`` is False. ``message`` explains why
        (e.g. "no_sign_change_in_bracket", "price_below_intrinsic").
    """
    if market_price <= 0 or S <= 0 or K <= 0 or T <= 0:
        return ImpliedVolResult(float("nan"), False, "invalid_inputs")

    if right == "call":
        intrinsic = max(S * np.exp(-q * T) - K * np.exp(-r * T), 0.0)
        upper_bound = S * np.exp(-q * T)
    elif right == "put":
        intrinsic = max(K * np.exp(-r * T) - S * np.exp(-q * T), 0.0)
        upper_bound = K * np.exp(-r * T)
    else:
        return ImpliedVolResult(float("nan"), False, f"invalid_right:{right}")

    if market_price < intrinsic - 1e-6:
        return ImpliedVolResult(float("nan"), False, "price_below_intrinsic")
    if market_price > upper_bound + 1e-6:
        return ImpliedVolResult(float("nan"), False, "price_above_no_arbitrage_bound")

    def error(sigma: float) -> float:
        return bs_price(S, K, T, r, sigma, q, right) - market_price

    try:
        f_low, f_high = error(low), error(high)
        if f_low * f_high > 0:
            return ImpliedVolResult(float("nan"), False, "no_sign_change_in_bracket")
        iv = brentq(error, low, high, xtol=1e-6, maxiter=200)
        return ImpliedVolResult(iv, True, "ok")
    except Exception as exc:  # pragma: no cover - defensive catch-all
        return ImpliedVolResult(float("nan"), False, f"solver_error:{exc}")
