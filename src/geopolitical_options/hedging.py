"""
hedging.py
==========

Portfolio hedging simulation (Phase 6): scenario P&L for a weighted
portfolio, and option payoff at expiration. Used to compare a no-hedge
baseline against a protective put, a collar, and a cross-asset call overlay.

A note on realism: these functions compute the payoff of a hedge at a single
scenario-ending price -- they do not model bid-ask spreads, transaction
costs, or early exercise. Combined with ``black_scholes.bs_price`` for the
premium, this produces a **historically calibrated hedge simulation**, not a
replay of tradable historical option quotes (this project has no historical
option-chain data; see the README's data-provenance notes).
"""

from __future__ import annotations

from typing import Mapping


def unhedged_pnl(scenario: Mapping[str, float], portfolio_weights: Mapping[str, float],
                  portfolio_value: float, flat_holdings: tuple[str, ...] = ("cash_bonds",)) -> float:
    """Weighted portfolio P&L under a scenario of per-asset percentage returns.

    Parameters
    ----------
    scenario : {ticker: percent_return}, e.g. {"SPY": -1.2, "XLY": 3.1}.
    portfolio_weights : {holding: weight}, weights should sum to 1.0.
    portfolio_value : total portfolio value in dollars.
    flat_holdings : holdings assumed to have 0% return in this scenario
        (e.g. cash/bonds), skipped rather than requiring a scenario entry.

    Returns
    -------
    Dollar P&L (not percent).
    """
    pnl = 0.0
    for holding, weight in portfolio_weights.items():
        if holding in flat_holdings:
            continue
        ret_pct = scenario.get(holding, 0.0)
        pnl += weight * portfolio_value * (ret_pct / 100)
    return pnl


def option_payoff(S0: float, ret_pct: float, K: float, right: str, shares: float) -> float:
    """Payoff of a long option position at expiration, given a scenario return.

    Parameters
    ----------
    S0 : underlying price today.
    ret_pct : the scenario's percentage return for this underlying, applied
        to S0 to get the terminal price.
    K : strike price.
    right : "call" or "put".
    shares : the position size (share-equivalent notional).

    Returns
    -------
    Dollar payoff (>= 0), before subtracting the premium paid.
    """
    if right not in ("call", "put"):
        raise ValueError(f"right must be 'call' or 'put', got {right!r}")

    S_end = S0 * (1 + ret_pct / 100)
    if right == "call":
        payoff = max(S_end - K, 0.0)
    else:
        payoff = max(K - S_end, 0.0)
    return payoff * shares


def protection_efficiency(loss_reduction: float, hedge_cost: float) -> float:
    """Loss reduction per dollar of hedge premium, vs. the no-hedge baseline.

    Returns nan if hedge_cost is 0 or negative (a net-credit hedge, like a
    collar that receives more premium than it pays, makes this ratio
    undefined rather than informative).
    """
    if hedge_cost is None or hedge_cost <= 0:
        return float("nan")
    return loss_reduction / hedge_cost
