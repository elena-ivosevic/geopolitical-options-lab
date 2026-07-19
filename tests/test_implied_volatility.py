import pytest

from geopolitical_options.black_scholes import bs_price
from geopolitical_options.implied_volatility import implied_volatility


S, K, T, r, q = 100.0, 100.0, 0.5, 0.03, 0.01


@pytest.mark.parametrize("true_sigma", [0.10, 0.25, 0.50, 0.90])
@pytest.mark.parametrize("right", ["call", "put"])
def test_recovers_known_volatility(true_sigma, right):
    """Price at a known sigma, solve back, and recover that same sigma."""
    price = bs_price(S, K, T, r, true_sigma, q, right)
    result = implied_volatility(price, S, K, T, r, q, right)
    assert result.success
    assert result.iv == pytest.approx(true_sigma, abs=1e-4)


def test_zero_price_fails_gracefully():
    result = implied_volatility(0.0, S, K, T, r, q, "call")
    assert not result.success
    assert result.message == "invalid_inputs"


def test_negative_price_fails_gracefully():
    result = implied_volatility(-5.0, S, K, T, r, q, "call")
    assert not result.success


def test_price_above_no_arbitrage_bound_fails_gracefully():
    """A call can never cost more than the (discounted) spot itself."""
    result = implied_volatility(S * 2, S, K, T, r, q, "call")
    assert not result.success
    assert result.message == "price_above_no_arbitrage_bound"


def test_price_below_intrinsic_fails_gracefully():
    """A deep ITM call priced below its own intrinsic value is impossible."""
    deep_itm_S = 500.0
    intrinsic = deep_itm_S - K
    result = implied_volatility(intrinsic * 0.5, deep_itm_S, K, T, r, q, "call")
    assert not result.success
    assert result.message == "price_below_intrinsic"


def test_never_raises_on_garbage_input():
    """The solver should report failure, never throw, on nonsensical input."""
    result = implied_volatility(float("nan"), S, K, T, r, q, "call")
    assert not result.success


def test_invalid_right_fails_gracefully():
    result = implied_volatility(5.0, S, K, T, r, q, "straddle")
    assert not result.success
    assert result.message.startswith("invalid_right")
