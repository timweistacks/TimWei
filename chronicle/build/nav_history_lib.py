"""Backfill daily NAV snapshots and persist price history."""

from __future__ import annotations

from collections import defaultdict
import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from chronicle.build.amortization import parse_iso_date


TRADE_TIMESTAMP_TZ = ZoneInfo("Asia/Taipei")
MARKET_TZ = ZoneInfo("America/New_York")


def _calendar_date_from_row(raw_date: str) -> date:
    """Accept YYYY-MM-DD or ISO datetime strings."""
    return parse_iso_date(str(raw_date)[:10])


def _cum_invested_usd(flows: list[dict], as_of: date) -> float:
    t = 0.0
    for f in flows:
        fd = parse_iso_date(f["date"]) if isinstance(f["date"], str) else f["date"]
        if fd <= as_of:
            t += float(f.get("usd", 0)) + float(f.get("fees_usd", 0))
    return t


def _cost_basis_fallback_usd(positions: list[dict]) -> float:
    return sum(float(p.get("cost_basis_usd", 0)) for p in positions)


def _existing_rows(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if path.is_file():
        with path.open(encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, list):
            rows = []
            for r in raw:
                if not isinstance(r, dict) or not r.get("date"):
                    continue
                sc = r.get("spy_close")
                rows.append(
                    {
                        "date": str(r["date"]),
                        "mv_usd": float(r["mv_usd"]),
                        "spy_close": float(sc) if sc is not None else None,
                    }
                )
    return rows


def _trade_date(trade: dict[str, Any]) -> date | None:
    executed_at = trade.get("executed_at")
    if isinstance(executed_at, str) and executed_at:
        return parse_iso_date(executed_at[:10])
    raw_date = trade.get("date")
    if isinstance(raw_date, str) and raw_date:
        return parse_iso_date(raw_date[:10])
    return None


def _parse_trade_datetime(raw_value: Any) -> datetime | None:
    """Parse an executed_at value, treating naive timestamps as Asia/Taipei."""
    raw = str(raw_value or "").strip()
    if not raw:
        return None
    raw = raw.replace("Z", "+00:00")
    try:
        if len(raw) >= 19:
            dt = datetime.fromisoformat(raw)
            if dt.tzinfo is None:
                return dt.replace(tzinfo=TRADE_TIMESTAMP_TZ)
            return dt
        if len(raw) >= 10:
            return datetime.fromisoformat(
                raw[:10] + "T12:00:00"
            ).replace(tzinfo=TRADE_TIMESTAMP_TZ)
    except ValueError:
        return None
    return None


def _trade_market_datetime(trade: dict[str, Any]) -> datetime | None:
    """Return executed_at in America/New_York for market-session bookkeeping."""
    dt = _parse_trade_datetime(trade.get("executed_at"))
    if dt is None:
        raw_date = trade.get("date")
        if not isinstance(raw_date, str) or not raw_date:
            return None
        try:
            dt = datetime.fromisoformat(raw_date[:10] + "T12:00:00").replace(
                tzinfo=MARKET_TZ
            )
        except ValueError:
            return None
    return dt.astimezone(MARKET_TZ)


def _trade_market_date(trade: dict[str, Any]) -> date | None:
    """Return the New York trading-session date for a trade."""
    market_dt = _trade_market_datetime(trade)
    return market_dt.date() if market_dt is not None else None


def _trade_units_delta(trade: dict[str, Any]) -> float:
    side = str(trade.get("side", "")).strip().lower()
    units = float(trade.get("units", 0) or 0)
    if side == "buy":
        return units
    if side == "sell":
        return -units
    return 0.0


def _trade_cash_delta(trade: dict[str, Any]) -> float:
    """Cash change from one trade (buy = outflow, sell = net proceeds in).

    Buys: debit = total_usd + fee_usd + other_fees_usd (principal rows often omit fee).
    Sells: credit = total_usd - fee_usd - other_fees_usd (gross proceeds convention).
    """
    side = str(trade.get("side", "")).strip().lower()
    units = float(trade.get("units", 0) or 0)
    if units <= 0:
        return 0.0
    if side == "buy":
        principal = float(trade.get("total_usd", 0) or 0)
        fee = float(trade.get("fee_usd", 0) or 0)
        other = float(trade.get("other_fees_usd", 0) or 0)
        return -(principal + fee + other)
    if side == "sell":
        gross = float(trade.get("total_usd", 0) or 0)
        fee = float(trade.get("fee_usd", 0) or 0)
        other = float(trade.get("other_fees_usd", 0) or 0)
        return gross - fee - other
    return 0.0


def _net_cashflow_from_trades_through(trades: list[dict], end: date) -> float:
    total = 0.0
    for t in trades:
        td = _trade_market_date(t)
        if td is None or td > end:
            continue
        total += _trade_cash_delta(t)
    return total


def _net_fx_usd_through(fx_events: list[dict], end: date) -> float:
    total = 0.0
    for e in fx_events:
        raw = e.get("date")
        if not isinstance(raw, str) or not raw:
            continue
        ed = parse_iso_date(raw)
        if ed <= end:
            total += float(e.get("usd_amount", 0) or 0)
    return total


def _funding_usd_through(
    opening_cash_usd: float, fx_events: list[dict[str, Any]], as_of: date
) -> float:
    """Cumulative USD from outside (opening wallet + FX inflows through as_of). Not trades."""
    return float(opening_cash_usd) + _net_fx_usd_through(fx_events, as_of)


def _fx_event_dt(e: dict[str, Any]) -> datetime:
    d = str(e.get("date", ""))[:10]
    tl = e.get("time_local")
    if tl:
        ts = str(tl)
        if ts.count(":") == 1:
            ts = f"{ts}:00"
        return datetime.fromisoformat(f"{d}T{ts}")
    return datetime.fromisoformat(f"{d}T00:00:00")


def _trade_event_dt(trade: dict[str, Any]) -> datetime:
    raw = str(trade.get("executed_at", "")).strip()
    parsed = _parse_trade_datetime(raw)
    if parsed is not None:
        # Keep the event timeline in the canonical Taiwan-local wall clock so
        # existing intraday NAV row keys continue to match executed_at.
        return parsed.astimezone(TRADE_TIMESTAMP_TZ).replace(tzinfo=None)
    if not raw:
        td = _trade_date(trade)
        if td is None:
            return datetime.combine(date.min, datetime.min.time())
        return datetime.combine(td, datetime.min.time())
    td = _trade_date(trade)
    if td is not None:
        return datetime.combine(td, datetime.min.time())
    return datetime.combine(date.min, datetime.min.time())


def _cash_eod_market_days(
    market_dates: list[date],
    trades_by_date: dict[date, list[dict[str, Any]]],
    fx_events: list[dict[str, Any]],
    opening_cash_usd: float,
    start: date,
    end: date,
) -> dict[date, float]:
    """EOD USD cash on each market date: opening + FX and trades in time order per calendar day."""
    market_set = set(market_dates)
    fx_by_day: dict[date, list[tuple[datetime, float]]] = defaultdict(list)
    for e in fx_events:
        raw = e.get("date")
        if not isinstance(raw, str) or not raw:
            continue
        d = parse_iso_date(raw)
        if d < start or d > end:
            continue
        fx_by_day[d].append((_fx_event_dt(e), float(e.get("usd_amount", 0) or 0)))

    out: dict[date, float] = {}
    running = float(opening_cash_usd)
    d = start
    while d <= end:
        deltas: list[tuple[datetime, float]] = []
        for dt, amt in fx_by_day.get(d, []):
            deltas.append((dt, amt))
        for tr in trades_by_date.get(d, []):
            deltas.append((_trade_event_dt(tr), _trade_cash_delta(tr)))
        deltas.sort(key=lambda x: x[0])
        for _, dx in deltas:
            running += dx
        if d in market_set:
            out[d] = running
        d += timedelta(days=1)
    return out


def _series_close_on(
    series_map: dict[str, pd.Series], ticker: str | None, as_of: date
) -> float | None:
    if not ticker:
        return None
    series = series_map.get(ticker)
    if series is None or series.empty:
        return None
    ts = pd.Timestamp(as_of)
    prior = series.loc[:ts]
    if prior.empty:
        return None
    # A daily series can legitimately miss a market date for one ticker while
    # the rest of the portfolio has a quote. Carry the last available close
    # forward instead of treating that holding as having zero market value.
    return float(prior.iloc[-1])


def _series_open_on(
    series_map: dict[str, pd.Series], benchmark_ticker: str, as_of: date
) -> float | None:
    """Daily open for the benchmark (series_map key: e.g. SPY_OPEN)."""
    key = f"{benchmark_ticker}_OPEN"
    series = series_map.get(key)
    if series is None or series.empty:
        return None
    ts = pd.Timestamp(as_of)
    if ts not in series.index:
        return None
    return float(series.loc[ts])


def _earliest_trade_row(trades: list[dict[str, Any]]) -> dict[str, Any] | None:
    dated = [
        t
        for t in trades
        if isinstance(t.get("executed_at"), str) and str(t.get("executed_at")).strip()
    ]
    if not dated:
        return None
    return min(dated, key=lambda t: str(t.get("executed_at", "")))


def _inject_first_trade_row(
    rows: list[dict[str, Any]],
    trades: list[dict[str, Any]],
    spy_anchor_close: float | None,
) -> list[dict[str, Any]]:
    """Insert a base-100 row at first fill time before the first EOD row on that calendar day."""
    first = _earliest_trade_row(trades)
    if first is None or spy_anchor_close is None or spy_anchor_close <= 0:
        return rows
    fd = _trade_market_date(first)
    if fd is None:
        return rows
    day_key = fd.isoformat()
    insert_at = -1
    for i, r in enumerate(rows):
        ds = str(r.get("date", ""))[:10]
        if ds == day_key:
            insert_at = i
            break
    if insert_at < 0:
        return rows
    cost = float(first.get("total_usd", 0) or 0)
    first_at = str(first.get("executed_at", ""))
    entry: dict[str, Any] = {
        "date": first_at,
        "mv_usd": round(cost, 4),
        "position_mv_usd": round(cost, 4),
        "nav_index": 100.0,
        "spy_close": round(float(spy_anchor_close), 6),
        "spy_index": 100.0,
        "cumulative_invested_usd": round(cost, 2),
    }
    return rows[:insert_at] + [entry] + rows[insert_at:]


def _sort_nav_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Order intraday ISO rows before plain YYYY-MM-DD on the same calendar day."""

    def _key(r: dict[str, Any]) -> tuple:
        raw = str(r.get("date", ""))
        day = raw[:10] if len(raw) >= 10 else raw
        if "T" in raw:
            return (day, 0, raw)
        return (day, 1, raw)

    return sorted(rows, key=_key)


def _history_dates(
    series_map: dict[str, pd.Series], tickers: list[str], start: date, end: date
) -> list[date]:
    dates: set[date] = set()
    for ticker in tickers:
        series = series_map.get(ticker)
        if series is None or series.empty:
            continue
        for ts in series.index:
            dt = ts.date()
            if start <= dt <= end:
                dates.add(dt)
    return sorted(dates)


def _backfilled_rows(
    flows: list[dict],
    trades: list[dict],
    positions: list[dict],
    series_map: dict[str, pd.Series],
    benchmark_ticker: str,
    start: date,
    end: date,
    *,
    equity_mode: bool = False,
    opening_cash_usd: float | None = None,
    fx_events: list[dict[str, Any]] | None = None,
    cash_like_symbols: frozenset[str] | None = None,
) -> list[dict[str, Any]]:
    tracked = [
        (str(pos.get("symbol", "")), pos.get("yahoo_ticker"))
        for pos in positions
        if pos.get("listed") is not False and pos.get("yahoo_ticker")
    ]
    tickers = sorted({ticker for _, ticker in tracked if ticker} | {benchmark_ticker})
    dates = _history_dates(series_map, tickers, start, end)
    trades_by_date: dict[date, list[dict[str, Any]]] = defaultdict(list)
    for trade in trades:
        td = _trade_market_date(trade)
        if td is None or td < start or td > end:
            continue
        trades_by_date[td].append(trade)

    cash_eod: dict[date, float] | None = None
    if equity_mode and opening_cash_usd is not None:
        cash_eod = _cash_eod_market_days(
            dates,
            trades_by_date,
            list(fx_events or []),
            float(opening_cash_usd),
            start,
            end,
        )

    cl_syms = cash_like_symbols if cash_like_symbols is not None else frozenset()
    units_by_symbol: dict[str, float] = defaultdict(float)
    rows: list[dict[str, Any]] = []
    for current_date in dates:
        same_day_trades = sorted(
            trades_by_date.get(current_date, []),
            key=lambda row: str(row.get("executed_at", "")),
        )
        for trade in same_day_trades:
            symbol = str(trade.get("symbol", ""))
            units_by_symbol[symbol] += _trade_units_delta(trade)

        invested = _cum_invested_usd(flows, current_date)
        equity_position_mv = 0.0
        cash_like_mv = 0.0
        has_equity_positions = False
        for symbol, ticker in tracked:
            units = units_by_symbol.get(symbol, 0.0)
            if abs(units) <= 1e-9:
                continue
            close = _series_close_on(series_map, ticker, current_date)
            if close is None:
                continue
            part = units * close
            if symbol in cl_syms:
                cash_like_mv += part
            else:
                equity_position_mv += part
                has_equity_positions = True
        spy_close = _series_close_on(series_map, benchmark_ticker, current_date)

        if cash_eod is not None:
            cash_usd = cash_eod.get(current_date, 0.0) + cash_like_mv
            equity_usd = equity_position_mv + cash_usd
            if (
                invested <= 1e-9
                and abs(equity_usd) <= 1e-9
                and not has_equity_positions
                and cash_like_mv <= 1e-9
            ):
                continue
            rows.append(
                {
                    "date": current_date.isoformat(),
                    "mv_usd": round(equity_usd, 6),
                    "position_mv_usd": round(equity_position_mv, 6),
                    "ledger_cash_usd": round(cash_usd, 6),
                    "cash_like_mv_usd": round(cash_like_mv, 6),
                    "spy_close": round(spy_close, 6) if spy_close is not None else None,
                }
            )
            continue

        total_positions_mv = equity_position_mv + cash_like_mv
        if invested <= 1e-9 and total_positions_mv <= 1e-9:
            continue
        rows.append(
            {
                "date": current_date.isoformat(),
                "mv_usd": round(total_positions_mv, 6),
                "position_mv_usd": round(equity_position_mv, 6),
                "cash_like_mv_usd": round(cash_like_mv, 6),
                "spy_close": round(spy_close, 6) if spy_close is not None else None,
            }
        )
    return rows


def _finalize_rows(
    raw_rows: list[dict[str, Any]],
    flows: list[dict],
    positions: list[dict],
    today: date,
    spy_anchor_close: float | None = None,
    *,
    wealth_mode: bool = False,
    opening_cash_usd: float | None = None,
    fx_events: list[dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = sorted(raw_rows, key=lambda r: r["date"])

    use_flows = bool(flows) and _cum_invested_usd(flows, today) > 1e-9
    fallback_cost = _cost_basis_fallback_usd(positions)

    wealth_funding = bool(
        wealth_mode
        and opening_cash_usd is not None
        and fx_events is not None
    )

    out: list[dict[str, Any]] = []
    first_spy: float | None = None
    latest_mv_usd = 0.0
    for h in rows:
        d = _calendar_date_from_row(h["date"])
        if use_flows:
            inv = _cum_invested_usd(flows, d)
        else:
            inv = fallback_cost
        mv = float(h["mv_usd"])
        latest_mv_usd = mv
        if wealth_funding:
            fund = _funding_usd_through(float(opening_cash_usd), fx_events, d)
            nav_idx = (mv / fund * 100.0) if fund > 1e-9 else None
        elif wealth_mode:
            nav_idx = None
        else:
            nav_idx = (mv / inv * 100.0) if inv > 1e-9 else None
        sc = h.get("spy_close")
        if spy_anchor_close is not None and spy_anchor_close > 0:
            spy_idx = (
                (float(sc) / spy_anchor_close * 100.0) if sc is not None else None
            )
        else:
            if sc is not None and first_spy is None:
                first_spy = float(sc)
            spy_idx = (
                (float(sc) / first_spy * 100.0)
                if first_spy is not None and sc is not None
                else None
            )
        row_out: dict[str, Any] = {
            "date": h["date"],
            "mv_usd": h["mv_usd"],
            "nav_index": round(nav_idx, 4) if nav_idx is not None else None,
            "spy_close": h.get("spy_close"),
            "spy_index": round(spy_idx, 4) if spy_idx is not None else None,
            "cumulative_invested_usd": round(inv, 2),
        }
        if h.get("position_mv_usd") is not None:
            row_out["position_mv_usd"] = h["position_mv_usd"]
        if h.get("ledger_cash_usd") is not None:
            row_out["ledger_cash_usd"] = h["ledger_cash_usd"]
        if h.get("cash_like_mv_usd") is not None:
            row_out["cash_like_mv_usd"] = h["cash_like_mv_usd"]
        if wealth_funding:
            row_out["funding_usd"] = round(
                _funding_usd_through(float(opening_cash_usd), fx_events, d), 2
            )
        out.append(row_out)

    last = out[-1] if out else {}
    pos_tail = last.get("position_mv_usd")
    cash_tail = last.get("ledger_cash_usd")
    # Align denominator (funding / flows invested) with the same calendar date as the
    # latest mv_usd row. Using `today` while mv is stale to the last market row makes
    # nav_index_100 disagree with the last nav_chart point after post-row FX events.
    last_row_date = (
        _calendar_date_from_row(str(last["date"])) if last.get("date") else today
    )
    invested_asof = _cum_invested_usd(flows, last_row_date) if use_flows else fallback_cost

    if wealth_funding:
        fund_asof = _funding_usd_through(float(opening_cash_usd), fx_events, last_row_date)
        nav_index_100 = (
            round((latest_mv_usd / fund_asof * 100.0), 4)
            if fund_asof > 1e-9
            else None
        )
        unrealized = None
        nav_funding_usd_val = round(fund_asof, 2) if fund_asof > 1e-9 else None
    else:
        nav_index_100 = (
            round((latest_mv_usd / invested_asof * 100.0), 4)
            if invested_asof > 1e-9
            else None
        )
        unrealized = (
            round(latest_mv_usd - invested_asof, 4)
            if invested_asof > 1e-9
            else None
        )
        nav_funding_usd_val = None

    summary = {
        "cumulative_invested_usd": round(invested_asof, 2),
        "invested_basis": "flows" if use_flows else "cost_basis_sum",
        "mv_usd": round(float(latest_mv_usd), 4),
        "mv_as_of": last_row_date.isoformat(),
        "nav_index_100": nav_index_100,
        "unrealized_pnl_usd": unrealized,
        "position_mv_usd": round(float(pos_tail), 4) if pos_tail is not None else None,
        "ledger_cash_usd": round(float(cash_tail), 4) if cash_tail is not None else None,
        "nav_funding_usd": nav_funding_usd_val if wealth_funding else None,
        "nav_index_basis": "equity_over_opening_plus_cumulative_fx"
        if wealth_funding
        else None,
    }

    return out, summary


def _spy_nav_benchmark_stats(
    nav_rows: list[dict[str, Any]],
    *,
    bench_field: str = "spy_shadow_index",
) -> dict[str, Any]:
    """Tail summary for UI: interval NAV vs cash-flow shadow benchmark."""
    scored: list[dict[str, Any]] = []
    for r in nav_rows:
        if not isinstance(r, dict):
            continue
        ni = r.get("nav_index")
        si = r.get(bench_field) or r.get("spy_index")
        if ni is None or si is None:
            continue
        try:
            nav_i = float(ni)
            spy_i = float(si)
        except (TypeError, ValueError):
            continue
        mv_raw = r.get("mv_usd")
        mv_f = None
        if mv_raw is not None:
            try:
                mv_f = float(mv_raw)
            except (TypeError, ValueError):
                pass
        scored.append(
            {
                "date": str(r.get("date", "")),
                "nav_index": nav_i,
                "spy_index": spy_i,
                "mv_usd": mv_f,
            }
        )
    if len(scored) < 2:
        return {"ready": False}

    head = scored[0]
    tail = scored[-1]
    pn, ln = head["nav_index"], tail["nav_index"]
    ps, ls = head["spy_index"], tail["spy_index"]
    nav_pct = round((ln / pn - 1.0) * 100.0, 4) if pn > 1e-12 else None
    spy_pct = round((ls / ps - 1.0) * 100.0, 4) if ps > 1e-12 else None
    excess = (
        round(nav_pct - spy_pct, 4)
        if nav_pct is not None and spy_pct is not None
        else None
    )

    prev_row, last_row = scored[-2], scored[-1]
    pn1, ln1 = prev_row["nav_index"], last_row["nav_index"]
    ps1, ls1 = prev_row["spy_index"], last_row["spy_index"]
    nav_1d = round((ln1 / pn1 - 1.0) * 100.0, 4) if pn1 > 1e-12 else None
    spy_1d = round((ls1 / ps1 - 1.0) * 100.0, 4) if ps1 > 1e-12 else None
    excess_1d = (
        round(nav_1d - spy_1d, 4)
        if nav_1d is not None and spy_1d is not None
        else None
    )

    mv_prev = prev_row["mv_usd"]
    mv_last = last_row["mv_usd"]
    mv_delta = None
    mv_pct = None
    if mv_prev is not None and mv_last is not None and mv_prev > 1e-12:
        mv_delta = round(mv_last - mv_prev, 4)
        mv_pct = round((mv_last / mv_prev - 1.0) * 100.0, 4)

    return {
        "ready": True,
        "interval": {
            "from_date": head["date"],
            "to_date": tail["date"],
            "nav_pct": nav_pct,
            "spy_pct": spy_pct,
            "excess_pct_points": excess,
        },
        "prior_row": {
            "prior_date": prev_row["date"],
            "last_date": last_row["date"],
            "nav_1d_pct": nav_1d,
            "spy_1d_pct": spy_1d,
            "excess_pct_points": excess_1d,
            "mv_usd_prior": mv_prev,
            "mv_usd_last": mv_last,
            "mv_usd_delta": mv_delta,
            "mv_usd_pct": mv_pct,
        },
    }


def sync_nav_history(
    path: Path,
    flows: list[dict],
    trades: list[dict],
    positions: list[dict],
    series_map: dict[str, pd.Series],
    benchmark_ticker: str,
    today: date,
    *,
    nav_equity_includes_cash: bool = False,
    cash_usd_anchor: float | None = None,
    fx_events: list[dict[str, Any]] | None = None,
    cash_like_symbols: frozenset[str] | None = None,
    intraday_lookup: Any | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    existing = _existing_rows(path)
    fx_list: list[dict[str, Any]] = list(fx_events or [])
    start_candidates: list[date] = []
    for flow in flows:
        raw_date = flow.get("date")
        if isinstance(raw_date, str) and raw_date:
            start_candidates.append(parse_iso_date(raw_date))
    for trade in trades:
        td = _trade_market_date(trade)
        if td is not None:
            start_candidates.append(td)
    for e in fx_list:
        raw = e.get("date")
        if isinstance(raw, str) and raw:
            start_candidates.append(parse_iso_date(raw))
    if existing and not nav_equity_includes_cash:
        start_candidates.append(_calendar_date_from_row(existing[0]["date"]))
    start = min(start_candidates) if start_candidates else today

    wealth_mode = bool(
        nav_equity_includes_cash
        and cash_usd_anchor is not None
        and isinstance(trades, list)
    )
    ledger_seed: float | None = None
    if wealth_mode:
        net_fx = _net_fx_usd_through(fx_list, today)
        net_tr = _net_cashflow_from_trades_through(trades, today)
        ledger_seed = float(cash_usd_anchor) - net_fx - net_tr

    computed = _backfilled_rows(
        flows=flows,
        trades=trades,
        positions=positions,
        series_map=series_map,
        benchmark_ticker=benchmark_ticker,
        start=start,
        end=today,
        equity_mode=wealth_mode,
        opening_cash_usd=ledger_seed,
        fx_events=fx_list,
        cash_like_symbols=cash_like_symbols,
    )
    if wealth_mode:
        prefix: list[dict[str, Any]] = []
    else:
        prefix = [
            row for row in existing if _calendar_date_from_row(row["date"]) < start
        ]
    merged = prefix + computed
    if not merged:
        merged = [
            {
                "date": today.isoformat(),
                "mv_usd": 0.0,
                "spy_close": _series_close_on(series_map, benchmark_ticker, today),
            }
        ]
    first_trade = _earliest_trade_row(trades)
    spy_anchor: float | None = None
    anchor_source: str | None = None
    if first_trade is not None:
        fd = _trade_market_date(first_trade)
        if fd is not None:
            spy_anchor = _series_open_on(series_map, benchmark_ticker, fd)
            if spy_anchor is not None:
                anchor_source = "yahoo_open"
            else:
                spy_anchor = _series_close_on(series_map, benchmark_ticker, fd)
                if spy_anchor is not None:
                    anchor_source = "yahoo_close"
    out, summary = _finalize_rows(
        merged,
        flows,
        positions,
        today,
        spy_anchor_close=spy_anchor,
        wealth_mode=wealth_mode,
        opening_cash_usd=ledger_seed if wealth_mode else None,
        fx_events=fx_list if wealth_mode else None,
    )
    if first_trade is not None and spy_anchor is not None:
        out = _inject_first_trade_row(out, trades, spy_anchor)
        out = _sort_nav_rows(out)
    from chronicle.build.nav_shadow_benchmark import enrich_nav_unit_and_shadows

    out, shadow_meta = enrich_nav_unit_and_shadows(
        out,
        trades,
        fx_list,
        series_map,
        cash_like_symbols,
        intraday_lookup=intraday_lookup,
    )
    summary.update(shadow_meta)
    summary["spy_nav_benchmark_stats"] = _spy_nav_benchmark_stats(out)
    summary["sso_nav_benchmark_stats"] = _spy_nav_benchmark_stats(
        out, bench_field="sso_shadow_index"
    )
    if out:
        tail = out[-1]
        tail_nav = tail.get("nav_index")
        if tail_nav is not None:
            summary["nav_index_100"] = tail_nav
        tail_mv = tail.get("position_mv_usd")
        if tail_mv is not None:
            summary["mv_usd"] = tail_mv
            summary["mv_as_of"] = str(tail.get("date", ""))[:10] or summary.get("mv_as_of")
    summary["first_trade_at"] = (
        str(first_trade.get("executed_at")) if first_trade else None
    )
    summary["spy_benchmark_anchor"] = anchor_source
    summary["nav_model"] = "equity_cash_ledger" if wealth_mode else "positions_only"
    summary["ledger_cash_seed_usd"] = (
        round(float(ledger_seed), 2) if ledger_seed is not None else None
    )
    summary["nav_cash_includes_fx"] = bool(wealth_mode)
    if nav_equity_includes_cash and cash_usd_anchor is None:
        summary["nav_equity_note"] = "equity_includes_cash_usd enabled but cash_usd is null; kept positions_only"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out, summary


def write_price_history(
    path: Path,
    series_map: dict[str, pd.Series],
    generated_at: date,
) -> None:
    payload = {
        "generated_at": generated_at.isoformat(),
        "tickers": {
            ticker: [
                {"date": ts.date().isoformat(), "close": round(float(value), 6)}
                for ts, value in series.items()
            ]
            for ticker, series in sorted(series_map.items())
            if series is not None
            and not series.empty
            and not str(ticker).endswith("_OPEN")
        },
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)


def charts_payload(nav_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], bool]:
    """Chart.js blocks: unit NAV vs cash-flow SPY / SSO shadows."""
    labels = [r["date"] for r in nav_rows]
    data_nav = [r.get("nav_index") for r in nav_rows]
    data_spy_shadow = [r.get("spy_shadow_index") for r in nav_rows]
    data_sso_shadow = [r.get("sso_shadow_index") for r in nav_rows]
    ready = len(nav_rows) >= 2 and bool(labels)
    nav_chart = {
        "caption_zh": "",
        "labels": labels,
        "datasets": [
            {
                "id": "nav",
                "label": "我的組合 NAV（單位淨值，基期 100）",
                "borderColor": "#496c59",
                "data": data_nav,
            },
            {
                "id": "spy_shadow",
                "label": "SPY 影子（跟你的買賣／現金）",
                "borderColor": "#8c5f34",
                "data": data_spy_shadow,
            },
            {
                "id": "sso_shadow",
                "label": "SSO 正二影子（跟你的買賣／現金）",
                "borderColor": "#6f5a9a",
                "data": data_sso_shadow,
            },
        ],
    }
    spy_compare_chart = {
        "caption_zh": "",
        "labels": labels,
        "datasets": nav_chart["datasets"][1:],
    }
    return nav_chart, spy_compare_chart, ready


def capital_deployed_chart_payload(nav_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Daily cumulative capital vs equity sleeve market value (USD)."""
    labels = [str(r["date"]) for r in nav_rows]
    funding = [r.get("funding_usd") for r in nav_rows]
    position_mv = [r.get("position_mv_usd") for r in nav_rows]
    ready = len(nav_rows) >= 2 and bool(labels)
    return {
        "caption_zh": (
            "棕線＝累計淨換匯投入；綠線＝權益型持股市值。"
            "券商 USD 與 BOXX 為現金側，不進 NAV 單位淨值。"
        ),
        "labels": labels,
        "datasets": [
            {
                "id": "funding_usd",
                "label": "Cumulative capital (net FX, USD)",
                "borderColor": "#8c5f34",
                "data": funding,
            },
            {
                "id": "position_mv_usd",
                "label": "Equity sleeve MV (USD)",
                "borderColor": "#496c59",
                "data": position_mv,
            },
        ],
        "ready": ready,
    }
