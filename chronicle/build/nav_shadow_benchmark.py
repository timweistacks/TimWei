"""Unit-based NAV and event-replayed SPY/SSO shadow benchmarks."""

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
    _trade_market_date,
    _trade_units_delta,
)

SHADOW_BENCHMARKS = (
    ("SPY", "spy_shadow_index", "SPY shadow (mirrors equity trades)"),
    ("SSO", "sso_shadow_index", "SSO 2x shadow (mirrors equity trades)"),
)


def _event_snapshot_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


def _row_snapshot_key(raw_date: str) -> str | None:
    raw = str(raw_date or "").strip()
    if "T" not in raw:
        return None
    key = raw.replace("Z", "").split("+")[0]
    if key.count(":") == 1:
        key = f"{key}:00"
    return key[:19] if len(key) >= 19 else None


def _first_equity_trade_key(
    trades: list[dict[str, Any]], cash_equiv: frozenset[str]
) -> str | None:
    candidates: list[datetime] = []
    for trade in trades:
        symbol = str(trade.get("symbol", ""))
        if symbol in cash_equiv:
            continue
        if str(trade.get("side", "")).strip().lower() != "buy":
            continue
        candidates.append(_trade_event_dt(trade))
    if not candidates:
        return None
    return _event_snapshot_key(min(candidates))


def _resolve_row_snapshot(
    raw_date: str,
    day: str,
    event_snapshots: dict[str, dict[str, Any]],
    day_snapshots: dict[str, dict[str, Any]],
    last_snap: dict[str, Any] | None,
) -> dict[str, Any] | None:
    row_key = _row_snapshot_key(raw_date)
    if row_key is not None:
        snap = event_snapshots.get(row_key)
        if snap is not None:
            return snap
    snap = day_snapshots.get(day)
    if snap is not None:
        return snap
    return last_snap


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
    td = _trade_market_date(trade) or _trade_event_dt(trade).date()
    px = _series_close_on(series_map, ticker, td)
    if px is None or px <= 1e-9:
        return None
    return float(px)


def _new_shadow_book() -> dict[str, float | bool | None]:
    return {
        "shares": 0.0,
        "fund_units": 0.0,
        "index": 100.0,
        "last_price": None,
        "started": False,
    }


def _advance_shadow_book(
    book: dict[str, float | bool | None], price: float
) -> None:
    """Advance a shadow fund to a benchmark price before the next event."""
    if bool(book["started"]):
        last_price = book["last_price"]
        shares = float(book["shares"] or 0.0)
        if last_price is not None and shares > 1e-9:
            book["index"] = float(book["index"]) * price / float(last_price)
    book["last_price"] = price


def _apply_shadow_trade(
    book: dict[str, float | bool | None], trade: dict[str, Any], price: float
) -> None:
    """Apply one mirrored trade at its transaction-time benchmark price."""
    side = str(trade.get("side", "")).strip().lower()
    notional = _trade_notional_usd(trade)
    if side not in ("buy", "sell") or notional <= 1e-9 or price <= 1e-9:
        return

    if not bool(book["started"]):
        if side != "buy":
            return
        book["started"] = True
        book["index"] = 100.0
        book["last_price"] = price
    else:
        _advance_shadow_book(book, price)

    index = float(book["index"])
    if index <= 1e-9:
        return
    if side == "buy":
        book["shares"] = float(book["shares"]) + notional / price
        book["fund_units"] = float(book["fund_units"]) + notional / index
        return

    shares_to_sell = min(float(book["shares"]), notional / price)
    book["shares"] = max(0.0, float(book["shares"]) - shares_to_sell)
    book["fund_units"] = max(
        0.0,
        float(book["fund_units"]) - (shares_to_sell * price / index),
    )


