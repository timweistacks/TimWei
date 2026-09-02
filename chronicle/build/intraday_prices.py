"""Yahoo intraday bars for shadow benchmark fills at trade executed_at."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

_YFINANCE_LOG = logging.getLogger("yfinance")
_YFINANCE_LOG.setLevel(logging.ERROR)

from chronicle.build.nav_history_lib import (
    _series_close_on,
    _trade_date,
    _trade_event_dt,
)
from chronicle.build.paths import PRICES_DIR

TRADE_TIMESTAMP_TZ = ZoneInfo("Asia/Taipei")
MARKET_TZ = ZoneInfo("America/New_York")
INTRADAY_CACHE_DIR = PRICES_DIR / "intraday"
INTRADAY_INTERVALS = ("1m", "5m")
YAHOO_1M_MAX_AGE_DAYS = 29


def _parse_trade_dt(executed_at: str) -> datetime | None:
    raw = str(executed_at or "").strip()
    if not raw:
        return None
    raw = raw.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            return dt.replace(tzinfo=TRADE_TIMESTAMP_TZ)
        return dt
    except ValueError:
        return None
    return None


def _to_market_dt(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TRADE_TIMESTAMP_TZ)
    return dt.astimezone(MARKET_TZ)


def _market_session_date(dt_market: datetime) -> date:
    return dt_market.date()


def _cache_path(ticker: str, session_day: date, interval: str) -> Path:
    safe = ticker.replace("/", "_")
    return INTRADAY_CACHE_DIR / safe / interval / f"{session_day.isoformat()}.json"


def _miss_path(ticker: str, session_day: date, interval: str) -> Path:
    return _cache_path(ticker, session_day, interval).with_suffix(".miss.json")


def _yahoo_1m_eligible(session_day: date, as_of: date) -> bool:
    return (as_of - session_day).days <= YAHOO_1M_MAX_AGE_DAYS


def _intervals_to_try(session_day: date, as_of: date) -> tuple[str, ...]:
    if _yahoo_1m_eligible(session_day, as_of):
        return INTRADAY_INTERVALS
    return ("5m",)


def _load_miss_marker(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if payload.get("status") == "unavailable":
        return payload
    return None


def _write_miss_marker(
    path: Path,
    *,
    ticker: str,
    session_day: date,
    interval: str,
    reason: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ticker": ticker,
        "date": session_day.isoformat(),
        "interval": interval,
        "status": "unavailable",
        "reason": reason,
        "checked_at": datetime.now(tz=TRADE_TIMESTAMP_TZ).isoformat(timespec="seconds"),
    }
    tmp = path.with_suffix(".miss.json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _load_cached_bars(path: Path) -> list[tuple[datetime, float]] | None:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    out: list[tuple[datetime, float]] = []
    for row in payload.get("bars", []):
        ts_raw = row.get("ts")
        close = row.get("close")
        if not ts_raw or close is None:
            continue
        ts = datetime.fromisoformat(str(ts_raw))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=MARKET_TZ)
        out.append((ts, float(close)))
    out.sort(key=lambda item: item[0])
    return out or None


def _write_cached_bars(
    path: Path,
    *,
    ticker: str,
    session_day: date,
    interval: str,
    bars: list[tuple[datetime, float]],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ticker": ticker,
        "date": session_day.isoformat(),
        "interval": interval,
        "market_tz": str(MARKET_TZ),
        "trade_timestamp_tz": str(TRADE_TIMESTAMP_TZ),
        "bars": [
            {"ts": ts.isoformat(), "close": round(close, 6)}
            for ts, close in bars
        ],
    }
    tmp = path.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def _fetch_intraday_day(
    ticker: str, session_day: date, interval: str
) -> list[tuple[datetime, float]] | None:
    import warnings

    import yfinance as yf

    start = session_day.isoformat()
    end = (session_day + timedelta(days=1)).isoformat()
    hist = None
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=FutureWarning)
        hist = yf.Ticker(ticker).history(
            start=start,
            end=end,
            interval=interval,
            auto_adjust=True,
        )
    if hist is None or hist.empty or "Close" not in hist.columns:
        return None
    out: list[tuple[datetime, float]] = []
    for ts, row in hist.iterrows():
        dt = pd.Timestamp(ts).to_pydatetime()
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=MARKET_TZ)
        else:
            dt = dt.astimezone(MARKET_TZ)
        if dt.date() != session_day:
            continue
        out.append((dt, float(row["Close"])))
    out.sort(key=lambda item: item[0])
    return out or None


def _bars_for_session(
    ticker: str, session_day: date, as_of: date, *, use_cache: bool = True
) -> tuple[list[tuple[datetime, float]] | None, str | None]:
    intervals = _intervals_to_try(session_day, as_of)
    cached_hits: dict[str, list[tuple[datetime, float]]] = {}

    if use_cache:
        for interval in intervals:
            bar_path = _cache_path(ticker, session_day, interval)
            if _load_miss_marker(_miss_path(ticker, session_day, interval)):
                continue
            cached = _load_cached_bars(bar_path)
            if cached:
                cached_hits[interval] = cached
        for interval in INTRADAY_INTERVALS:
            if interval in cached_hits:
                return cached_hits[interval], interval

    for interval in intervals:
        bar_path = _cache_path(ticker, session_day, interval)
        miss_path = _miss_path(ticker, session_day, interval)
        if use_cache and _load_miss_marker(miss_path):
            continue
        if interval == "1m" and not _yahoo_1m_eligible(session_day, as_of):
            _write_miss_marker(
                miss_path,
                ticker=ticker,
                session_day=session_day,
                interval=interval,
                reason="outside_yahoo_1m_window",
            )
            continue
        bars = _fetch_intraday_day(ticker, session_day, interval)
        if bars:
            _write_cached_bars(
                bar_path,
                ticker=ticker,
                session_day=session_day,
                interval=interval,
                bars=bars,
            )
            return bars, interval
        _write_miss_marker(
            miss_path,
            ticker=ticker,
            session_day=session_day,
            interval=interval,
            reason="yahoo_no_data",
        )
    return None, None


def _backfill_miss_markers_for_cached_5m(tickers: tuple[str, ...]) -> None:
    """If 5m bars are cached but 1m is not, record 1m miss so Yahoo is not retried."""
    for ticker in tickers:
        safe = ticker.replace("/", "_")
        five_dir = INTRADAY_CACHE_DIR / safe / "5m"
        if not five_dir.is_dir():
            continue
        for bar_file in five_dir.glob("*.json"):
            if bar_file.suffix != ".json" or ".miss" in bar_file.name:
                continue
            try:
                session_day = date.fromisoformat(bar_file.stem)
            except ValueError:
                continue
            one_path = _cache_path(ticker, session_day, "1m")
            miss_path = _miss_path(ticker, session_day, "1m")
            if one_path.is_file() or miss_path.is_file():
                continue
            _write_miss_marker(
                miss_path,
                ticker=ticker,
                session_day=session_day,
                interval="1m",
                reason="use_5m_cache",
            )


def _nearest_bar_close(
    bars: list[tuple[datetime, float]], target: datetime
) -> tuple[float, datetime] | None:
    if not bars:
        return None
    if target.tzinfo is None:
        target = target.replace(tzinfo=MARKET_TZ)
    else:
        target = target.astimezone(MARKET_TZ)
    chosen: tuple[float, datetime] | None = None
    for ts, close in bars:
        if ts <= target:
            chosen = (close, ts)
        else:
            break
    if chosen is not None:
        return chosen
    return bars[0][1], bars[0][0]


@dataclass(frozen=True)
class ShadowFillQuote:
    price_usd: float
    source: str
    bar_at: str | None
    interval: str | None


class IntradayPriceLookup:
    """Resolve SPY/SSO price at each trade's executed_at (Asia/Taipei naive -> US market bars)."""

    def __init__(
        self,
        series_map: dict[str, pd.Series],
        *,
        as_of: date,
        session_bars: dict[tuple[str, date], list[tuple[datetime, float]]],
        session_interval: dict[tuple[str, date], str],
    ) -> None:
        self._series_map = series_map
        self._as_of = as_of
        self._session_bars = session_bars
        self._session_interval = session_interval

    def price_at_trade(self, trade: dict[str, Any], ticker: str) -> ShadowFillQuote | None:
        executed_at = str(trade.get("executed_at", "") or "").strip()
        trade_dt = _parse_trade_dt(executed_at) if executed_at else None
        if trade_dt is None:
            td = _trade_date(trade)
            if td is None:
                return None
            px = _series_close_on(self._series_map, ticker, td)
            if px is None or px <= 1e-9:
                return None
            return ShadowFillQuote(
                price_usd=float(px),
                source="daily_close",
                bar_at=None,
                interval=None,
            )
        market_dt = _to_market_dt(trade_dt)
        session_day = _market_session_date(market_dt)
        key = (ticker, session_day)
        bars = self._session_bars.get(key)
        interval = self._session_interval.get(key)
        if bars:
            hit = _nearest_bar_close(bars, market_dt)
            if hit is not None:
                px, bar_ts = hit
                if px > 1e-9:
                    return ShadowFillQuote(
                        price_usd=float(px),
                        source=f"intraday_{interval or '5m'}",
                        bar_at=bar_ts.isoformat(),
                        interval=interval,
                    )
        # The fallback must use the same New York session date as the
        # intraday lookup.  A Taiwan early-morning execution can otherwise
        # incorrectly fall through to the following calendar day's close.
        td = session_day
        px = _series_close_on(self._series_map, ticker, td)
        if px is None or px <= 1e-9:
            return None
        return ShadowFillQuote(
            price_usd=float(px),
            source="daily_close_fallback",
            bar_at=None,
            interval=None,
        )


