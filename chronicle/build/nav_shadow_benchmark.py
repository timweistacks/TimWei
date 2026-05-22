"""Unit-based NAV index and trade-mirrored shadow benchmarks (SPY, SSO 2x)."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime
from typing import Any

from chronicle.build.amortization import parse_iso_date
from chronicle.build.intraday_prices import IntradayPriceLookup
from chronicle.build.nav_history_lib import (
    _fx_event_dt,
    _series_close_on,
    _trade_cash_delta,
    _trade_event_dt,
    _trade_units_delta,
)

SHADOW_BENCHMARKS = (
    ("SPY", "spy_shadow_index", "SPY shadow (mirrors equity trades)"),
    ("SSO", "sso_shadow_index", "SSO 2x shadow (mirrors equity trades)"),
)


def _calendar_key(raw: str) -> str:
    return str(raw)[:10] if raw else ""


def _trade_notional_usd(trade: dict[str, Any]) -> float:
    side = str(trade.get("side", "")).strip().lower()
    if side == "buy":
        return abs(float(_trade_cash_delta(trade)))
    if side == "sell":
        return float(_trade_cash_delta(trade))
    return 0.0


def _apply_unit_flow(units: float, equity_before: float, flow_usd: float) -> float:
    if abs(flow_usd) < 1e-9:
        return units
    if units <= 1e-9:
        if flow_usd > 0:
            return flow_usd / 100.0
        return units
    nps = equity_before / units
    if abs(nps) < 1e-9:
        return units
    return units + flow_usd / nps


def _position_mv_usd(
    units_by_symbol: dict[str, float],
    series_map: dict,
    as_of: date,
    cash_equiv_symbols: frozenset[str],
) -> float:
    total = 0.0
    for symbol, units in units_by_symbol.items():
        if abs(units) <= 1e-9 or symbol in cash_equiv_symbols:
            continue
        close = _series_close_on(series_map, symbol, as_of)
        if close is None:
            continue
        total += units * close
    return total


def _shadow_equity_usd(
    book: dict[str, float],
    series_map: dict,
    bench_ticker: str,
    as_of: date,
) -> float | None:
    bench_px = _series_close_on(series_map, bench_ticker, as_of)
    if bench_px is None:
        return None
    return book["shares"] * bench_px


def _build_events(
    trades: list[dict[str, Any]],
    fx_events: list[dict[str, Any]],
) -> list[tuple[datetime, str, Any]]:
    events: list[tuple[datetime, str, Any]] = []
    for trade in trades:
        events.append((_trade_event_dt(trade), "trade", trade))
    for event in fx_events:
        events.append((_fx_event_dt(event), "fx", event))
    events.sort(key=lambda row: row[0])
    return events


def _shadow_fill_price(
    trade: dict[str, Any],
    ticker: str,
    series_map: dict,
    intraday: IntradayPriceLookup | None,
) -> float | None:
    if intraday is not None:
        quote = intraday.price_at_trade(trade, ticker)
        if quote is not None and quote.price_usd > 1e-9:
            return float(quote.price_usd)
    td = _trade_event_dt(trade).date()
    px = _series_close_on(series_map, ticker, td)
    if px is None or px <= 1e-9:
        return None
    return float(px)


def enrich_nav_unit_and_shadows(
    nav_rows: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    fx_events: list[dict[str, Any]],
    series_map: dict,
    cash_like_symbols: frozenset[str] | None,
    *,
    intraday_lookup: IntradayPriceLookup | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Unit NAV from equity sleeve MV only; cash/BOXX idle USD excluded.

    - FX: wallet cash only (no fund_units, no shadow shares).
    - Equity buy/sell: adjust fund_units; mirror notional in SPY/SSO shadow shares.
    - Shadow index: chained benchmark daily return while shadow holds shares (not
      shadow_equity/fund_units, which cliffs when cash redeploys into stocks).
    - BOXX (cash_equiv): wallet cash only (no units, no shadow).
    """
    cash_equiv = cash_like_symbols if cash_like_symbols is not None else frozenset()
    events = _build_events(trades, fx_events)
    if not nav_rows or not events:
        return nav_rows, {"nav_index_basis": "unit_fund", "shadow_ready": False}

    fund_units = 0.0
    cash_usd = 0.0
    units_by_symbol: dict[str, float] = {}
    shadow: dict[str, dict[str, float]] = {
        "SPY": {"shares": 0.0},
        "SSO": {"shares": 0.0},
    }
    day_snapshots: dict[str, dict[str, Any]] = {}

    for dt, kind, payload in events:
        day = dt.date().isoformat()
        as_of = dt.date()
        deployed_equity = _position_mv_usd(
            units_by_symbol, series_map, as_of, cash_equiv
        )

        if kind == "fx":
            cash_usd += float(payload.get("usd_amount", 0) or 0)
        else:
            trade = payload
            symbol = str(trade.get("symbol", ""))
            notional = _trade_notional_usd(trade)
            side = str(trade.get("side", "")).strip().lower()
            is_equity = symbol not in cash_equiv
            if (
                is_equity
                and notional > 1e-9
                and side in ("buy", "sell")
            ):
                signed = notional if side == "buy" else -notional
                fund_units = _apply_unit_flow(fund_units, deployed_equity, signed)
            cash_usd += _trade_cash_delta(trade)
            if is_equity:
                units_by_symbol[symbol] = units_by_symbol.get(symbol, 0.0) + _trade_units_delta(
                    trade
                )
            if is_equity and notional > 1e-9 and side in ("buy", "sell"):
                for spec in SHADOW_BENCHMARKS:
                    ticker = spec[0]
                    px = _shadow_fill_price(
                        trade, ticker, series_map, intraday_lookup
                    )
                    if px is None or px <= 1e-9:
                        continue
                    book = shadow[ticker]
                    shares_delta = notional / px
                    if side == "buy":
                        book["shares"] += shares_delta
                    elif side == "sell":
                        book["shares"] = max(
                            0.0, book["shares"] - min(book["shares"], shares_delta)
                        )

        day_snapshots[day] = {
            "fund_units": fund_units,
            "shadow": deepcopy(shadow),
        }

    shadow_idx: dict[str, float] = {t[0]: 100.0 for t in SHADOW_BENCHMARKS}
    prev_close: dict[str, float | None] = {t[0]: None for t in SHADOW_BENCHMARKS}
    shadow_started: dict[str, bool] = {t[0]: False for t in SHADOW_BENCHMARKS}

    out: list[dict[str, Any]] = []
    last_snap: dict[str, Any] | None = None
    for row in nav_rows:
        row_out = dict(row)
        day = _calendar_key(str(row.get("date", "")))
        snap = day_snapshots.get(day, last_snap)
        if snap is None:
            out.append(row_out)
            continue
        last_snap = snap
        units = float(snap["fund_units"])
        nav_mv = float(row.get("position_mv_usd") or row.get("mv_usd", 0) or 0)
        as_of = parse_iso_date(day) if day else date.today()
        if units > 1e-9:
            row_out["nav_index"] = round(nav_mv / units, 4)
            row_out["fund_units"] = round(units, 6)
        for ticker, field, _ in SHADOW_BENCHMARKS:
            book = snap["shadow"][ticker]
            shares = float(book["shares"])
            bench_equity = _shadow_equity_usd(book, series_map, ticker, as_of)
            close_px = _series_close_on(series_map, ticker, as_of)
            if bench_equity is not None:
                row_out[f"{field}_equity_usd"] = round(bench_equity, 4)
            if close_px is None:
                continue
            if shares > 1e-9:
                if not shadow_started[ticker]:
                    shadow_idx[ticker] = 100.0
                    shadow_started[ticker] = True
                elif prev_close[ticker] is not None and prev_close[ticker] > 1e-9:
                    shadow_idx[ticker] *= close_px / prev_close[ticker]
                row_out[field] = round(shadow_idx[ticker], 4)
                prev_close[ticker] = close_px
        out.append(row_out)

    return out, {
        "nav_index_basis": "unit_fund_deployed_on_trade",
        "shadow_ready": True,
        "shadow_tickers": [s[0] for s in SHADOW_BENCHMARKS],
        "shadow_index_basis": "chained_benchmark_return_with_mirrored_shares",
        "shadow_fill_price_basis": (
            "intraday_bar_at_executed_at"
            if intraday_lookup is not None
            else "daily_close_on_trade_date"
        ),
        "shadow_fill_timestamp_tz": "Asia/Taipei",
        "shadow_fill_market_tz": "America/New_York",
    }
