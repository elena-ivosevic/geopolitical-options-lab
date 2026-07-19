"""
model_risk.py
==============

Model-risk stress tests (Phase 7): a discrete delta-hedging replication
simulation, used to quantify how much a constant-volatility assumption and
discrete rebalancing cost a hedger through a real price path (including a
real overnight jump).
"""

from __future__ import annotations

from typing import Sequence

import numpy as np

from .black_scholes import bs_price
from .greeks import bs_greeks


def simulate_delta_hedge(price_series: Sequence[float], K: float, T_days: int, r: float,
                          sigma_pricing: float, q: float, rebalance_every: int,
                          trading_days_per_year: int = 252) -> dict:
    """Replicate a short ATM/OTM/ITM call via discrete delta-hedging.

    The seller collects the Black-Scholes premium at inception (priced with
    ``sigma_pricing``, held constant throughout -- this is deliberately the
    "wrong" assumption being stress-tested), then rebalances a stock hedge
    every ``rebalance_every`` trading days using the *actual* observed price
    path, financing the hedge at rate ``r``.

    Parameters
    ----------
    price_series : actual daily closing prices, starting at the option's
        inception date. Must have at least ``T_days + 1`` entries.
    K : strike price.
    T_days : trading days to maturity.
    r : risk-free rate.
    sigma_pricing : the (constant) volatility used to price and delta-hedge.
    q : dividend yield.
    rebalance_every : rebalance every N trading days (1 = daily).

    Returns
    -------
    dict with keys: "premium_received", "final_stock_price", "payoff",
    "hedging_pnl". ``hedging_pnl`` is the seller's net result: premium
    collected, plus hedge trading and financing, minus the option's payoff
    at maturity. In a perfect, continuously-hedged, correctly-priced world
    this would be ~0; deviations are the cost of discretization and/or a
    volatility mismatch.

    Raises
    ------
    ValueError
        If ``price_series`` doesn't have enough data to reach maturity.
    """
    S = list(price_series[: T_days + 1])
    n = len(S) - 1
    if n < T_days:
        raise ValueError("Not enough price history for the requested horizon.")

    T0 = n / trading_days_per_year
    premium = bs_price(S[0], K, T0, r, sigma_pricing, q, "call")

    cash = premium
    stock_position = 0.0

    for i in range(n + 1):
        if i > 0:
            cash *= np.exp(r / trading_days_per_year)

        is_rebalance_day = (i % rebalance_every == 0) and i < n
        is_maturity = i == n

        if is_rebalance_day:
            remaining = n - i
            T_t = remaining / trading_days_per_year
            if T_t > 0:
                delta_t = bs_greeks(S[i], K, T_t, r, sigma_pricing, q, "call")["delta"]
            else:
                delta_t = 1.0 if S[i] > K else 0.0
            trade = delta_t - stock_position
            cash -= trade * S[i]
            stock_position = delta_t

        if is_maturity:
            cash += stock_position * S[i]
            payoff = max(S[i] - K, 0.0)
            return {
                "premium_received": premium,
                "final_stock_price": S[i],
                "payoff": payoff,
                "hedging_pnl": cash - payoff,
            }

    raise RuntimeError("Simulation did not reach maturity.")  # pragma: no cover