def build_intraday_lookup(
    trades: list[dict[str, Any]],
    series_map: dict[str, pd.Series],
    tickers: tuple[str, ...],
    *,
    as_of: date,
    cash_like_symbols: frozenset[str] | None = None,
) -> IntradayPriceLookup:
    cash_equiv = cash_like_symbols if cash_like_symbols is not None else frozenset()
    sessions: set[tuple[str, date]] = set()
    for trade in trades:
        sym = str(trade.get("symbol", "") or "")
        if sym in cash_equiv:
            continue
        side = str(trade.get("side", "")).strip().lower()
        if side not in ("buy", "sell"):
            continue
        executed_at = str(trade.get("executed_at", "") or "").strip()
        trade_dt = _parse_trade_dt(executed_at) if executed_at else None
        if trade_dt is None:
            td = _trade_date(trade)
            if td is None:
                continue
            session_day = td
        else:
            session_day = _market_session_date(_to_market_dt(trade_dt))
        for ticker in tickers:
            sessions.add((ticker, session_day))

    _backfill_miss_markers_for_cached_5m(tickers)

    session_bars: dict[tuple[str, date], list[tuple[datetime, float]]] = {}
    session_interval: dict[tuple[str, date], str] = {}
    for ticker, session_day in sorted(sessions):
        bars, interval = _bars_for_session(ticker, session_day, as_of)
        if bars and interval:
            session_bars[(ticker, session_day)] = bars
            session_interval[(ticker, session_day)] = interval

    return IntradayPriceLookup(
        series_map,
        as_of=as_of,
        session_bars=session_bars,
        session_interval=session_interval,
    )


def enrich_trades_shadow_fills(
    trades: list[dict[str, Any]],
    lookup: IntradayPriceLookup,
    tickers: tuple[str, ...] = ("SPY", "SSO"),
    *,
    cash_like_symbols: frozenset[str] | None = None,
) -> list[dict[str, Any]]:
    cash_equiv = cash_like_symbols if cash_like_symbols is not None else frozenset()
    out: list[dict[str, Any]] = []
    for row in trades:
        merged = dict(row)
        sym = str(row.get("symbol", "") or "")
        side = str(row.get("side", "")).strip().lower()
        if sym in cash_equiv or side not in ("buy", "sell"):
            out.append(merged)
            continue
        fills: dict[str, Any] = {}
        for ticker in tickers:
            quote = lookup.price_at_trade(row, ticker)
            if quote is None:
                continue
            fills[ticker] = {
                "price_usd": round(quote.price_usd, 4),
                "source": quote.source,
                "bar_at": quote.bar_at,
                "interval": quote.interval,
            }
        if fills:
            merged["shadow_benchmark_fills"] = fills
        out.append(merged)
    return out
