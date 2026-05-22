#!/usr/bin/env python3
"""Write chronicle/site/data/snapshot.json (quotes, loan, NAV history vs SPY)."""

from __future__ import annotations

import json
import sys
import time
from datetime import date, timedelta
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

import pandas as pd  # noqa: E402

from chronicle.build.amortization import (  # noqa: E402
    build_schedule_from_loan_dict,
    count_payments_due_on_or_before,
    liability_for_net_worth_twd,
    next_due_on_calendar_day,
    outstanding_after_n_full_payments,
    parse_iso_date,
)
from chronicle.build.intraday_prices import (  # noqa: E402
    build_intraday_lookup,
    enrich_trades_shadow_fills,
)
from chronicle.build.nav_history_lib import (  # noqa: E402
    capital_deployed_chart_payload,
    charts_payload,
    sync_nav_history,
    write_price_history,
)
from chronicle.build.trade_nav_enrichment import (  # noqa: E402
    enrich_trades_with_nav_touchpoints,
)
from chronicle.build.paths import DATA_DIR, SITE_DATA_DIR  # noqa: E402
from chronicle.build.allocation_status import build_portfolio_view  # noqa: E402
from chronicle.build.snapshot_helpers import schedule_to_jsonable  # noqa: E402

WEB_SNAPSHOT = SITE_DATA_DIR / "snapshot.json"
WEB_SNAPSHOT_JS = SITE_DATA_DIR / "snapshot.js"

CHART_LOOKBACK_DAYS = 380


def _align_nav_cash_anchor(
    nav_rows: list[dict],
    nav_summary: dict[str, object],
    nav_path: Path,
    cash_usd: float,
    as_of: date,
) -> list[dict]:
    """Sync nav_summary and optional tail row when portfolio.cash_usd is newer than last EOD."""
    c = round(float(cash_usd), 2)
    nav_summary["ledger_cash_usd"] = c
    pos = nav_summary.get("position_mv_usd")
    if pos is not None:
        nav_summary["equity_plus_cash_usd"] = round(float(pos) + c, 2)
    if not nav_rows:
        return nav_rows
    last = nav_rows[-1]
    last_ledger = float(last.get("ledger_cash_usd", 0) or 0)
    if abs(last_ledger - c) <= 0.01:
        return nav_rows
    pos_last = float(last.get("position_mv_usd", 0) or 0)
    snap = dict(last)
    snap["date"] = as_of.isoformat()
    snap["ledger_cash_usd"] = c
    snap["position_mv_usd"] = round(pos_last, 6)
    snap["mv_usd"] = round(pos_last + c, 6)
    out = nav_rows + [snap]
    nav_path.parent.mkdir(parents=True, exist_ok=True)
    with nav_path.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    return out


BENCHMARKS = (
    ("SPY", "SPY", "S&P 500"),
    ("SSO", "SSO", "S&P 500 2x daily (proxy for 正二)"),
)


def _trade_sort_key(t: dict) -> str:
    return str(t.get("executed_at", ""))


def compute_realized_pnl_from_trades(trades: list[dict]) -> dict[str, object]:
    """
    Average-cost realized P/L from chronological trades.
    Buy cost adds total_usd only (matches portfolio.json cost_basis convention).
    Sell: net_proceeds = total_usd - fee_usd - other_fees_usd; cost_basis = units * avg_cost.
    """
    ordered = sorted(
        [t for t in trades if isinstance(t, dict)],
        key=_trade_sort_key,
    )
    lots: dict[str, dict[str, float]] = {}
    rows: list[dict[str, object]] = []
    total = 0.0

    for t in ordered:
        sym = str(t.get("symbol", "") or "")
        side = str(t.get("side", "")).strip().lower()
        units = float(t.get("units", 0) or 0)
        if not sym or units <= 0:
            continue

        if side == "buy":
            principal = float(t.get("total_usd", 0) or 0)
            fee = float(t.get("fee_usd", 0) or 0)
            other = float(t.get("other_fees_usd", 0) or 0)
            cost_usd = principal + fee + other
            lot = lots.setdefault(sym, {"units": 0.0, "cost_usd": 0.0})
            lot["units"] += units
            lot["cost_usd"] += cost_usd
            continue

        if side != "sell":
            continue

        lot = lots.setdefault(sym, {"units": 0.0, "cost_usd": 0.0})
        u = float(lot["units"])
        c = float(lot["cost_usd"])
        if u <= 1e-12:
            rows.append(
                {
                    "executed_at": t.get("executed_at"),
                    "symbol": sym,
                    "side": "sell",
                    "units": units,
                    "error": "no_position",
                }
            )
            continue
        if units > u + 1e-6:
            rows.append(
                {
                    "executed_at": t.get("executed_at"),
                    "symbol": sym,
                    "side": "sell",
                    "units": units,
                    "error": "insufficient_units",
                }
            )
            continue

        gross = float(t.get("total_usd", 0) or 0)
        fee = float(t.get("fee_usd", 0) or 0)
        other = float(t.get("other_fees_usd", 0) or 0)
        net_proceeds = gross - fee - other

        avg_cost = c / u
        cost_basis = avg_cost * units
        realized = net_proceeds - cost_basis
        total += realized

        lot["units"] = u - units
        lot["cost_usd"] = c - cost_basis
        if lot["units"] < 1e-9:
            lot["units"] = 0.0
            lot["cost_usd"] = 0.0

        rows.append(
            {
                "executed_at": t.get("executed_at"),
                "symbol": sym,
                "side": "sell",
                "units": units,
                "net_proceeds_usd": round(net_proceeds, 2),
                "cost_basis_usd": round(cost_basis, 2),
                "realized_pnl_usd": round(realized, 2),
            }
        )

    ok_rows = [r for r in rows if "realized_pnl_usd" in r]
    return {
        "cost_method": "average_cost",
        "total_realized_pnl_usd": round(total, 2),
        "sell_count": len(ok_rows),
        "rows": rows,
    }


