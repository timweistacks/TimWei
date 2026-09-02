"""Approximate per-trade NAV touchpoints for personal ledger UI."""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any

import pandas as pd

from chronicle.build.nav_history_lib import (
    _cum_invested_usd,
    _funding_usd_through,
    _fx_event_dt,
    _net_cashflow_from_trades_through,
    _net_fx_usd_through,
    _series_close_on,
    _trade_cash_delta,
    _trade_date,
    _trade_event_dt,
    _trade_market_date,
    _trade_units_delta,
)


def _tracked_pairs(positions: list[dict[str, Any]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    for pos in positions:
        if pos.get("listed") is False:
            continue
        sym = str(pos.get("symbol", "") or "")
        tkr = pos.get("yahoo_ticker")
        if not sym or not tkr:
            continue
        out.append((sym, str(tkr)))
    return out


def _mark_equity_positions_only(
    units: dict[str, float],
    as_of: date,
    tracked: list[tuple[str, str]],
    series_map: dict[str, pd.Series],
) -> float | None:
    total = 0.0
    for symbol, ticker in tracked:
        u = float(units.get(symbol, 0.0))
        if abs(u) <= 1e-12:
            continue
        close = _series_close_on(series_map, ticker, as_of)
        if close is None:
            return None
        total += u * close
    return total


def _mark_equity_wealth(
    units: dict[str, float],
    wallet_cash_usd: float,
    as_of: date,
    tracked: list[tuple[str, str]],
    cash_like_syms: frozenset[str],
    series_map: dict[str, pd.Series],
) -> float | None:
    equity_mv = 0.0
    cash_like_mv = 0.0
    for symbol, ticker in tracked:
        u = float(units.get(symbol, 0.0))
        if abs(u) <= 1e-12:
            continue
        close = _series_close_on(series_map, ticker, as_of)
        if close is None:
            return None
        part = u * close
        if symbol in cash_like_syms:
            cash_like_mv += part
        else:
            equity_mv += part
    return equity_mv + cash_like_mv + float(wallet_cash_usd)


def enrich_trades_with_nav_touchpoints(
    trades: list[dict[str, Any]],
    positions: list[dict[str, Any]],
    series_map: dict[str, pd.Series],
    fx_events: list[dict[str, Any]],
    flows: list[dict[str, Any]],
    *,
    as_of: date,
    wealth_mode: bool,
    cash_usd_anchor: float | None,
    fallback_invested_usd: float,
    cash_like_symbols: frozenset[str],
    unit_nav_touch: bool = False,
) -> list[dict[str, Any]]:
    """Return trades with nav_touch_pts and nav_touch_equity_delta_usd added."""

    tracked = _tracked_pairs(positions)
    fx_list = list(fx_events or [])
    flows_list = list(flows or [])

    ledger_seed: float | None = None
    if wealth_mode and cash_usd_anchor is not None:
        ledger_seed = float(cash_usd_anchor) - _net_fx_usd_through(
            fx_list, as_of
        ) - _net_cashflow_from_trades_through(trades, as_of)

    use_flows = bool(flows_list) and _cum_invested_usd(flows_list, as_of) > 1e-9

    timeline: list[tuple[str, Any, Any]] = []
    for e in fx_list:
        timeline.append(("fx", _fx_event_dt(e), e))
    sorted_indices = sorted(range(len(trades)), key=lambda i: _trade_event_dt(trades[i]))
    for idx in sorted_indices:
        timeline.append(("trade", _trade_event_dt(trades[idx]), idx))
    timeline.sort(key=lambda row: row[1])

    cash_wallet = float(ledger_seed) if ledger_seed is not None else 0.0
    units: dict[str, float] = defaultdict(float)
    extras_by_idx: dict[int, dict[str, Any]] = {}

    for kind, _evt_dt, payload in timeline:
        if kind == "fx":
            if wealth_mode and ledger_seed is not None:
                cash_wallet += float(payload.get("usd_amount", 0) or 0)
            continue

        idx = int(payload)
        trade = trades[idx]
        sym = str(trade.get("symbol", "") or "")
        td = _trade_market_date(trade)
        if td is None:
            extras_by_idx[idx] = {
                "nav_touch_pts": None,
                "nav_touch_equity_delta_usd": None,
            }
            continue

        if unit_nav_touch:
            eq_before = _mark_equity_positions_only(units, td, tracked, series_map)
            ud = _trade_units_delta(trade)
            if sym not in cash_like_symbols:
                units[sym] += ud
            eq_after = _mark_equity_positions_only(units, td, tracked, series_map)
            inv = (
                _cum_invested_usd(flows_list, td) if use_flows else fallback_invested_usd
            )
            fund = float(inv) if inv > 1e-9 else float(fallback_invested_usd)
        elif wealth_mode and ledger_seed is not None:
            eq_before = _mark_equity_wealth(
                units, cash_wallet, td, tracked, cash_like_symbols, series_map
            )
            cd = _trade_cash_delta(trade)
            ud = _trade_units_delta(trade)
            units[sym] += ud
            cash_wallet += cd
            eq_after = _mark_equity_wealth(
                units, cash_wallet, td, tracked, cash_like_symbols, series_map
            )
            fund = _funding_usd_through(ledger_seed, fx_list, td)
        else:
            eq_before = _mark_equity_positions_only(units, td, tracked, series_map)
            ud = _trade_units_delta(trade)
            units[sym] += ud
            eq_after = _mark_equity_positions_only(units, td, tracked, series_map)
            inv = (
                _cum_invested_usd(flows_list, td) if use_flows else fallback_invested_usd
            )
            fund = float(inv) if inv > 1e-9 else float(fallback_invested_usd)

        touch_pts = None
        delta_eq = None
        if eq_before is not None and eq_after is not None and fund > 1e-9:
            delta_eq = eq_after - eq_before
            touch_pts = round(delta_eq / fund * 100.0, 6)

        extras_by_idx[idx] = {
            "nav_touch_pts": touch_pts,
            "nav_touch_equity_delta_usd": round(delta_eq, 6) if delta_eq is not None else None,
        }

    out: list[dict[str, Any]] = []
    for i, row in enumerate(trades):
        merged = dict(row)
        merged.update(extras_by_idx.get(i, {}))
        out.append(merged)
    return out
