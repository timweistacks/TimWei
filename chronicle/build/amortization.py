"""Loan amortization: daily interest (annual/365 * days per period), fixed payment."""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterator


@dataclass(frozen=True)
class ScheduleRow:
    balance_end: float
    days: int
    index: int
    interest: float
    payment: float
    payment_date: date
    period_start: date
    principal: float


def add_months(d: date, months: int) -> date:
    m0 = d.month - 1 + months
    y = d.year + m0 // 12
    m = m0 % 12 + 1
    last = calendar.monthrange(y, m)[1]
    return date(y, m, min(d.day, last))


def _interest_amount_daily_365(
    balance: float, annual_nominal_rate: float, days: int
) -> int:
    raw = balance * (annual_nominal_rate / 365.0) * float(days)
    return int(round(raw))


def build_schedule(
    principal: float,
    annual_nominal_rate: float,
    monthly_payment: float,
    origin_date: date,
    first_payment_date: date,
    *,
    term_months: int = 84,
) -> list[ScheduleRow]:
    """
    Equal payment schedule with interest = balance * (rate/365) * days in period.
    Period 1: days from origin_date to first_payment_date.
    Later periods: days from previous payment_date to current payment_date.
    Interest rounded to integer TWD; principal = payment - interest; last period may pay less than full PMT.
    """
    if principal <= 0:
        raise ValueError("principal must be positive")
    if monthly_payment <= 0:
        raise ValueError("monthly_payment must be positive")
    if term_months < 1:
        raise ValueError("term_months must be positive")

    rows: list[ScheduleRow] = []
    balance = int(round(principal))
    pmt = int(round(monthly_payment))
    prev = origin_date

    for i in range(1, term_months + 1):
        if balance <= 0:
            break
        pay_date = add_months(first_payment_date, i - 1)
        days = (pay_date - prev).days
        if days <= 0:
            raise ValueError("non-positive days in period; check dates")

        interest_amt = _interest_amount_daily_365(balance, annual_nominal_rate, days)
        planned_principal = pmt - interest_amt
        if planned_principal < 0:
            raise ValueError(
                "monthly_payment does not cover interest; check rate, payment, or dates"
            )
        principal_part = min(planned_principal, balance)
        actual_payment = float(principal_part + interest_amt)

        new_balance = balance - principal_part
        rows.append(
            ScheduleRow(
                index=i,
                period_start=prev,
                payment_date=pay_date,
                days=days,
                payment=actual_payment,
                interest=float(interest_amt),
                principal=float(principal_part),
                balance_end=float(max(new_balance, 0)),
            )
        )
        balance = new_balance
        prev = pay_date

    return rows


def parse_iso_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def count_payments_due_on_or_before(first_due: date, as_of: date) -> int:
    if as_of < first_due:
        return 0
    n = 0
    d = first_due
    while d <= as_of:
        n += 1
        d = add_months(first_due, n)
    return n


def outstanding_after_n_full_payments(
    principal: float, schedule: list[ScheduleRow], n: int
) -> tuple[float, float]:
    """Returns (outstanding_balance, cumulative_interest_paid) after n full payments."""
    if n <= 0:
        return principal, 0.0
    if not schedule:
        return principal, 0.0
    k = min(n, len(schedule))
    cum_interest = sum(r.interest for r in schedule[:k])
    return schedule[k - 1].balance_end, cum_interest


def liability_for_net_worth_twd(
    principal: float,
    schedule: list[ScheduleRow],
    n_paid: int,
    *,
    term_months: int,
    treat_under_twd: float,
) -> tuple[float, float]:
    """
    Outstanding for liability side of net worth.
    After n_paid >= term_months, if raw balance_end is under treat_under_twd, returns 0.
    """
    raw, cum_int = outstanding_after_n_full_payments(principal, schedule, n_paid)
    if n_paid >= term_months and raw >= 0 and raw < treat_under_twd:
        return 0.0, cum_int
    return raw, cum_int


def next_due_on_calendar_day(as_of: date, day_of_month: int) -> date:
    y, m = as_of.year, as_of.month
    last = calendar.monthrange(y, m)[1]
    d = min(day_of_month, last)
    this_due = date(y, m, d)
    if as_of <= this_due:
        return this_due
    return add_months(this_due, 1)


def iter_schedule_rows(schedule: list[ScheduleRow]) -> Iterator[ScheduleRow]:
    yield from schedule


def build_schedule_from_loan_dict(data: dict, principal: float) -> list[ScheduleRow]:
    """Build schedule using loan.json fields (origin_date, due.first_due_date, term_months)."""
    origin = parse_iso_date(data["origin_date"])
    first_due = parse_iso_date(data["due"]["first_due_date"])
    rate = float(data["annual_nominal_rate"])
    pmt = float(data["monthly_payment_twd"])
    term = int(data.get("term_months", 84))
    return build_schedule(
        principal,
        rate,
        pmt,
        origin,
        first_due,
        term_months=term,
    )


__all__ = [
    "ScheduleRow",
    "add_months",
    "build_schedule",
    "build_schedule_from_loan_dict",
    "count_payments_due_on_or_before",
    "liability_for_net_worth_twd",
    "next_due_on_calendar_day",
    "outstanding_after_n_full_payments",
    "parse_iso_date",
]
