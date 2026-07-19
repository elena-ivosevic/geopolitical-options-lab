import pytest

from geopolitical_options.greeks import bs_greeks


S, K, T, r, sigma, q = 100.0, 100.0, 0.5, 0.03, 0.25, 0.01


def test_call_delta_in_zero_one():
    g = bs_greeks(S, K, T, r, sigma, q, "call")
    assert 0 < g["delta"] < 1


def test_put_delta_in_negative_one_zero():
    g = bs_greeks(S, K, T, r, sigma, q, "put")
    assert -1 < g["delta"] < 0


def test_gamma_is_positive_and_same_for_call_and_put():
    g_call = bs_greeks(S, K, T, r, sigma, q, "call")
    g_put = bs_greeks(S, K, T, r, sigma, q, "put")
    assert g_call["gamma"] > 0
    assert g_call["gamma"] == pytest.approx(g_put["gamma"])


def test_vega_is_positive_and_same_for_call_and_put():
    g_call = bs_greeks(S, K, T, r, sigma, q, "call")
    g_put = bs_greeks(S, K, T, r, sigma, q, "put")
    assert g_call["vega"] > 0
    assert g_call["vega"] == pytest.approx(g_put["vega"])


def test_call_delta_increases_as_spot_rises():
    g_low = bs_greeks(80, K, T, r, sigma, q, "call")
    g_high = bs_greeks(120, K, T, r, sigma, q, "call")
    assert g_high["delta"] > g_low["delta"]


def test_deep_itm_call_delta_approaches_one():
    g = bs_greeks(1000, K, T, r, sigma, q, "call")
    assert g["delta"] > 0.99


def test_deep_otm_call_delta_approaches_zero():
    g = bs_greeks(1, K, T, r, sigma, q, "call")
    assert g["delta"] < 0.01


def test_invalid_right_raises():
    with pytest.raises(ValueError):
        bs_greeks(S, K, T, r, sigma, q, right="not_an_option")
