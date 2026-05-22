"""Yahoo Finance helpers for personal ledger (daily close)."""

from __future__ import annotations

from datetime import date, timedelta


def fetch_close_on_or_before(ticker: str, as_of: date) -> float:
    import yfinance as yf

    start = as_of - timedelta(days=14)
    end = as_of + timedelta(days=1)
    t = yf.Ticker(ticker)
    hist = t.history(start=start.isoformat(), end=end.isoformat(), auto_adjust=False)
    if hist is None or hist.empty:
        raise RuntimeError(f"no price history for {ticker!r} around {as_of.isoformat()}")
    for i in range(len(hist) - 1, -1, -1):
        ts = hist.index[i]
        d = ts.date() if hasattr(ts, "date") else ts
        if d <= as_of:
            return float(hist["Close"].iloc[i])
    raise RuntimeError(f"no rows on or before as_of for {ticker!r}")