def _position_nav_index_peak_drawdown(
    nav_rows: list[dict], *, wealth_equity_mode: bool
) -> tuple[float | None, float | None, float | None]:
    """Peak / last position-only NAV index and drawdown % from that peak.

    Index = position_mv_usd / denominator * 100. Numerator is listed sleeves only
    (excludes wallet USD and cash_like sleeve MV). Denominator matches the NAV chart:
    funding_usd when equity_cash_ledger, else cumulative_invested_usd.
    """

    indices: list[float] = []
    for row in nav_rows:
        pos_raw = row.get("position_mv_usd")
        if pos_raw is None:
            continue
        pos_f = float(pos_raw)
        if wealth_equity_mode:
            den_raw = row.get("funding_usd")
        else:
            den_raw = row.get("cumulative_invested_usd")
        if den_raw is None:
            continue
        den = float(den_raw)
        if den <= 1e-9:
            continue
        indices.append(pos_f / den * 100.0)
    if not indices:
        return None, None, None
    peak = max(indices)
    current = indices[-1]
    if peak <= 1e-12:
        return None, None, None
    dd_pct = (peak - current) / peak * 100.0
    return peak, current, dd_pct


def _history_start_date(
    end: date, flows: list[dict], trades: list[dict[str, object]]
) -> date:
    anchors: list[date] = []
    for flow in flows:
        raw_date = flow.get("date")
        if isinstance(raw_date, str) and raw_date:
            anchors.append(parse_iso_date(raw_date))
    for trade in trades:
        executed_at = trade.get("executed_at")
        if isinstance(executed_at, str) and executed_at:
            anchors.append(parse_iso_date(executed_at[:10]))
            continue
        raw_date = trade.get("date")
        if isinstance(raw_date, str) and raw_date:
            anchors.append(parse_iso_date(raw_date[:10]))
    if anchors:
        return min(anchors)
    return end - timedelta(days=CHART_LOOKBACK_DAYS)


def _load_portfolio() -> dict:
    with (DATA_DIR / "portfolio.json").open(encoding="utf-8") as f:
        return json.load(f)


def _load_json(name: str) -> dict:
    with (DATA_DIR / name).open(encoding="utf-8") as f:
        return json.load(f)


def _load_json_optional(name: str) -> dict | None:
    p = DATA_DIR / name
    if not p.is_file():
        return None
    with p.open(encoding="utf-8") as f:
        return json.load(f)


def _loan_block(loan: dict, as_of: date) -> dict:
    principal = float(loan["contract"]["principal_twd"])
    schedule = build_schedule_from_loan_dict(loan, principal)
    first_due = parse_iso_date(loan["due"]["first_due_date"])
    n_paid = count_payments_due_on_or_before(first_due, as_of)
    term = int(loan.get("term_months", 84))
    treat = float(loan.get("rounding", {}).get("treat_under_twd_as_paid_after_term", 0))
    raw, cum_int = outstanding_after_n_full_payments(principal, schedule, n_paid)
    liab, _ = liability_for_net_worth_twd(
        principal, schedule, n_paid, term_months=term, treat_under_twd=treat
    )
    next_due = next_due_on_calendar_day(as_of, int(loan["due"]["day_of_month"]))
    disbursement = loan.get("disbursement", {})
    handling_fee = float(disbursement.get("handling_fee_twd", 0) or 0)
    cross_bank_fee = float(disbursement.get("cross_bank_fee_twd", 0) or 0)
    next_row = schedule[n_paid] if 0 <= n_paid < len(schedule) else None
    block = {
        "annual_nominal_rate": float(loan.get("annual_nominal_rate", 0) or 0),
        "contract_principal_twd": principal,
        "cross_bank_fee_twd": cross_bank_fee,
        "cumulative_interest_paid_twd": round(cum_int, 2),
        "cumulative_principal_paid_twd": round(principal - raw, 2),
        "fees_total_twd": round(handling_fee + cross_bank_fee, 2),
        "first_due_date": loan["due"]["first_due_date"],
        "handling_fee_twd": handling_fee,
        "lock_in_months": int(loan.get("lock_in_months", 0) or 0),
        "monthly_payment_twd": float(loan["monthly_payment_twd"]),
        "net_to_account_twd": float(disbursement.get("net_to_account_twd", 0) or 0),
        "next_due_amount_twd": float(loan["monthly_payment_twd"]),
        "next_due_date": next_due.isoformat(),
        "origin_date": loan["origin_date"],
        "outstanding_raw_twd": round(raw, 2),
        "outstanding_twd": round(liab, 2),
        "payments_assumed_count": n_paid,
        "term_months": term,
    }
    if next_row is not None:
        block["next_due_interest_twd"] = round(float(next_row.interest), 2)
        block["next_due_period"] = int(next_row.index)
        block["next_due_principal_twd"] = round(float(next_row.principal), 2)
        block["outstanding_after_next_due_twd"] = round(float(next_row.balance_end), 2)
    if loan.get("reminder"):
        block["reminder"] = loan["reminder"]
    return block


