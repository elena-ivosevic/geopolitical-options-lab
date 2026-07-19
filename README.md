# Impacts of Geopolitical Tensions on Cross-Asset Allocations
### An Option-Implied Risk Dashboard

A Black-Scholes-based research project measuring how the 2026 Iran&ndash;Israel&ndash;U.S.
conflict and Strait of Hormuz disruptions moved oil, airline, consumer, healthcare, and
broad-market risk &mdash; and testing whether standard option hedges would have actually
protected a hypothetical wealth-management client portfolio through it.

**[Open the interactive dashboard](./dashboard/dashboard.html)** &mdash; the fastest way to see the
whole project. Download it and open in any browser, or enable GitHub Pages on this repo to view
it live (Settings &rarr; Pages &rarr; deploy from `/dashboard`).

---

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
├── dashboard/
│   └── dashboard.html          Interactive dashboard (open directly in any browser)
├── notebooks/
│   ├── 01_black_scholes_engine.ipynb       Core pricing engine + Greeks + validation tests
│   ├── 02_market_data_cleaning.ipynb       Option-chain cleaning pipeline (synthetic*)
│   ├── 03_implied_volatility.ipynb         Implied-vol solver + market-implied Greeks (synthetic*)
│   ├── 04_volatility_surfaces.ipynb        Term structure + vol surfaces (synthetic*)
│   ├── 05_geopolitical_event_study.ipynb   The core research: real event study
│   ├── 06_portfolio_hedging.ipynb          $1M hypothetical client, real hedge comparison
│   └── 07_model_risk.ipynb                 Where Black-Scholes breaks (real jump data)
├── data/
│   ├── real_historical_prices/      Real daily OHLCV for all 7 assets + VIX/OVX (source: yfinance)
│   ├── phase5_real_event_study/     Real computed event metrics and correlation shifts
│   ├── phase6_real_hedging/         Real hedge scenario results and Greeks
│   ├── phase7_real_model_risk/      Real delta-hedging simulation and pricing-error results
│   ├── phase2_synthetic_market_data/    Synthetic option chains (see note below)
│   ├── phase3_synthetic_implied_vol/    Synthetic implied-vol solve results
│   └── phase4_synthetic_surfaces/       Synthetic volatility surfaces
├── scripts/
│   └── fetch_event_data.py     Standalone script to re-pull real historical data via yfinance
└── requirements.txt
```

## What's real data vs. synthetic data, and why

**Notebooks 05, 06, and 07, and the dashboard, run entirely on real data**: actual daily closing
prices for USO, JETS, SPY, XLE, XLY, XLV, and GLD, plus VIX and OVX as volatility proxies, pulled
via `yfinance` (see `scripts/fetch_event_data.py`).

**Notebooks 02, 03, and 04 run on synthetic data**, generated directly from the Notebook 01
Black-Scholes engine plus a hand-coded volatility smile. This is because historical *per-strike
option chain* data (needed for a real implied-volatility surface) generally requires paid access
&mdash; ORATS, CBOE DataShop, OptionMetrics, or a Bloomberg/Refinitiv terminal &mdash; which wasn't
available for this project. Free tools like `yfinance` only expose **live** option chains, not
historical ones.

This substitution is real and worth being upfront about in any interview: the pricing engine,
the cleaning pipeline, and the implied-vol solver are all genuinely functional and validated code
(Notebook 01 passes a full suite of no-arbitrage and put-call-parity tests), demonstrated on
realistic synthetic data rather than hidden behind a "trust me" placeholder. The research
conclusions that actually matter (Notebooks 05&ndash;07) are drawn from real market data, not the
synthetic set.

## Running the notebooks

```bash
pip install -r requirements.txt
jupyter notebook notebooks/
```

Notebooks 05&ndash;07 depend on the CSVs in `data/real_historical_prices/`, which are already
included in this repo. To refresh them with more recent data:

```bash
python scripts/fetch_event_data.py
```

(Requires `yfinance` and `pandas`; see the script's docstring for details.)

## The dashboard

`dashboard/dashboard.html` is a single self-contained file (no build step, no server) with five
views:

1. **Market Overview** &mdash; real price paths and volatility proxies across the full period
2. **Pricing Calculator** &mdash; the Black-Scholes engine, live and interactive, in the browser
3. **Event Study** &mdash; the real volatility-transmission analysis, switchable per event
4. **Hedge Simulator** &mdash; the $1M portfolio comparison, rescalable to any portfolio size
5. **Model Risk** &mdash; the delta-hedging-through-a-jump and constant-volatility-failure results

Just download and open it, or host it via GitHub Pages for a shareable link.

## Résumé bullet

> Developed a Python-based geopolitical options dashboard using Black-Scholes to calculate implied
> volatility, Greeks, volatility surfaces, and event-driven pricing errors across oil, airline,
> consumer, healthcare, and equity ETFs; evaluated protective puts, collars, and cross-asset hedges
> for a hypothetical private-client portfolio using real market data from the 2026 Iran-Israel
> conflict.

## Limitations

- Historical per-strike option-chain data (real skew, real vega) isn't included &mdash; see the
  synthetic-data note above.
- VIX and OVX are broad volatility-index proxies, not this project's own measured implied
  volatility for each specific asset.
- The "Mild Escalation" scenario in the hedging notebook is an interpolation (35% of the real
  Major Disruption event's magnitude), since no event in this project's real sample was actually
  mild &mdash; labeled explicitly wherever it's used.
