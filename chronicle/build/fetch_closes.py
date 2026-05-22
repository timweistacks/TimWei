#!/usr/bin/env python3
"""Download daily closes from Yahoo Finance into chronicle/data/prices/*.csv."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from chronicle.build.paths import DATA_DIR, PRICES_DIR  # noqa: E402


def _load_portfolio() -> dict:
    path = DATA_DIR / "portfolio.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _tickers_from_portfolio(data: dict) -> list[str]:
    out: list[str] = []
    for p in data.get("positions", []):
        if p.get("listed") is False:
            continue
        t = p.get("yahoo_ticker")
        if t and t not in out:
            out.append(t)
    val = data.get("valuation", {})
    pol = val.get("usd_twd_policy")
    fx_t = val.get("yahoo_usdtwd_ticker")
    if pol == "yahoo" and fx_t and fx_t not in out:
        out.append(fx_t)
    return out


def _safe_filename(ticker: str) -> str:
    return ticker.replace("^", "").replace("=", "_").replace("/", "_")


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch daily closes to CSV cache.")
    parser.add_argument(
        "--end",
        type=str,
        default=None,
        help="ISO end date (default: today)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Calendar days of history to request ending at --end",
    )
    args = parser.parse_args()

    import yfinance as yf

    if args.end:
        end_d = datetime.strptime(args.end, "%Y-%m-%d").date()
    else:
        end_d = date.today()
    start_d = end_d - timedelta(days=args.days)

    data = _load_portfolio()
    tickers = _tickers_from_portfolio(data)
    if not tickers:
        raise SystemExit("no tickers in portfolio.json")

    PRICES_DIR.mkdir(parents=True, exist_ok=True)

    for ticker in tickers:
        t = yf.Ticker(ticker)
        hist = t.history(
            start=start_d.isoformat(),
            end=(end_d + timedelta(days=1)).isoformat(),
            auto_adjust=False,
        )
        if hist is None or hist.empty:
            print(f"warn: no rows for {ticker}", file=sys.stderr)
            continue
        out_path = PRICES_DIR / f"{_safe_filename(ticker)}_daily.csv"
        with out_path.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "close"])
            for idx, row in hist.iterrows():
                d = idx.date().isoformat()
                w.writerow([d, f"{float(row['Close']):.6f}"])
        print(f"wrote {out_path} rows={len(hist)}")


if __name__ == "__main__":
    main()