def _net_worth_block(
    cash_twd: float,
    cash_usd: float | None,
    usd_twd: float | None,
    inv_mv_twd: float | None,
    liability_twd: float,
    cash_like_mv_twd: float = 0.0,
) -> dict:
    fx = usd_twd or 0.0
    if cash_usd is None:
        cash_total_twd = cash_twd + float(cash_like_mv_twd)
    else:
        cash_total_twd = cash_twd + float(cash_usd) * fx + float(cash_like_mv_twd)
    inv = inv_mv_twd if inv_mv_twd is not None else 0.0
    assets = cash_total_twd + inv
    net = assets - liability_twd
    return {
        "assets_twd": round(assets, 2),
        "cash_total_twd": round(cash_total_twd, 2),
        "cash_usd_omitted": cash_usd is None,
        "investment_positions_twd": round(inv, 2),
        "liabilities_twd": round(liability_twd, 2),
        "net_worth_twd": round(net, 2),
    }


def _capital_summary_block(
    loan_ui: dict,
    cash_twd: float,
    cash_usd: float | None,
    usd_twd: float | None,
    inv_mv_twd: float | None,
    nw: dict,
    cash_like_mv_twd: float = 0.0,
) -> dict:
    usd_cash_twd = None
    if cash_usd is not None and usd_twd is not None:
        usd_cash_twd = round(float(cash_usd) * float(usd_twd), 2)
    liquid_assets_twd = round(
        cash_twd + (usd_cash_twd or 0.0) + float(cash_like_mv_twd), 2
    )
    investment_mv = float(inv_mv_twd or 0.0)
    project_assets_twd = round(liquid_assets_twd + investment_mv, 2)
    deployment_ratio_pct = None
    if project_assets_twd > 0:
        deployment_ratio_pct = round(investment_mv / project_assets_twd * 100, 2)
    return {
        "cash_twd": round(cash_twd, 2),
        "cash_usd": round(float(cash_usd), 2) if cash_usd is not None else None,
        "cash_usd_twd": usd_cash_twd,
        "contract_principal_twd": float(loan_ui["contract_principal_twd"]),
        "deployment_ratio_pct": deployment_ratio_pct,
        "investment_mv_twd": round(investment_mv, 2),
        "liquid_assets_twd": liquid_assets_twd,
        "loan_outstanding_twd": float(loan_ui["outstanding_twd"]),
        "net_to_account_twd": float(loan_ui.get("net_to_account_twd", 0) or 0),
        "net_worth_twd": float(nw["net_worth_twd"]),
        "project_assets_twd": project_assets_twd,
        "setup_cost_twd": float(loan_ui.get("fees_total_twd", 0) or 0),
    }


def _fx_event_is_twd_to_usd(event: dict) -> bool:
    """Legs where TWD is exchanged for USD (positive USD wallet delta). Excludes USD->TWD."""
    if event.get("direction") == "usd_to_twd":
        return False
    usd = float(event.get("usd_amount", 0) or 0)
    return usd >= 0


def _weighted_fx_rate(events: list[dict]) -> float | None:
    legs = [event for event in events if _fx_event_is_twd_to_usd(event)]
    total_twd = sum(float(event.get("twd_amount", 0) or 0) for event in legs)
    total_usd = sum(float(event.get("usd_amount", 0) or 0) for event in legs)
    if total_usd <= 1e-9:
        return None
    return total_twd / total_usd


