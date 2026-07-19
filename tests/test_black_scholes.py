import numpy as np
import pytest

from geopolitical_options.black_scholes import bs_price, d1_d2


S, K, T, r, sigma, q = 100.0, 100.0, 0.5, 0.03, 0.25, 0.01


def test_call_price_rises_with_spot():
    c_low = bs_price(90, K, T, r, sigma, q, "call")
    c_high = bs_price(110, K, T, r, sigma, q, "call")
    assert c_high > c_low


def test_put_price_falls_with_spot():
    p_low = bs_price(90, K, T, r, sigma, q, "put")
    p_high = bs_price(110, K, T, r, sigma, q, "put")
    assert p_high < p_low


def test_call_price_rises_with_volatility():
    c_lowvol = bs_price(S, K, T, r, 0.10, q, "call")
    c_hivol = bs_price(S, K, T, r, 0.40, q, "call")
    assert c_hivol > c_lowvol


def test_put_price_rises_with_volatility():
    p_lowvol = bs_price(S, K, T, r, 0.10, q, "put")
    p_hivol = bs_price(S, K, T, r, 0.40, q, "put")
    assert p_hivol > p_lowvol


def test_longer_dated_call_has_more_time_value():
    c_short = bs_price(S, K, 0.1, r, sigma, q, "call")
    c_long = bs_price(S, K, 1.0, r, sigma, q, "call")
    assert c_long > c_short


def test_put_call_parity():
    """C - P == S*e^(-qT) - K*e^(-rT), to within numerical tolerance."""
    C = bs_price(S, K, T, r, sigma, q, "call")
    P = bs_price(S, K, T, r, sigma, q, "put")
    lhs = C - P
    rhs = S * np.exp(-q * T) - K * np.exp(-r * T)
    assert abs(lhs - rhs) < 1e-8


def test_call_price_bounded_by_spot():
    """A call can never be worth more than the (discounted) underlying itself."""
    c = bs_price(S, K, T, r, sigma, q, "call")
    assert 0 <= c <= S


def test_put_price_bounded_by_discounted_strike():
    p = bs_price(S, K, T, r, sigma, q, "put")
    assert 0 <= p <= K * np.exp(-r * T)


def test_deep_itm_call_approaches_intrinsic_value():
    """A deep in-the-money call with tiny time value should be close to intrinsic."""
    c = bs_price(1000, K, 1 / 365, r, sigma, q, "call")
    intrinsic = 1000 * np.exp(-q * (1 / 365)) - K * np.exp(-r * (1 / 365))
    assert abs(c - intrinsic) < 1.0


@pytest.mark.parametrize("bad_T", [0, -0.5])
def test_zero_or_negative_time_raises(bad_T):
    with pytest.raises(ValueError):
        d1_d2(S, K, bad_T, r, sigma, q)


@pytest.mark.parametrize("bad_sigma", [0, -0.1])
def test_zero_or_negative_volatility_raises(bad_sigma):
    with pytest.raises(ValueError):
        d1_d2(S, K, T, r, bad_sigma, q)


def test_invalid_right_raises():
    with pytest.raises(ValueError):
        bs_price(S, K, T, r, sigma, q, right="straddle")
