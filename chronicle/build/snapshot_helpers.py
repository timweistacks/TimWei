"""Helpers for dashboard snapshot: loan schedule JSON, USD/TWD from Yahoo."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from chronicle.build.amortization import ScheduleRow


def schedule_to_jsonable(schedule: list[ScheduleRow]) -> list[dict[str, Any]]:
    """Serialize amortization schedule rows for snapshot.json / web tables."""
    out: list[dict[str, Any]] = []
    for r in schedule:
        out.append(
            {
                "balance_after_twd": round(r.balance_end, 2),
                "days": r.days,
                "interest_twd": round(r.interest, 2),
                "payment_date": r.payment_date.isoformat(),
                "payment_twd": round(r.payment, 2),
                "period": r.index,
                "period_start": r.period_start.isoformat(),
                "principal_twd": round(r.principal, 2),
            }
        )
    return out