def _investment_cost_block(
    flows: list[dict],
    fx_events: list[dict],
    current_usd_twd: float | None,
    investment_mv_twd: float | None,
    cash_like_symbols: frozenset[str] | None = None,
) -> dict:
    fx_by_date: dict[str, list[dict]] = {}
    for event in fx_events:
        raw_date = event.get("date")
        if isinstance(raw_date, str) and raw_date:
            fx_by_date.setdefault(raw_date, []).append(event)

    historical_cost_twd = 0.0
    invested_usd = 0.0
    matched = 0
    unmatched = 0
    used_rates: list[float] = []
    fx_fallback_rate = _weighted_fx_rate(fx_events)
    skip_sym = cash_like_symbols or frozenset()

    for flow in flows:
        sym = str(flow.get("symbol", "") or "")
        if sym in skip_sym:
            continue
        usd_total = float(flow.get("usd", 0) or 0) + float(flow.get("fees_usd", 0) or 0)
        # Negative usd (e.g. sell releasing cost basis) must not be skipped.
        if abs(usd_total) <= 1e-9:
            continue
        invested_usd += usd_total
        if flow.get("cost_twd") is not None:
            historical_cost_twd += float(flow.get("cost_twd") or 0)
            matched += 1
            continue
        explicit_rate = flow.get("funding_fx_rate_twd_per_usd")
        if explicit_rate is not None:
            rate = float(explicit_rate)
            historical_cost_twd += usd_total * rate
            used_rates.append(rate)
            matched += 1
            continue
        flow_date = flow.get("date")
        same_day_events = fx_by_date.get(flow_date, []) if isinstance(flow_date, str) else []
        same_day_rate = _weighted_fx_rate(same_day_events)
        if same_day_rate is not None:
            historical_cost_twd += usd_total * same_day_rate
            used_rates.append(same_day_rate)
            matched += 1
            continue
        if fx_fallback_rate is not None:
            historical_cost_twd += usd_total * float(fx_fallback_rate)
            used_rates.append(float(fx_fallback_rate))
            matched += 1
            continue
        unmatched += 1

    if matched == 0 and invested_usd > 1e-9 and current_usd_twd is not None:
        estimated_twd = invested_usd * float(current_usd_twd)
        pnl_twd = (
            round(float(investment_mv_twd) - estimated_twd, 2)
            if investment_mv_twd is not None
            else None
        )
        return {
            "historical_cost_twd": None,
            "current_fx_equivalent_twd": round(estimated_twd, 2),
            "invested_usd": round(invested_usd, 2),
            "matched_flow_count": 0,
            "unmatched_flow_count": unmatched,
            "historical_fx_rate_avg": None,
            "twd_cost_method": "current_fx_fallback",
            "unrealized_pnl_twd": pnl_twd,
        }

    historical_twd = round(historical_cost_twd, 2) if matched > 0 and unmatched == 0 else None
    pnl_twd = (
        round(float(investment_mv_twd) - historical_twd, 2)
        if investment_mv_twd is not None and historical_twd is not None
        else None
    )
    avg_rate = _weighted_fx_rate(
        [{"twd_amount": rate, "usd_amount": 1.0} for rate in used_rates]
    )
    return {
        "historical_cost_twd": historical_twd,
        "current_fx_equivalent_twd": round(invested_usd * float(current_usd_twd), 2)
        if current_usd_twd is not None
        else None,
        "invested_usd": round(invested_usd, 2),
        "matched_flow_count": matched,
        "unmatched_flow_count": unmatched,
        "historical_fx_rate_avg": round(avg_rate, 4) if avg_rate is not None else None,
        "twd_cost_method": "historical_fx_log" if unmatched == 0 else "partial_historical_fx_log",
        "unrealized_pnl_twd": pnl_twd,
    }


def _record_health_block(
    capital_events: dict,
    cash_buckets: dict,
    rule_events: dict,
    rebalance_log: dict,
    income_events: dict,
    ledger_intent: dict,
) -> dict:
    cash_snapshots = cash_buckets.get("snapshots", [])
    pending_followups = ledger_intent.get("pending_followups_zh", [])
    return {
        "capital_event_count": len(capital_events.get("events", [])),
        "cash_snapshot_count": len(cash_snapshots),
        "latest_cash_snapshot_as_of": cash_snapshots[-1].get("as_of") if cash_snapshots else None,
        "rule_event_count": len(rule_events.get("events", [])),
        "rebalance_log_count": len(rebalance_log.get("entries", [])),
        "income_event_count": len(income_events.get("events", [])),
        "pending_followup_count": len(pending_followups),
        "first_pending_followup_zh": pending_followups[0] if pending_followups else "",
    }


def _close_series(ticker: str, start: date, end: date) -> pd.Series | None:
    """Fetch daily closes; retries and period= fallback help when Yahoo returns empty JSON."""
    import yfinance as yf

    t = yf.Ticker(ticker)
    hist = None
    for attempt in range(3):
        hist = t.history(
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),
            auto_adjust=True,
        )
        if hist is not None and not hist.empty and "Close" in hist.columns:
            break
        time.sleep(0.6 * (attempt + 1))
    if hist is None or hist.empty or "Close" not in hist.columns:
        hist = t.history(period="2y", auto_adjust=True)
    if hist is None or hist.empty or "Close" not in hist.columns:
        return None
    s = hist["Close"].copy()
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end + timedelta(days=1))
    s = s.loc[(s.index >= start_ts) & (s.index < end_ts)]
    if s.empty:
        return None
    return s


def _open_series(ticker: str, start: date, end: date) -> pd.Series | None:
    """Daily opens for benchmark anchor (same fetch path as closes)."""
    import yfinance as yf

    t = yf.Ticker(ticker)
    hist = None
    for attempt in range(3):
        hist = t.history(
            start=start.isoformat(),
            end=(end + timedelta(days=1)).isoformat(),
            auto_adjust=True,
        )
        if hist is not None and not hist.empty and "Open" in hist.columns:
            break
        time.sleep(0.6 * (attempt + 1))
    if hist is None or hist.empty or "Open" not in hist.columns:
        hist = t.history(period="2y", auto_adjust=True)
    if hist is None or hist.empty or "Open" not in hist.columns:
        return None
    s = hist["Open"].copy()
    s.index = pd.to_datetime(s.index).tz_localize(None).normalize()
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end + timedelta(days=1))
    s = s.loc[(s.index >= start_ts) & (s.index < end_ts)]
    if s.empty:
        return None
    return s


