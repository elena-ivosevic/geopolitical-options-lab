"""
event_study.py
================

Helpers for the geopolitical event study (Phase 5): locating trading-day
windows around an event date, and computing realized volatility and price
moves within those windows. Operates on plain pandas DataFrames with a
``Date`` column and (for realized vol) a ``log_return`` column, so it has no
dependency on any particular data source.
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def get_window(df: pd.DataFrame, t0_date, offsets: tuple[int, ...] = (-5, -1, 0, 1, 5)) -> Optional[dict]:
    """Return {offset: row} for the nearest trading day <= t0_date, then +/- offsets.

    Parameters
    ----------
    df : DataFrame with a ``Date`` column, sorted ascending.
    t0_date : the event's reference date (e.g. ``Market_T0``).
    offsets : trading-day offsets relative to the located t0 row.

    Returns
    -------
    dict mapping each offset to its row (a pandas Series), or None if
    ``t0_date`` is entirely before the data starts. An offset maps to None
    if it falls outside the available data range.
    """
    d = df.reset_index(drop=True)
    idx_candidates = d.index[d["Date"] <= t0_date]
    if len(idx_candidates) == 0:
        return None
    t0_idx = idx_candidates[-1]

    window = {}
    for off in offsets:
        i = t0_idx + off
        window[off] = d.loc[i] if 0 <= i < len(d) else None
    return window


def realized_vol(df: pd.DataFrame, t0_date, offset_start: int, offset_end: int,
                  trading_days_per_year: int = 252) -> float:
    """Annualized realized volatility of log returns over a trading-day window.

    Parameters
    ----------
    df : DataFrame with ``Date`` and ``log_return`` columns.
    t0_date : the event's reference date.
    offset_start, offset_end : inclusive trading-day offsets defining the window
        (e.g. -5, -1 for "the five trading days before the event").

    Returns
    -------
    Annualized realized volatility, or nan if the window has fewer than 2
    valid returns.
    """
    d = df.reset_index(drop=True)
    idx_candidates = d.index[d["Date"] <= t0_date]
    if len(idx_candidates) == 0:
        return float("nan")
    t0_idx = idx_candidates[-1]
    lo, hi = max(t0_idx + offset_start, 0), min(t0_idx + offset_end, len(d) - 1)
    window_returns = d.loc[lo:hi, "log_return"].dropna()
    if len(window_returns) < 2:
        return float("nan")
    return window_returns.std() * np.sqrt(trading_days_per_year)


def pct_change(before: Optional[pd.Series], after: Optional[pd.Series],
               price_col: str = "Adj Close") -> float:
    """Percent change in ``price_col`` between two rows (e.g. from ``get_window``).

    Returns nan if either row is None (i.e. out of range).
    """
    if before is None or after is None:
        return float("nan")
    return (after[price_col] / before[price_col] - 1) * 100
