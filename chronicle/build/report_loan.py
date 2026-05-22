#!/usr/bin/env python3
"""Print amortization schedule, cumulative interest, next due date for personal loan."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from chronicle.build.amortization import (
    build_schedule_from_loan_dict,
    count_payments_due_on_or_before,
    liability_for_net_worth_twd,
    next_due_on_calendar_day,
    outstanding_after_n_full_payments,
    parse_iso_date,
)
from chronicle.build.paths import DATA_DIR  # noqa: E402


def _load_loan() -> dict:
    path = DATA_DIR / "loan.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _principal_from_basis(data: dict) -> float:
    basis = data.get("amortization_basis", "contract_principal")
    if basis == "contract_principal":
        return float(data["contract"]["principal_twd"])
    if basis == "net_disbursement":
        return float(data["disbursement"]["net_to_account_twd"])
    raise ValueError(f"unknown amortization_basis: {basis}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Loan amortization report (personal ledger).")
    parser.add_argument(
        "--as-of",
        type=str,
        default=None,
        help="ISO date for outstanding balance (default: today)",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=120,
        help="Max rows to print from schedule",
    )
    args = parser.parse_args()

    data = _load_loan()
    principal = _principal_from_basis(data)
    rate = float(data["annual_nominal_rate"])
    pmt = float(data["monthly_payment_twd"])
    first_due = parse_iso_date(data["due"]["first_due_date"])
    due_day = int(data["due"]["day_of_month"])

    if args.as_of:
        as_of = parse_iso_date(args.as_of)
    else:
        as_of = date.today()

    schedule = build_schedule_from_loan_dict(data, principal)
    total_interest = sum(r.interest for r in schedule)
    n_paid = count_payments_due_on_or_before(first_due, as_of)
    outstand, cum_int = outstanding_after_n_full_payments(principal, schedule, n_paid)
    term_m = int(data.get("term_months", 84))
    treat_u = float(data.get("rounding", {}).get("treat_under_twd_as_paid_after_term", 0))
    liab_nw, _ = liability_for_net_worth_twd(
        principal,
        schedule,
        n_paid,
        term_months=term_m,
        treat_under_twd=treat_u,
    )
    next_due = next_due_on_calendar_day(as_of, due_day)

    print("=== Loan summary ===")
    print(f"origin_date: {data['origin_date']}")
    print(f"amortization_basis: {data.get('amortization_basis')}")
    print(f"contract_principal_twd: {data['contract']['principal_twd']}")
    print(f"net_to_account_twd: {data['disbursement']['net_to_account_twd']}")
    print(f"annual_nominal_rate: {rate}")
    intr = data.get("interest", {})
    print(f"interest_method: {intr.get('method', 'daily_365')}  day_count_basis: {intr.get('day_count_basis', 365)}")
    print(f"term_months: {data.get('term_months', 84)}")
    print(f"monthly_payment_twd: {pmt}")
    print(f"first_due_date: {first_due.isoformat()}")
    print(f"lock_in_months: {data.get('lock_in_months')}")
    print()
    print("=== As-of position ===")
    print(f"as_of_date: {as_of.isoformat()}")
    print(f"payments_assumed_due_by_as_of: {n_paid}")
    print(f"outstanding_principal_twd (raw schedule): {outstand:,.2f}")
    print(f"liability_twd_for_net_worth: {liab_nw:,.2f}")
    print(f"cumulative_interest_through_payments_twd: {cum_int:,.2f}")
    print(f"total_interest_if_scheduled_to_zero_twd: {total_interest:,.2f}")
    if schedule:
        print(f"final_payoff_date: {schedule[-1].payment_date.isoformat()}")
        print(f"total_monthly_payments_count: {len(schedule)}")
        last_bal = schedule[-1].balance_end
        if last_bal > 0.5:
            print(
                f"schedule_end_balance_residual_twd: {last_bal:,.2f}  "
                f"(see loan.rounding.treat_under_twd_as_paid_after_term for net worth)"
            )
    print()
    print("=== Next due (reminder) ===")
    print(f"next_due_date: {next_due.isoformat()}")
    print(f"next_due_amount_twd: {pmt:,.2f}")
    print()
    print("=== Schedule (first N rows) ===")
    for row in schedule[: args.max_rows]:
        print(
            f"{row.index:4d}  {row.payment_date.isoformat()}  days={row.days:2d}  "
            f"pmt={row.payment:,.2f}  int={row.interest:,.2f}  "
            f"prin={row.principal:,.2f}  end_bal={row.balance_end:,.2f}"
        )
    if len(schedule) > args.max_rows:
        print(f"... ({len(schedule) - args.max_rows} more rows)")


if __name__ == "__main__":
    main()