def _resolve_usd_twd(
    val: dict, end: date, errors: list[str]
) -> tuple[float | None, str]:
    """Prefer Yahoo USDTWD=X; fallback to manual rate from portfolio valuation."""
    pol = val.get("usd_twd_policy", "yahoo")
    manual = val.get("usd_twd_rate")
    tkr = val.get("yahoo_usdtwd_ticker", "USDTWD=X")
    if pol == "manual":
        if manual is not None:
            return float(manual), "manual"
        errors.append("usd_twd_policy_manual_missing_rate")
        return None, "missing"
    s = _close_series(tkr, end - timedelta(days=35), end)
    if s is not None and not s.empty:
        return float(s.iloc[-1]), "yahoo"
    errors.append(f"no_close:{tkr}")
    if manual is not None:
        return float(manual), "manual_fallback"
    return None, "missing"


def main() -> None:
    port = _load_portfolio()
    nav_cfg = port.get("nav") or {}
    cash_like_syms: frozenset[str] = frozenset(
        str(x).strip()
        for x in (nav_cfg.get("cash_like_symbols") or ["BOXX"])
        if str(x).strip()
    )
    val = port.get("valuation", {})
    end = date.today()
    errors: list[str] = []
    usd_twd, usd_twd_source = _resolve_usd_twd(val, end, errors)
    flows_path = DATA_DIR / "investment_flows.json"
    flows_list: list = []
    if flows_path.is_file():
        flows_list = json.loads(flows_path.read_text(encoding="utf-8")).get("flows", [])
    trade_ledger = _load_json_optional("trades.json") or {"trades": []}
    trades_list = trade_ledger.get("trades", [])

    positions = port.get("positions", [])
    pos_rows: list[dict] = []
    for p in positions:
        sym = p.get("symbol", "")
        if p.get("listed") is False:
            pos_rows.append(
                {
                    "listed": False,
                    "symbol": sym,
                    "units": float(p.get("units", 0)),
                    "yahoo_ticker": None,
                    "cost_basis_usd": float(p.get("cost_basis_usd", 0) or 0),
                }
            )
            continue
        tkr = p.get("yahoo_ticker") or sym
        pos_rows.append(
            {
                "listed": True,
                "symbol": sym,
                "units": float(p.get("units", 0)),
                "yahoo_ticker": tkr,
                "cost_basis_usd": float(p.get("cost_basis_usd", 0) or 0),
            }
        )

    start = _history_start_date(end, flows_list, trades_list)

    # History for holdings + benchmarks
    tickers: list[str] = []
    for pr in pos_rows:
        if pr["yahoo_ticker"] and pr["yahoo_ticker"] not in tickers:
            tickers.append(pr["yahoo_ticker"])
    bench_ids = [b[0] for b in BENCHMARKS]
    for b in bench_ids:
        if b not in tickers:
            tickers.append(b)

    series_map: dict[str, pd.Series] = {}
    for tkr in tickers:
        s = _close_series(tkr, start, end)
        if s is None:
            errors.append(f"no_close:{tkr}")
            continue
        series_map[tkr] = s
    spy_open = _open_series("SPY", start, end)
    if spy_open is not None:
        series_map["SPY_OPEN"] = spy_open
    fx_history_ticker = val.get("yahoo_usdtwd_ticker", "USDTWD=X")
    fx_history_series = _close_series(fx_history_ticker, start, end)
    if fx_history_series is not None and not fx_history_series.empty:
        series_map[fx_history_ticker] = fx_history_series

    quotes: list[dict] = []
    for pr in pos_rows:
        tkr = pr.get("yahoo_ticker")
        if pr.get("listed") is False:
            quotes.append(
                {
                    "last_usd": None,
                    "listed": False,
                    "listing_note": "pending",
                    "symbol": pr["symbol"],
                    "units": pr["units"],
                    "yahoo_ticker": None,
                }
            )
            continue
        s = series_map.get(tkr) if tkr else None
        last = float(s.iloc[-1]) if s is not None and not s.empty else None
        units = float(pr["units"])
        cost_basis = float(pr.get("cost_basis_usd", 0) or 0)
        avg_entry = (cost_basis / units) if units > 1e-9 else None
        unrealized = None
        if last is not None and avg_entry is not None:
            unrealized = (last - avg_entry) * units
        q: dict = {
            "listed": True,
            "symbol": pr["symbol"],
            "yahoo_ticker": tkr,
            "last_usd": last,
            "units": pr["units"],
            "avg_entry_usd": round(avg_entry, 6) if avg_entry is not None else None,
            "unrealized_pnl_usd": round(unrealized, 2) if unrealized is not None else None,
        }
        if last is not None and usd_twd is not None:
            q["last_twd"] = round(last * usd_twd, 2)
        if pr["symbol"] in cash_like_syms:
            q["cash_like"] = True
        quotes.append(q)

    for bid, _, _ in BENCHMARKS:
        s = series_map.get(bid)
        last = float(s.iloc[-1]) if s is not None and not s.empty else None
        quotes.append(
            {
                "symbol": bid,
                "yahoo_ticker": bid,
                "last_usd": last,
                "benchmark": True,
            }
        )

    cash_like_mv_usd = 0.0
    for q in quotes:
        if q.get("benchmark") or q.get("listed") is False:
            continue
        sym = str(q.get("symbol", ""))
        if sym not in cash_like_syms:
            continue
        if q.get("last_usd") is not None:
            cash_like_mv_usd += float(q.get("units", 0) or 0) * float(q["last_usd"])

    inv_mv_usd = 0.0
    for pr in pos_rows:
        if pr.get("symbol") in cash_like_syms:
            continue
        tkr = pr.get("yahoo_ticker")
        if not tkr:
            continue
        u = pr["units"]
        s = series_map.get(tkr)
        if s is None or s.empty:
            continue
        inv_mv_usd += float(u) * float(s.iloc[-1])

    inv_mv_twd = round(inv_mv_usd * usd_twd, 2) if usd_twd is not None else None
    cash_like_mv_twd = (
        round(cash_like_mv_usd * float(usd_twd), 2) if usd_twd is not None else 0.0
    )

    cash_twd = float(port.get("cash_twd", 0))
    raw_cusd = port.get("cash_usd")
    cash_usd = float(raw_cusd) if raw_cusd is not None else None
    nav_equity_want = bool(nav_cfg.get("equity_includes_cash_usd", False))
    nav_equity_on = nav_equity_want and cash_usd is not None
    if nav_equity_want and cash_usd is None:
        errors.append(
            "nav.equity_includes_cash_usd is true but portfolio.cash_usd is null; NAV chart uses positions-only mv"
        )

    spy_series = series_map.get("SPY")
    spy_last = (
        float(spy_series.iloc[-1])
        if spy_series is not None and not spy_series.empty
        else None
    )

    fxj = _load_json("fx.json")
    shadow_tickers = ("SPY", "SSO")
    intraday_lookup = build_intraday_lookup(
        trades_list,
        series_map,
        shadow_tickers,
        as_of=end,
        cash_like_symbols=cash_like_syms,
    )
    nav_path = DATA_DIR / "nav_history.json"
    nav_rows, nav_summary = sync_nav_history(
        nav_path,
        flows_list,
        trades_list,
        positions,
        series_map,
        "SPY",
        end,
        nav_equity_includes_cash=nav_equity_on,
        cash_usd_anchor=cash_usd if nav_equity_on else None,
        fx_events=fxj.get("events", []),
        cash_like_symbols=cash_like_syms,
        intraday_lookup=intraday_lookup,
    )
    if cash_usd is not None and nav_equity_on:
        nav_rows = _align_nav_cash_anchor(
            nav_rows, nav_summary, nav_path, cash_usd, end
        )
    fallback_invested_usd = max(
        sum(float(p.get("cost_basis_usd", 0) or 0) for p in positions),
        1e-9,
    )
    unit_nav_basis = (
        nav_summary.get("nav_index_basis") == "unit_fund_deployed_on_trade"
    )
    trades_enriched = enrich_trades_with_nav_touchpoints(
        trades_list,
        positions,
        series_map,
        fxj.get("events", []),
        flows_list,
        as_of=end,
        wealth_mode=nav_summary.get("nav_model") == "equity_cash_ledger",
        cash_usd_anchor=cash_usd if nav_equity_on else None,
        fallback_invested_usd=fallback_invested_usd,
        cash_like_symbols=cash_like_syms,
        unit_nav_touch=unit_nav_basis,
    )
    trades_enriched = enrich_trades_shadow_fills(
        trades_enriched,
        intraday_lookup,
        shadow_tickers,
        cash_like_symbols=cash_like_syms,
    )
    write_price_history(DATA_DIR / "prices" / "history.json", series_map, end)

    nav_chart, spy_compare_chart, charts_ready = charts_payload(nav_rows)
    capital_deployed_chart = capital_deployed_chart_payload(nav_rows)
    if nav_summary.get("nav_model") == "equity_cash_ledger":
        nav_chart["caption_zh"] = (
            "綠線 = 單位淨值 NAV（僅權益型 ETF 持股市值；閒置 USD 與 BOXX 不計入）；"
            "換匯（含美金換台幣）不動單位；僅權益型 ETF 買入增單位、賣出減單位。"
            "棕線 = 若改買 SPY（跟你的股票買賣名目；成交時點對 Yahoo 1m/5m）；"
            "紫線 = 同上改 SSO。BOXX 等同美金現金，不進 NAV、不動影子。"
        )

    loan_data = _load_json("loan.json")
    loan_ui = _loan_block(loan_data, end)
    principal_loan = float(loan_data["contract"]["principal_twd"])
    schedule_full = build_schedule_from_loan_dict(loan_data, principal_loan)
    loan_schedule_computed = {
        "caption_zh": "",
        "method": loan_data.get("interest", {}).get("method", "daily_365"),
        "rows": schedule_to_jsonable(schedule_full),
    }
    nw = _net_worth_block(
        cash_twd,
        cash_usd,
        usd_twd,
        inv_mv_twd,
        float(loan_ui["outstanding_twd"]),
        cash_like_mv_twd,
    )
    capital_summary = _capital_summary_block(
        loan_ui,
        cash_twd,
        cash_usd,
        usd_twd,
        inv_mv_twd,
        nw,
        cash_like_mv_twd,
    )
    net_worth_note_zh = "未計入 USD 現金（portfolio.cash_usd 未填）" if cash_usd is None else None

    alloc = _load_json("allocations.json")
    investment_cost = _investment_cost_block(
        flows_list,
        fxj.get("events", []),
        usd_twd,
        inv_mv_twd,
        cash_like_syms,
    )
    capital_events = _load_json_optional("capital_events.json") or {"events": []}
    cash_buckets_full = _load_json_optional("cash_buckets.json") or {"snapshots": []}
    rule_events = _load_json_optional("rule_events.json") or {"events": []}
    rebalance_log = _load_json_optional("rebalance_log.json") or {"entries": []}
    income_events = _load_json_optional("income_events.json") or {"events": []}
    ledger_intent = _load_json_optional("ledger_intent.json") or {"pending_followups_zh": []}
    record_health = _record_health_block(
        capital_events,
        cash_buckets_full,
        rule_events,
        rebalance_log,
        income_events,
        ledger_intent,
    )
    dd = port.get("drawdown_reinvest") or {}
    trigger_pct = float(dd.get("trigger_drawdown_from_peak_pct", 0.2))
    manual_peak = dd.get("peak_investment_value_twd")
    manual_peak_f = float(manual_peak) if manual_peak is not None else None

    wealth_equity_dd = nav_summary.get("nav_model") == "equity_cash_ledger"

    drawdown_ui: dict = {
        "peak_investment_value_twd": manual_peak,
        "trigger_drawdown_from_peak_pct": trigger_pct,
    }

    if manual_peak_f is not None and manual_peak_f > 0 and inv_mv_twd is not None:
        drawdown_ui["effective_peak_twd"] = round(manual_peak_f, 2)
        drawdown_ui["current_vs_peak_pct"] = round(
            (manual_peak_f - float(inv_mv_twd)) / manual_peak_f * 100.0,
            2,
        )
        drawdown_ui["trigger_level_twd"] = round(manual_peak_f * (1.0 - trigger_pct), 2)
    else:
        peak_idx, cur_idx, dd_pct = _position_nav_index_peak_drawdown(
            nav_rows, wealth_equity_mode=wealth_equity_dd
        )
        if peak_idx is not None and cur_idx is not None and dd_pct is not None:
            peak_idx_f = float(peak_idx)
            drawdown_ui["effective_peak_nav_index"] = round(peak_idx_f, 4)
            drawdown_ui["current_position_nav_index"] = round(float(cur_idx), 4)
            drawdown_ui["current_vs_peak_pct"] = round(float(dd_pct), 2)
            drawdown_ui["trigger_nav_index"] = round(peak_idx_f * (1.0 - trigger_pct), 4)

    capital_buckets = _load_json_optional("capital_buckets.json") or {}
    bucket_list = capital_buckets.get("buckets", [])
    project_buckets_total_twd = round(
        sum(float(b.get("amount_twd", 0) or 0) for b in bucket_list), 2
    )
    reb_cfg = alloc.get("rebalance") or {}
    inc_cash_denom = bool(reb_cfg.get("include_cash_usd_in_denominator", False))
    rebalance_cash_usd: float | None = None
    if inc_cash_denom:
        if cash_usd is None:
            errors.append(
                "allocations.rebalance.include_cash_usd_in_denominator is true "
                "but portfolio.cash_usd is null; rebalance denominator excludes cash"
            )
        else:
            rebalance_cash_usd = float(cash_usd)

    deploy_all_cash = bool(reb_cfg.get("deploy_all_cash_usd", False))
    exact_min_usd = float(reb_cfg.get("exact_target_min_trade_usd", 5.0))

    portfolio_view = build_portfolio_view(
        alloc,
        pos_rows,
        series_map,
        usd_twd,
        end,
        inv_mv_twd,
        inv_mv_usd,
        rebalance_cash_usd=rebalance_cash_usd,
        deploy_all_cash_usd=deploy_all_cash,
        exact_target_min_trade_usd=exact_min_usd,
    )
    ph = portfolio_view.get("phase") or {}
    cash_like_usd = (
        round(float(cash_usd) + cash_like_mv_usd, 2)
        if cash_usd is not None
        else None
    )
    boxx_only_mv_usd = 0.0
    if "BOXX" in cash_like_syms:
        for q in quotes:
            if q.get("benchmark") or q.get("listed") is False:
                continue
            if str(q.get("symbol", "")) != "BOXX" or q.get("last_usd") is None:
                continue
            boxx_only_mv_usd += float(q.get("units", 0) or 0) * float(q["last_usd"])
    overview = {
        "assets_twd": nw["assets_twd"],
        "broker_cash_plus_boxx_mv_usd": cash_like_usd,
        "broker_cash_plus_cash_like_mv_usd": cash_like_usd,
        "boxx_market_value_usd": round(boxx_only_mv_usd, 2)
        if boxx_only_mv_usd > 1e-9
        else 0.0,
        "cash_like_market_value_usd": round(cash_like_mv_usd, 2)
        if cash_like_mv_usd > 1e-9
        else 0.0,
        "cash_like_symbols": sorted(cash_like_syms),
        "cash_like_note_zh": (
            "券商 USD 餘額 + BOXX 市值（等同美金現金，計入淨資產現金側）；"
            "NAV 綠線與 SPY 影子僅跟權益型 ETF 買賣，不含閒置現金與 BOXX。"
        ),
        "investment_mv_twd": inv_mv_twd,
        "liabilities_twd": nw["liabilities_twd"],
        "loan_next_due_amount_twd": loan_ui["next_due_amount_twd"],
        "loan_next_due_date": loan_ui["next_due_date"],
        "net_worth_twd": nw["net_worth_twd"],
        "phase_id": ph.get("id"),
        "phase_range": {
            "from": ph.get("effective_from"),
            "to": ph.get("effective_to"),
        },
        "project_buckets_note_zh": capital_buckets.get("ledger_scope_note_zh")
        or capital_buckets.get("project_scope_note_zh")
        or "",
        "project_buckets_total_twd": project_buckets_total_twd,
        "rebalance_needed": portfolio_view.get("rebalance_needed", False),
        "usd_twd": usd_twd,
        "usd_twd_source": usd_twd_source,
    }

    realized_pnl = compute_realized_pnl_from_trades(trades_list)
    if usd_twd is not None and realized_pnl.get("total_realized_pnl_usd") is not None:
        realized_pnl = {
            **realized_pnl,
            "total_realized_pnl_twd": round(
                float(realized_pnl["total_realized_pnl_usd"]) * float(usd_twd), 2
            ),
        }

    out = {
        "allocations": {
            "monthly_contribution": alloc.get("monthly_contribution"),
            "phases": alloc.get("phases", []),
            "rebalance": alloc.get("rebalance"),
        },
        "benchmarks_note": "",
        "capital_summary": capital_summary,
        "capital_deployed_chart": capital_deployed_chart,
        "capital_buckets": capital_buckets,
        "cash_buckets": cash_buckets_full,
        "cash_usd": cash_usd,
        "cash_twd": cash_twd,
        "charts_ready": charts_ready,
        "capital_events": capital_events,
        "drawdown_reinvest": drawdown_ui,
        "errors": errors,
        "fx_events": fxj.get("events", []),
        "generated_at": date.today().isoformat(),
        "income_events": income_events,
        "ledger_intent": ledger_intent,
        "loan_schedule_computed": loan_schedule_computed,
        "investment_cost": investment_cost,
        "investment_mv_twd": inv_mv_twd,
        "investment_mv_usd": round(inv_mv_usd, 4),
        "liabilities": {
            "loan_next_due_amount_twd": loan_ui["next_due_amount_twd"],
            "loan_next_due_date": loan_ui["next_due_date"],
            "loan_outstanding_twd": loan_ui["outstanding_twd"],
            "net_worth_liabilities_twd": nw["liabilities_twd"],
        },
        "loan": loan_ui,
        "nav_chart": nav_chart,
        "nav_history_days": len(nav_rows),
        "nav_summary": nav_summary,
        "net_worth": nw,
        "net_worth_note_zh": net_worth_note_zh,
        "overview": overview,
        "platform_note_zh": "",
        "portfolio_view": portfolio_view,
        "refresh_hint_zh": "",
        "rebalance_log": rebalance_log,
        "record_health": record_health,
        "quotes": quotes,
        "realized_pnl": realized_pnl,
        "rule_events": rule_events,
        "spy_compare_chart": spy_compare_chart,
        "trade_ledger": {
            "count": len(trade_ledger.get("trades", [])),
            "trades": trades_enriched,
        },
        "usd_twd": usd_twd,
        "usd_twd_source": usd_twd_source,
    }

    realized_path = DATA_DIR / "realized_pnl.json"
    realized_path.parent.mkdir(parents=True, exist_ok=True)
    with realized_path.open("w", encoding="utf-8") as f:
        json.dump(
            {"generated_at": date.today().isoformat(), **realized_pnl},
            f,
            ensure_ascii=False,
            indent=2,
        )

    WEB_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
    with WEB_SNAPSHOT.open("w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    payload_js = json.dumps(out, ensure_ascii=False, indent=2)
    payload_js = payload_js.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    WEB_SNAPSHOT_JS.write_text(
        f"window.__PERSONAL_LEDGER_SNAPSHOT__ = {payload_js};\n",
        encoding="utf-8",
    )

    print(f"wrote {WEB_SNAPSHOT}")
    print(f"wrote {realized_path}")


if __name__ == "__main__":
    main()
