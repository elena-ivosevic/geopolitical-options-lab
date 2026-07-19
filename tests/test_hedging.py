import math

import pytest

from geopolitical_options.hedging import option_payoff, protection_efficiency, unhedged_pnl


def test_call_payoff_is_zero_when_out_of_the_money():
    payoff = option_payoff(S0=100, ret_pct=-5, K=110, right="call", shares=1)
    assert payoff == 0


def test_call_payoff_is_positive_when_in_the_money():
    # S0=100, +10% -> S_end=110, K=105 -> payoff = 5 per share
    payoff = option_payoff(S0=100, ret_pct=10, K=105, right="call", shares=1)
    assert payoff == pytest.approx(5.0)


def test_put_payoff_is_positive_when_in_the_money():
    # S0=100, -10% -> S_end=90, K=95 -> payoff = 5 per share
    payoff = option_payoff(S0=100, ret_pct=-10, K=95, right="put", shares=1)
    assert payoff == pytest.approx(5.0)


def test_payoff_scales_with_shares():
    payoff_1 = option_payoff(S0=100, ret_pct=10, K=100, right="call", shares=1)
    payoff_10 = option_payoff(S0=100, ret_pct=10, K=100, right="call", shares=10)
    assert payoff_10 == pytest.approx(payoff_1 * 10)


def test_invalid_right_raises():
    with pytest.raises(ValueError):
        option_payoff(S0=100, ret_pct=10, K=100, right="straddle", shares=1)


def test_unhedged_pnl_weighted_correctly():
    scenario = {"SPY": -2.0, "XLY": 4.0}
    weights = {"SPY": 0.5, "XLY": 0.5, "cash_bonds": 0.0}
    pnl = unhedged_pnl(scenario, weights, portfolio_value=1_000_000)
    # 0.5 * 1e6 * -0.02 + 0.5 * 1e6 * 0.04 = -10,000 + 20,000 = 10,000
    assert pnl == pytest.approx(10_000)


def test_unhedged_pnl_skips_flat_holdings():
    scenario = {"SPY": -2.0}
    weights = {"SPY": 0.9, "cash_bonds": 0.1}
    pnl = unhedged_pnl(scenario, weights, portfolio_value=1_000_000)
    assert pnl == pytest.approx(0.9 * 1_000_000 * -0.02)


def test_unhedged_pnl_defaults_missing_ticker_to_zero_return():
    scenario = {}  # no data for this holding
    weights = {"GLD": 1.0}
    pnl = unhedged_pnl(scenario, weights, portfolio_value=1_000_000)
    assert pnl == 0


def test_protection_efficiency_basic_ratio():
    eff = protection_efficiency(loss_reduction=20_000, hedge_cost=5_000)
    assert eff == pytest.approx(4.0)


def test_protection_efficiency_nan_for_zero_or_negative_cost():
    assert math.isnan(protection_efficiency(loss_reduction=1000, hedge_cost=0))
    assert math.isnan(protection_efficiency(loss_reduction=1000, hedge_cost=-500))