def _replay_shadow_benchmark_snapshots(
    nav_rows: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    series_map: dict,
    cash_equiv: frozenset[str],
    intraday_lookup: IntradayPriceLookup | None,
) -> tuple[
    dict[str, dict[str, dict[str, float | bool | None]]],
    dict[str, dict[str, dict[str, float | bool | None]]],
]:
    """Replay benchmark books at trade bars and then at each market close."""
    trades_by_day: dict[str, list[tuple[datetime, dict[str, Any]]]] = {}
    days: set[str] = set()

    for row in nav_rows:
        day = _calendar_key(str(row.get("date", "")))
        if day:
            days.add(day)

    for trade in trades:
        symbol = str(trade.get("symbol", "") or "")
        side = str(trade.get("side", "")).strip().lower()
        if symbol in cash_equiv or side not in ("buy", "sell"):
            continue
        market_day = _trade_market_date(trade)
        if market_day is None:
            continue
        day = market_day.isoformat()
        days.add(day)
        trades_by_day.setdefault(day, []).append((_trade_event_dt(trade), trade))

    books: dict[str, dict[str, float | bool | None]] = {
        ticker: _new_shadow_book() for ticker, _, _ in SHADOW_BENCHMARKS
    }
    event_snapshots: dict[
        str, dict[str, dict[str, float | bool | None]]
    ] = {}
    day_snapshots: dict[
        str, dict[str, dict[str, float | bool | None]]
    ] = {}

    for day in sorted(days):
        day_trades = sorted(
            trades_by_day.get(day, []),
            key=lambda item: item[0],
        )
        for event_dt, trade in day_trades:
            for ticker, _, _ in SHADOW_BENCHMARKS:
                price = _shadow_fill_price(
                    trade, ticker, series_map, intraday_lookup
                )
                if price is not None:
                    _apply_shadow_trade(books[ticker], trade, price)
            event_snapshots[_event_snapshot_key(event_dt)] = (
                deepcopy(books)
            )

        market_day = parse_iso_date(day)
        for ticker, _, _ in SHADOW_BENCHMARKS:
            close = _series_close_on(series_map, ticker, market_day)
            if close is not None:
                _advance_shadow_book(books[ticker], close)
        day_snapshots[day] = deepcopy(books)

    return event_snapshots, day_snapshots


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
    - Shadow index: event-replayed, unitized benchmark NAV. Each equity buy/sell
      is applied at its SPY/SSO minute fill when available; daily closes advance
      only the shares that remain after the event.
    - BOXX (cash_equiv): wallet cash only (no units, no shadow).
    """
    cash_equiv = cash_like_symbols if cash_like_symbols is not None else frozenset()
    events = _build_events(trades, fx_events)
    if not nav_rows or not events:
        return nav_rows, {"nav_index_basis": "unit_fund", "shadow_ready": False}

    fund_units = 0.0
    units_by_symbol: dict[str, float] = {}
    fund_day_snapshots: dict[str, dict[str, Any]] = {}
    fund_event_snapshots: dict[str, dict[str, Any]] = {}
    first_equity_trade_key = _first_equity_trade_key(trades, cash_equiv)

    for dt, kind, payload in events:
        if kind != "trade":
            continue
        as_of = _trade_market_date(payload) or dt.date()
        day = as_of.isoformat()
        deployed_equity = _position_mv_usd(
            units_by_symbol, series_map, as_of, cash_equiv
        )

        trade = payload
        symbol = str(trade.get("symbol", ""))
        notional = _trade_notional_usd(trade)
        side = str(trade.get("side", "")).strip().lower()
        is_equity = symbol not in cash_equiv
        if is_equity and notional > 1e-9 and side in ("buy", "sell"):
            signed = notional if side == "buy" else -notional
            fund_units = _apply_unit_flow(fund_units, deployed_equity, signed)
        if is_equity:
            units_by_symbol[symbol] = units_by_symbol.get(symbol, 0.0) + _trade_units_delta(
                trade
            )

        snap = {
            "fund_units": fund_units,
        }
        fund_event_snapshots[_event_snapshot_key(dt)] = snap
        fund_day_snapshots[day] = snap

    shadow_event_snapshots, shadow_day_snapshots = (
        _replay_shadow_benchmark_snapshots(
            nav_rows,
            trades,
            series_map,
            cash_equiv,
            intraday_lookup,
        )
    )

    out: list[dict[str, Any]] = []
    last_fund_snap: dict[str, Any] | None = None
    last_shadow_snap: dict[str, Any] | None = None
    for row in nav_rows:
        row_out = dict(row)
        raw_date = str(row.get("date", ""))
        day = _calendar_key(raw_date)
        fund_snap = _resolve_row_snapshot(
            raw_date, day, fund_event_snapshots, fund_day_snapshots, last_fund_snap
        )
        shadow_snap = _resolve_row_snapshot(
            raw_date, day, shadow_event_snapshots, shadow_day_snapshots, last_shadow_snap
        )
        if fund_snap is not None:
            last_fund_snap = fund_snap
            units = float(fund_snap["fund_units"])
            nav_mv = float(row.get("position_mv_usd") or row.get("mv_usd", 0) or 0)
            row_key = _row_snapshot_key(raw_date)
            if units > 1e-9:
                if first_equity_trade_key and row_key == first_equity_trade_key:
                    row_out["nav_index"] = 100.0
                else:
                    row_out["nav_index"] = round(nav_mv / units, 4)
                row_out["fund_units"] = round(units, 6)
        if shadow_snap is not None:
            last_shadow_snap = shadow_snap
        for ticker, field, _ in SHADOW_BENCHMARKS:
            if shadow_snap is None:
                continue
            book = shadow_snap[ticker]
            if not bool(book["started"]):
                continue
            shares = float(book["shares"])
            mark_price = book["last_price"]
            if mark_price is not None:
                row_out[f"{field}_equity_usd"] = round(
                    shares * float(mark_price), 4
                )
            row_out[field] = round(float(book["index"]), 4)
        out.append(row_out)

    return out, {
        "nav_index_basis": "unit_fund_deployed_on_trade",
        "nav_anchor_first_trade": first_equity_trade_key,
        "shadow_ready": True,
        "shadow_tickers": [s[0] for s in SHADOW_BENCHMARKS],
        "shadow_index_basis": "event_replayed_benchmark_return_with_mirrored_shares",
        "shadow_fill_price_basis": (
            "intraday_bar_at_executed_at"
            if intraday_lookup is not None
            else "daily_close_on_trade_date"
        ),
        "shadow_fill_timestamp_tz": "Asia/Taipei",
        "shadow_fill_market_tz": "America/New_York",
    }
