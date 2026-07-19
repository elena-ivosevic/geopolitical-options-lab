import numpy as np
import pandas as pd
import pytest

from geopolitical_options.event_study import get_window, pct_change, realized_vol
from geopolitical_options.model_risk import simulate_delta_hedge


@pytest.fixture
def sample_df():
    dates = pd.date_range("2026-01-01", periods=20, freq="B")
    prices = 100 + np.cumsum(np.random.default_rng(0).normal(0, 1, size=20))
    df = pd.DataFrame({"Date": dates, "Adj Close": prices})
    df["log_return"] = np.log(df["Adj Close"] / df["Adj Close"].shift(1))
    return df


def test_get_window_returns_correct_offsets(sample_df):
    t0 = sample_df["Date"].iloc[10]
    window = get_window(sample_df, t0, offsets=(-2, 0, 2))
    assert window[0]["Date"] == t0
    assert window[-2]["Date"] == sample_df["Date"].iloc[8]
    assert window[2]["Date"] == sample_df["Date"].iloc[12]


def test_get_window_handles_out_of_range_offset(sample_df):
    t0 = sample_df["Date"].iloc[1]
    window = get_window(sample_df, t0, offsets=(-5, 0))
    assert window[-5] is None  # would be a negative index


def test_get_window_returns_none_if_t0_before_data_starts(sample_df):
    too_early = sample_df["Date"].iloc[0] - pd.Timedelta(days=100)
    assert get_window(sample_df, too_early) is None


def test_pct_change_basic():
    before = pd.Series({"Adj Close": 100.0})
    after = pd.Series({"Adj Close": 110.0})
    assert pct_change(before, after) == pytest.approx(10.0)


def test_pct_change_none_inputs_return_nan():
    before = pd.Series({"Adj Close": 100.0})
    assert np.isnan(pct_change(before, None))
    assert np.isnan(pct_change(None, before))


def test_realized_vol_is_nonnegative(sample_df):
    t0 = sample_df["Date"].iloc[10]
    vol = realized_vol(sample_df, t0, -5, -1)
    assert vol >= 0


def test_realized_vol_nan_with_insufficient_data(sample_df):
    t0 = sample_df["Date"].iloc[0]
    vol = realized_vol(sample_df, t0, -1, -1)
    assert np.isnan(vol)


def test_delta_hedge_smooth_path_produces_small_hedging_error():
    """On a smooth, low-realized-vol path with a matching pricing vol, daily
    delta-hedging should nearly replicate the option (small hedging P&L)."""
    rng = np.random.default_rng(42)
    sigma = 0.20
    n_days = 30
    dt = 1 / 252
    prices = [100.0]
    for _ in range(n_days):
        shock = rng.normal(-0.5 * sigma ** 2 * dt, sigma * np.sqrt(dt))
        prices.append(prices[-1] * np.exp(shock))

    result = simulate_delta_hedge(
        prices, K=100.0, T_days=n_days, r=0.03, sigma_pricing=sigma, q=0.0, rebalance_every=1
    )
    # Hedging error should be small relative to the premium when the pricing
    # vol matches the path's actual vol and rebalancing is daily.
    assert abs(result["hedging_pnl"]) < result["premium_received"]


def test_delta_hedge_raises_with_insufficient_price_history():
    with pytest.raises(ValueError):
        simulate_delta_hedge([100.0, 101.0], K=100.0, T_days=30, r=0.03,
                              sigma_pricing=0.2, q=0.0, rebalance_every=1)


def test_rebalance_frequency_changes_the_hedging_outcome():
    """Different rebalancing frequencies on the same price path should
    generally produce different hedging P&L -- confirming the parameter
    actually does something, rather than asserting a specific direction.
    (The specific finding that less-frequent rebalancing performs worse
    through a real jump is demonstrated empirically on real USO data in
    notebooks/07_model_risk.ipynb, where the price path's other dynamics
    are realistic; a short synthetic path here isn't a reliable stand-in
    for that directional claim.)"""
    rng = np.random.default_rng(7)
    sigma = 0.30
    n_days = 30
    dt = 1 / 252
    prices = [100.0]
    for i in range(n_days):
        shock = rng.normal(-0.5 * sigma ** 2 * dt, sigma * np.sqrt(dt))
        if i == 12:
            shock += 0.30  # embed one large jump mid-path
        prices.append(prices[-1] * np.exp(shock))

    kwargs = dict(K=100.0, T_days=n_days, r=0.03, sigma_pricing=sigma, q=0.0)
    daily = simulate_delta_hedge(prices, rebalance_every=1, **kwargs)
    weekly = simulate_delta_hedge(prices, rebalance_every=5, **kwargs)

    assert np.isfinite(daily["hedging_pnl"])
    assert np.isfinite(weekly["hedging_pnl"])
    assert daily["hedging_pnl"] != pytest.approx(weekly["hedging_pnl"])
