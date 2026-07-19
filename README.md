# Impacts of Geopolitical Tensions on Cross-Asset Allocations
### An Option-Implied Geopolitical Risk Dashboard

[![tests](https://github.com/elena-ivosevic/geopolitical_options_lab/actions/workflows/tests.yml/badge.svg)](https://github.com/elena-ivosevic/geopolitical_options_lab/actions/workflows/tests.yml)

A Black-Scholes-based research project measuring how the 2026 Iran&ndash;Israel&ndash;U.S.
conflict and Strait of Hormuz disruptions moved oil, airline, consumer, healthcare, and
broad-market risk &mdash; and testing whether standard option hedges would have actually
protected a hypothetical wealth-management client portfolio through it.

**[Open the interactive dashboard &rarr;](https://elena-ivosevic.github.io/geopolitical_options_lab/)**
(once GitHub Pages is enabled &mdash; see *Running the project* below). Or download
`dashboard/index.html` and open it directly in any browser; no server or build step required.

---

## Selected results

![Hedge comparison](docs/hedge_comparison_screenshot.png)

| | |
|---|---|
| **USO move around the war's outbreak** | +29%, vs. an oil-vol proxy (OVX) that jumped 36 points |
| **Protective SPY put, same event** | -1.0x protection efficiency (it made things *worse*) |
| **Oil-linked call overlay, same event** | +7.26x protection efficiency |
| **Same option, two volatility inputs** | 64.5% difference in the model price |

## The research question

> How does the options market price geopolitical oil-supply risk, how does that risk transmit
> across sectors, and which option strategies most efficiently hedge a diversified private-client
> portfolio?

Three hypotheses were tested against real data rather than assumed:

1. **H1**: Middle East escalation raises implied volatility most directly in oil and energy assets.
2. **H2**: Airlines and consumer discretionary show more downside concern from higher energy costs
   and squeezed consumer spending.
3. **H3**: Healthcare behaves more defensively than airlines, consumer discretionary, and broad
   equities.

## Key findings

- **Oil absorbed the shock first and hardest.** USO moved +29% and its volatility proxy (OVX)
  jumped 36 points around the war's outbreak (Feb 28&ndash;Mar 2, 2026) &mdash; by far the largest
  reaction of any asset in the study.
- **A protective SPY put would have barely helped, or even hurt.** The broad market itself moved
  less than 1% during the same event. A hedge built to protect against a market crash missed
  where the actual risk was.
- **An oil-linked call overlay outperformed dramatically** in the same scenario (protection
  efficiency of 7.26x, vs. -1.0x for the SPY put) &mdash; because the real risk was concentrated in
  oil, not the broad market.
- **Black-Scholes' constant-volatility assumption visibly failed around the event.** The same
  option, priced with pre-event vs. post-event volatility, produced prices 64.5% apart. Even daily
  delta-hedging couldn't fully absorb a real overnight jump in oil prices (+13%, Mar 5&rarr;6, 2026).

## Project structure

```
geopolitical-options-lab/
├── src/geopolitical_options/        Core, reusable, unit-tested calculations
│   ├── black_scholes.py             Pricing engine (d1/d2, European call/put price)
│   ├── greeks.py                    Delta, Gamma, Vega, Theta, Rho
│   ├── implied_volatility.py        Numerical IV solver (brentq), with no-arbitrage checks
│   ├── event_study.py               Trading-day windows, realized volatility, pct change
│   ├── hedging.py                   Portfolio P&L, option payoff, protection efficiency
│   └── model_risk.py                Discrete delta-hedging replication simulator
├── tests/                           pytest suite (56 tests, 98% coverage of src/)
├── .github/workflows/tests.yml      CI: runs the test suite on every push and PR
├── dashboard/
│   └── index.html                   Interactive dashboard (open directly, or served by GitHub Pages)
├── notebooks/
│   ├── 01_black_scholes_engine.ipynb       Builds and validates the pricing engine from scratch
│   ├── 02_market_data_cleaning.ipynb       Option-chain cleaning pipeline (synthetic*)
│   ├── 03_implied_volatility.ipynb         Implied-vol solver + market-implied Greeks (synthetic*)
│   ├── 04_volatility_surfaces.ipynb        Term structure + vol surfaces (synthetic*)
│   ├── 05_geopolitical_event_study.ipynb   The core research: real event study
│   ├── 06_portfolio_hedging.ipynb          $1M hypothetical client, historically calibrated hedge sim
│   └── 07_model_risk.ipynb                 Where Black-Scholes breaks (real jump data)
├── data/
│   ├── real_historical_prices/      Real daily OHLCV for all 7 assets + VIX/OVX (source: yfinance)
│   ├── phase5_real_event_study/     Real computed event metrics and correlation shifts
│   ├── phase6_real_hedging/         Hedge scenario results and Greeks (see hedging note below)
│   ├── phase7_real_model_risk/      Real delta-hedging simulation and pricing-error results
│   ├── phase2_synthetic_market_data/    Synthetic option chains (see note below)
│   ├── phase3_synthetic_implied_vol/    Synthetic implied-vol solve results
│   └── phase4_synthetic_surfaces/       Synthetic volatility surfaces
├── scripts/
│   └── fetch_event_data.py     Standalone script to re-pull real historical data via yfinance
├── pyproject.toml               Makes src/geopolitical_options pip-installable (`pip install -e .`)
└── requirements.txt
```

Notebooks 02&ndash;07 import their core calculations from `src/geopolitical_options/` rather than
redefining them inline (Notebook 01 is the one exception: it *builds* the engine from scratch, as
Phase 1's own subject, and `src/black_scholes.py`/`greeks.py` mirror that same implementation).
This keeps one tested source of truth for the math instead of seven slightly-drifting copies.

## What's real data vs. synthetic data, and why

**Notebooks 05, 06, and 07, and the dashboard, run on real historical price data**: actual daily
closing prices for USO, JETS, SPY, XLE, XLY, XLV, and GLD, plus VIX and OVX as volatility proxies,
pulled via `yfinance` (see `scripts/fetch_event_data.py`).

**Notebooks 02, 03, and 04 run on synthetic data**, generated directly from the `src/` Black-Scholes
engine plus a hand-coded volatility smile. This is because historical *per-strike option chain*
data (needed for a real implied-volatility surface) generally requires paid access &mdash; ORATS,
CBOE DataShop, OptionMetrics, or a Bloomberg/Refinitiv terminal &mdash; which wasn't available for
this project. Free tools like `yfinance` only expose **live** option chains, not historical ones.

This substitution is real and worth being upfront about in any interview: the pricing engine,
the cleaning pipeline, and the implied-vol solver are all genuinely functional, unit-tested code
(see `tests/`, 56 tests / 98% coverage, run automatically in CI), demonstrated on realistic
synthetic data rather than hidden behind a "trust me" placeholder. The research conclusions that
actually matter (Notebooks 05&ndash;07) are drawn from real market data, not the synthetic set.

### A note on precision: "historically calibrated," not "historically traded"

Notebook 06's hedge comparison prices each hedge (protective put, collar, oil call overlay) using
the `src/black_scholes.py` engine, with:

- **strikes** set mechanically at 5% out-of-the-money from the current spot,
- **volatility inputs** taken from VIX/OVX levels (broad proxies, not this project's own
  per-security implied volatility),
- **no bid-ask spread, transaction costs, or early-exercise modeling**, and
- **scenario returns** calibrated from real, measured Phase 5 event moves, applied over a
  30-calendar-day hedge horizon that doesn't exactly match the ~10-trading-day windows those
  moves were measured over (a documented simplification).

That combination is best described as a **historically calibrated hedge simulation** &mdash; the
scenarios are real, the pricing engine is real and tested, but the specific option premiums were
never quoted or tradable, since this project has no historical option-chain data. Worth stating
precisely rather than calling every number in that section "real."

## Running the project

```bash
git clone https://github.com/elena-ivosevic/geopolitical_options_lab.git
cd geopolitical_options_lab
pip install -e ".[dev]"        # installs src/geopolitical_options + pytest
pytest tests/                  # 56 tests, should all pass
jupyter notebook notebooks/    # open and run any notebook
```

Notebooks 05&ndash;07 depend on the CSVs in `data/real_historical_prices/`, which are already
included in this repo. To refresh them with more recent data:

```bash
python scripts/fetch_event_data.py
```

(Requires `yfinance` and `pandas`; see the script's docstring for details.)

### Enabling the live dashboard link

Settings &rarr; Pages &rarr; Source: "Deploy from a branch" &rarr; Branch: `main`, folder:
`/dashboard` &rarr; Save. GitHub will publish a URL like
`https://elena-ivosevic.github.io/geopolitical_options_lab/` within a couple of minutes.

### Repository "About" section (GitHub setup)

Suggested description:

> Python options research platform studying geopolitical shocks, volatility transmission, and
> portfolio hedging.

Suggested topics:

```
quantitative-finance  options-pricing  black-scholes  geopolitical-risk
portfolio-hedging  event-study  python
```

## The dashboard

`dashboard/index.html` is a single self-contained file (no build step, no server) with five
views:

1. **Market Overview** &mdash; real price paths and volatility proxies across the full period
2. **Pricing Calculator** &mdash; the Black-Scholes engine, live and interactive, in the browser
3. **Event Study** &mdash; the real volatility-transmission analysis, switchable per event
4. **Hedge Simulator** &mdash; the $1M portfolio comparison, rescalable to any portfolio size
5. **Model Risk** &mdash; the delta-hedging-through-a-jump and constant-volatility-failure results

## Résumé bullets

> Developed a Python options-research platform analyzing geopolitical volatility transmission
> across seven equity, energy, airline, consumer, healthcare, and commodity ETFs using
> Black-Scholes, Greeks, an implied-volatility solver, and event-study methodology on real
> market data.

> Compared protective puts, collars, and cross-asset overlays for a hypothetical $1 million
> portfolio using a historically calibrated hedge simulation, finding an oil-linked hedge
> achieved 7.26x protection efficiency during the studied supply shock &mdash; while a
> broad-market protective put underperformed a no-hedge baseline.

## Limitations

- Historical per-strike option-chain data (real skew, real vega, real quoted premiums) isn't
  included &mdash; see the synthetic-data and hedge-precision notes above.
- VIX and OVX are broad volatility-index proxies, not this project's own measured implied
  volatility for each specific asset.
- The "Mild Escalation" scenario in the hedging notebook is an interpolation (35% of the real
  Major Disruption event's magnitude), since no event in this project's real sample was actually
  mild &mdash; labeled explicitly wherever it's used.
- The event study currently compares simple before/after windows around three events rather than
  a full benchmark-adjusted event-study specification (abnormal returns vs. an estimation window,
  bootstrap confidence intervals, sensitivity to window length, non-event-period comparison).
  That rigor would strengthen the statistical claims further and is a natural next iteration.
- The hedging simulation does not model bid-ask spreads, transaction costs, or early exercise.
