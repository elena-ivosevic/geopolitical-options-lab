from pathlib import Path
import shutil
import sys

import pandas as pd
import yfinance as yf


# -----------------------------
# 1. Project settings
# -----------------------------
TICKERS = [
    "USO",
    "JETS",
    "SPY",
    "XLE",
    "XLY",
    "XLV",
    "GLD",
    "^VIX",
    "^OVX",
]

EVENTS = [
    {
        "Event_ID": "E1",
        "News_Date": "2026-02-28",
        "Market_T0": "2026-03-02",
        "Direction": "Escalation",
        "Event": "Joint U.S.-Israeli strikes begin the war with Iran",
    },
    {
        "Event_ID": "E2",
        "News_Date": "2026-04-17",
        "Market_T0": "2026-04-17",
        "Direction": "De-escalation",
        "Event": "Iran announces that the Strait of Hormuz is open",
    },
    {
        "Event_ID": "E3",
        "News_Date": "2026-06-15",
        "Market_T0": "2026-06-15",
        "Direction": "De-escalation",
        "Event": (
            "Initial U.S.-Iran agreement extends the ceasefire "
            "and moves toward reopening Hormuz"
        ),
    },
]

CALENDAR_BUFFER_DAYS = 20
OUTPUT_DIR = Path("event_data")


def safe_filename(ticker: str) -> str:
    """Convert Yahoo symbols such as ^VIX into normal filenames."""
    return ticker.replace("^", "")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    events = pd.DataFrame(EVENTS)
    events["News_Date"] = pd.to_datetime(events["News_Date"])
    events["Market_T0"] = pd.to_datetime(events["Market_T0"])

    earliest_date = events["News_Date"].min()
    latest_date = events["Market_T0"].max()

    requested_start = earliest_date - pd.Timedelta(days=CALENDAR_BUFFER_DAYS)
    requested_end_inclusive = latest_date + pd.Timedelta(days=CALENDAR_BUFFER_DAYS)

    # yfinance treats `end` as exclusive. It also cannot download future data,
    # so cap the request at tomorrow.
    tomorrow = pd.Timestamp.now(tz="America/New_York").normalize().tz_localize(None) + pd.Timedelta(days=1)
    download_end_exclusive = min(
        requested_end_inclusive + pd.Timedelta(days=1),
        tomorrow,
    )

    print(f"Downloading data from {requested_start.date()} through "
          f"{(download_end_exclusive - pd.Timedelta(days=1)).date()}...")
    print()

    saved_files = []

    for ticker in TICKERS:
        try:
            data = yf.download(
                ticker,
                start=requested_start.strftime("%Y-%m-%d"),
                end=download_end_exclusive.strftime("%Y-%m-%d"),
                interval="1d",
                auto_adjust=False,
                actions=False,
                progress=False,
                repair=True,
                threads=False,
            )

            if data.empty:
                print(f"WARNING: No rows returned for {ticker}")
                continue

            # Recent yfinance versions may return MultiIndex columns even for
            # one ticker. Flatten them so the CSV is easy to read.
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = [
                    col[0] if isinstance(col, tuple) else str(col)
                    for col in data.columns
                ]

            data = data.reset_index()
            data["Ticker"] = ticker

            preferred_order = [
                "Date",
                "Ticker",
                "Open",
                "High",
                "Low",
                "Close",
                "Adj Close",
                "Volume",
            ]
            data = data[[c for c in preferred_order if c in data.columns]]

            output_file = OUTPUT_DIR / f"{safe_filename(ticker)}.csv"
            data.to_csv(output_file, index=False)
            saved_files.append(output_file)

            print(f"Saved {ticker:>5}: {len(data):>4} rows -> {output_file}")

        except Exception as exc:
            print(f"ERROR downloading {ticker}: {exc}", file=sys.stderr)

    events_to_save = events.copy()
    events_to_save["News_Date"] = events_to_save["News_Date"].dt.strftime("%Y-%m-%d")
    events_to_save["Market_T0"] = events_to_save["Market_T0"].dt.strftime("%Y-%m-%d")

    events_file = OUTPUT_DIR / "events.csv"
    events_to_save.to_csv(events_file, index=False)
    saved_files.append(events_file)
    print(f"Saved event table -> {events_file}")

    zip_path = shutil.make_archive(
        base_name=str(OUTPUT_DIR),
        format="zip",
        root_dir=OUTPUT_DIR,
    )

    print()
    print(f"Finished. Created {len(saved_files)} CSV files.")
    print(f"Upload this file back to Claude: {zip_path}")


if __name__ == "__main__":
    main()
