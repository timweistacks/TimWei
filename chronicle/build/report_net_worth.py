#!/usr/bin/env python3
"""Net worth: portfolio (USD) + cash, loan outstanding, optional TWD conversion."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from chronicle.build.amortization import (  # noqa: E402
    build_schedule_from_loan_dict,
    count_payments_due_on_or_before,
    liability_for_net_worth_twd,
    parse_iso_date,
)
from chronicle.build.investment_metrics import (  # noqa: E402
    drawdown_reinvest_status,
    investment_assets_twd,
)
from chronicle.build.paths import DATA_DIR, PRICES_DIR  # noqa: E402
from chronicle.build.yahoo_prices import fetch_close_on_or_before  # noqa: E402


def _load_json(name: str) -> dict:
    path = DATA_DIR / name
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _principal_loan(data: dict) -> float:
    basis = data.get("amortization_basis", "contract_principal")
    if basis == "contract_principal":
        return float(data["contract"]["principal_twd"])
    if basis == "net_disbursement":
        return float(data["disbursement"]["net_to_account_twd"])
    raise ValueError(f"unknown amortization_basis: {basis}")


def _read_close_from_cache(ticker: str, as_of: date) -> float | None:
    safe = ticker.replace("^", "").replace("=", "_").replace("/", "_")
    path = PRICES_DIR / f"{safe}_daily.csv"
    if not path.is_file():
        return None
    last_close: float | None = None
    last_d: date | None = None
    with path.open(encoding="utf-8", newline="") as f:
        r = csv.DictReader(f)
        for row in r:
            d = parse_iso_date(row["date"])
            if d <= as_of:
                last_close = float(row["close"])
                last_d = d
    if last_close is None:
        return None
    return last_close


def main() -> None:
    parser = argparse.ArgumentParser(description="Net worth report (personal ledger).")
    parser.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="ISO date (default: today)",
    )
    parser.add_argument(
        "--prefer-cache",
        action="store_true",
        help="Use CSV in chronicle/data/prices when available",
    )
    args = parser.parse_args()

    if args.as_of:
        as_of = parse_iso_date(args.as_of)
    else:
        as_of = date.today()

    loan = _load_json("loan.json")
    port = _load_json("portfolio.json")

    principal = _principal_loan(loan)
    first_due = parse_iso_date(loan["due"]["first_due_date"])
    schedule = build_schedule_from_loan_dict(loan, principal)
    n_paid = count_payments_due_on_or_before(first_due, as_of)
    term = int(loan.get("term_months", 84))
    treat_under = float(loan.get("rounding", {}).get("treat_under_twd_as_paid_after_term", 0))
    outstand, _ = liability_for_net_worth_twd(
        principal,
        schedule,
        n_paid,
        term_months=term,
        treat_under_twd=treat_under,
    )

    cash_twd = float(port.get("cash_twd", 0))
    raw_cusd = port.get("cash_usd")
    cash_usd = float(raw_cusd) if raw_cusd is not None else None
    cash_usd_num = 0.0 if cash_usd is None else float(cash_usd)
    val = port.get("valuation", {})

    pos_lines: list[tuple[str, float, float, float]] = []
    portfolio_usd = 0.0
    for p in port.get("positions", []):
        units = float(p.get("units", 0))
        if p.get("listed") is False:
            sym = p.get("symbol", "")
            pos_lines.append((sym, units, 0.0, 0.0))
            continue
        tkr = p.get("yahoo_ticker") or p.get("symbol")
        if not tkr:
            continue
        if abs(units) < 1e-12:
            pos_lines.append((tkr, units, 0.0, 0.0))
            continue
        px: float | None = None
        if args.prefer_cache:
            px = _read_close_from_cache(tkr, as_of)
        if px is None:
            px = fetch_close_on_or_before(tkr, as_of)
        mv = units * px
        portfolio_usd += mv
        pos_lines.append((tkr, units, px, mv))

    pol = val.get("usd_twd_policy", "manual")
    manual = val.get("usd_twd_rate")
    fx_ticker = val.get("yahoo_usdtwd_ticker", "USDTWD=X")

    usd_exposure_usd = cash_usd_num + portfolio_usd
    usd_twd: float | None = None
    if abs(usd_exposure_usd) >= 1e-12:
        if pol == "manual":
            if manual is None:
                raise SystemExit("usd_twd_policy is manual but usd_twd_rate is null")
            usd_twd = float(manual)
        elif pol == "yahoo":
            if args.prefer_cache:
                usd_twd = _read_close_from_cache(fx_ticker, as_of)
            if usd_twd is None:
                usd_twd = fetch_close_on_or_before(fx_ticker, as_of)
        else:
            raise SystemExit(f"unknown usd_twd_policy: {pol}")
    else:
        usd_twd = float(manual) if manual is not None else 0.0

    assets_twd = cash_twd + (cash_usd_num + portfolio_usd) * usd_twd
    liabilities_twd = outstand
    net_twd = assets_twd - liabilities_twd

    inv_twd = investment_assets_twd(port, portfolio_usd, cash_twd, cash_usd, float(usd_twd or 0.0))
    peak, trig_lvl, dd_pct, dd_hit = drawdown_reinvest_status(port, inv_twd)

    print("=== Net worth (TWD) ===")
    print(f"as_of_date: {as_of.isoformat()}")
    print(
        f"usd_twd_rate: {usd_twd:.4f}  (policy={pol}; "
        f"usd_exposure_usd={usd_exposure_usd:,.4f})"
    )
    print()
    print("--- Cash ---")
    print(f"cash_twd: {cash_twd:,.2f}")
    print(
        f"cash_usd: {cash_usd_num:,.4f}"
        if cash_usd is not None
        else "cash_usd: null (portfolio.cash_usd not set; see fx.json for FX log)"
    )
    print()
    print("--- Positions (USD) ---")
    for tkr, units, px, mv in pos_lines:
        print(f"{tkr}: units={units}  close={px:.4f}  mv_usd={mv:,.2f}")
    print(f"portfolio_mv_usd: {portfolio_usd:,.2f}")
    print()
    print("--- Loan ---")
    print(f"outstanding_principal_twd: {outstand:,.2f}")
    print()
    print("=== Totals ===")
    print(f"assets_twd: {assets_twd:,.2f}")
    print(f"liabilities_twd: {liabilities_twd:,.2f}")
    print(f"net_worth_twd: {net_twd:,.2f}")
    print()
    print("=== Investment assets & drawdown reinvest rule ===")
    pcfg = port.get("drawdown_reinvest") or {}
    pct = float(pcfg.get("trigger_drawdown_from_peak_pct", 0.2))
    print(
        f"investment_assets_twd (listed positions MV -> TWD; cash excluded unless flags): "
        f"{inv_twd:,.2f}"
    )
    if peak is None:
        print(
            "peak_investment_value_twd: (not set; update on each new ATH to track drawdown)"
        )
        print(f"rule: reinvest when assets <= peak * (1 - {pct:.2f})  (e.g. peak 150 -> {150 * (1 - pct):.0f})")
    else:
        print(f"peak_investment_value_twd: {peak:,.2f}")
        print(f"trigger_drawdown_from_peak_pct: {pct:.2f}")
        print(f"trigger_level_twd (peak * (1 - pct)): {trig_lvl:,.2f}" if trig_lvl is not None else "")
        if dd_pct is not None:
            print(f"drawdown_from_peak_pct: {dd_pct * 100:.2f}%")
        print(f"reinvest_trigger_hit: {dd_hit}")


if __name__ == "__main__":
    main()
