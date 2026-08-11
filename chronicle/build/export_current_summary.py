#!/usr/bin/env python3
"""Export a concise current summary markdown for human and AI handoff."""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from chronicle.build.paths import DATA_DIR, EXPORT_DIR, SITE_DATA_DIR  # noqa: E402

SNAPSHOT_PATH = SITE_DATA_DIR / "snapshot.json"
EXPORT_PATH = EXPORT_DIR / "current_summary.md"


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _load_json_optional(path: Path) -> dict:
    if not path.is_file():
        return {}
    return _load_json(path)


def _fmt_amount(value: float | int | None, digits: int = 2) -> str:
    if value is None:
        return "—"
    return f"{float(value):,.{digits}f}"


def _fmt_twd(value: float | int | None) -> str:
    return _fmt_amount(value, 0)


def _fmt_usd(value: float | int | None) -> str:
    return _fmt_amount(value, 2)


def _sum_currency(events: list[dict], field: str, source_kind: str | None = None) -> float:
    total = 0.0
    for event in events:
        if source_kind and event.get("source_kind") != source_kind:
            continue
        total += float(event.get(field) or 0)
    return total


def _active_months(events: list[dict]) -> list[str]:
    months = {
        str(event.get("date", ""))[:7]
        for event in events
        if isinstance(event.get("date"), str) and len(str(event.get("date"))) >= 7
    }
    return sorted(month for month in months if month)


def _timeline(capital_events: dict, trades: dict, fx: dict) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    for event in capital_events.get("events", []):
        when = str(event.get("occurred_at", event.get("date", "")))
        amount_twd = event.get("amount_twd")
        amount_usd = event.get("amount_usd")
        rows.append(
            (
                when,
                "Capital: "
                f"{event.get('event_type', 'unknown')} / "
                f"TWD {_fmt_twd(amount_twd) if amount_twd is not None else '—'} / "
                f"USD {_fmt_usd(amount_usd) if amount_usd is not None else '—'}",
            )
        )
    for trade in trades.get("trades", []):
        when = str(trade.get("executed_at", trade.get("date", "")))
        rows.append(
            (
                when,
                "Trade: "
                f"{trade.get('side', 'unknown')} {trade.get('symbol', '—')} / "
                f"{_fmt_amount(trade.get('units'), 4)} units / "
                f"USD {_fmt_usd(trade.get('total_usd'))}",
            )
        )
    for event in fx.get("events", []):
        when = str(event.get("date", ""))
        rows.append(
            (
                when,
                "FX: "
                f"TWD {_fmt_twd(event.get('twd_amount'))} -> "
                f"USD {_fmt_usd(event.get('usd_amount'))} @ {_fmt_amount(event.get('rate_twd_per_usd'), 4)}",
            )
        )
    return sorted(rows, key=lambda row: row[0], reverse=True)


def _position_lines(snapshot: dict) -> list[str]:
    lines: list[str] = []
    for row in snapshot.get("quotes", []):
        if row.get("benchmark") is True:
            continue
        units = float(row.get("units") or 0)
        last_usd = row.get("last_usd")
        listed = row.get("listed", True)
        if not listed:
            lines.append(f"- {row.get('symbol', '—')}: pending listing, {units:.4f} units")
            continue
        lines.append(
            f"- {row.get('symbol', '—')}: {units:.4f} units, last USD {_fmt_usd(last_usd)}"
        )
    return lines


def _intake_lines() -> list[str]:
    return [
        "- New trade: need executed_at, symbol, side, units, average price, total amount, fee.",
        "- Capital addition: need date, source kind, amount, currency, and whether it counts as strategy capital.",
        "- Cash snapshot: need as_of, bucket, currency, amount, and location.",
        "- Loan payment: need paid_at, total payment, principal, interest, and remaining balance if available.",
        "- Dividend: need symbol, ex_date or pay_date, gross, tax, net, and destination.",
        "- Rebalance action: need trigger reason, recommended action, executed action, and why they differ.",
    ]


def build_markdown() -> str:
    snapshot = _load_json(SNAPSHOT_PATH)
    capital_events = _load_json_optional(DATA_DIR / "capital_events.json")
    cash_buckets = _load_json_optional(DATA_DIR / "cash_buckets.json")
    rule_events = _load_json_optional(DATA_DIR / "rule_events.json")
    rebalance_log = _load_json_optional(DATA_DIR / "rebalance_log.json")
    income_events = _load_json_optional(DATA_DIR / "income_events.json")
    fx = _load_json_optional(DATA_DIR / "fx.json")
    trades = _load_json_optional(DATA_DIR / "trades.json")
    ledger_intent = _load_json_optional(DATA_DIR / "ledger_intent.json")

    capital_rows = capital_events.get("events", [])
    active_months = _active_months(capital_rows)
    active_month_count = max(len(active_months), 1)

    debt_twd = _sum_currency(capital_rows, "amount_twd", "debt")
    debt_usd = _sum_currency(capital_rows, "amount_usd", "debt")
    self_twd = _sum_currency(capital_rows, "amount_twd", "self_funded")
    self_usd = _sum_currency(capital_rows, "amount_usd", "self_funded")
    total_external_twd = _sum_currency(capital_rows, "amount_twd")
    total_external_usd = _sum_currency(capital_rows, "amount_usd")

    cash_snapshots = cash_buckets.get("snapshots", [])
    latest_cash_snapshot = cash_snapshots[-1] if cash_snapshots else None
    pending_followups = ledger_intent.get("pending_followups_zh", [])
    comparison_text = "unknown"
    if snapshot.get("investment_mv_twd") and snapshot.get("loan", {}).get("outstanding_twd"):
        debt = float(snapshot["loan"]["outstanding_twd"] or 0)
        market = float(snapshot.get("investment_mv_twd") or 0)
        comparison_text = "—" if debt <= 0 else f"{market / debt * 100:.2f}% market coverage"

    drawdown_cfg = snapshot.get("drawdown_reinvest", {})
    trigger_pct = float(drawdown_cfg.get("trigger_drawdown_from_peak_pct", 0) or 0) * 100

    sections: list[str] = []
    sections.append("# Current Summary")
    sections.append("")
    sections.append(f"- Generated on: {date.today().isoformat()}")
    sections.append(f"- Snapshot date: {snapshot.get('generated_at', '—')}")
    sections.append("- Purpose: portable summary for future AI review and handoff.")
    sections.append("")

    sections.append("## Current State")
    sections.append("")
    sections.append(
        f"- Net worth: TWD {_fmt_twd(snapshot.get('net_worth', {}).get('net_worth_twd'))}"
    )
    sections.append(
        f"- Market value: TWD {_fmt_twd(snapshot.get('investment_mv_twd'))} / "
        f"USD {_fmt_usd(snapshot.get('investment_mv_usd'))}"
    )
    sections.append(
        f"- Remaining liability: TWD {_fmt_twd(snapshot.get('loan', {}).get('outstanding_twd'))}"
    )
    sections.append(
        f"- NAV index: {_fmt_amount(snapshot.get('nav_summary', {}).get('nav_index_100'), 2)}"
    )
    sections.append(
        f"- Unrealized PnL: USD {_fmt_usd(snapshot.get('nav_summary', {}).get('unrealized_pnl_usd'))}"
    )
    sections.append(
        f"- Unrealized PnL in TWD view: TWD {_fmt_twd(snapshot.get('investment_cost', {}).get('unrealized_pnl_twd'))}"
    )
    sections.append(f"- Market vs debt: {comparison_text}")
    sections.append(
        f"- Next loan payment: {snapshot.get('loan', {}).get('next_due_date', '—')} / "
        f"TWD {_fmt_twd(snapshot.get('loan', {}).get('next_due_amount_twd'))}"
    )
    sections.append("")

    sections.append("## Capital Structure")
    sections.append("")
    sections.append(
        f"- External capital events: {len(capital_rows)} "
        f"(active months: {len(active_months) if active_months else 0})"
    )
    sections.append(
        f"- Debt-funded capital: TWD {_fmt_twd(debt_twd)} / USD {_fmt_usd(debt_usd)}"
    )
    sections.append(
        f"- Self-funded capital: TWD {_fmt_twd(self_twd)} / USD {_fmt_usd(self_usd)}"
    )
    sections.append(
        f"- Total external capital logged: TWD {_fmt_twd(total_external_twd)} / "
        f"USD {_fmt_usd(total_external_usd)}"
    )
    sections.append(
        f"- Average external contribution per active month: "
        f"TWD {_fmt_twd(total_external_twd / active_month_count)} / "
        f"USD {_fmt_usd(total_external_usd / active_month_count)}"
    )
    sections.append(
        f"- Deployed capital into positions: "
        f"USD {_fmt_usd(snapshot.get('nav_summary', {}).get('cumulative_invested_usd'))}"
    )
    sections.append(
        f"- TWD invested cost basis: "
        f"TWD {_fmt_twd(snapshot.get('investment_cost', {}).get('historical_cost_twd'))} "
        f"({snapshot.get('investment_cost', {}).get('twd_cost_method', 'unknown')})"
    )
    sections.append("")

    sections.append("## Holdings")
    sections.append("")
    sections.extend(_position_lines(snapshot))
    sections.append("")

    sections.append("## Rules And Risk")
    sections.append("")
    sections.append(
        f"- Rebalance band: ±{int(float(snapshot.get('allocations', {}).get('rebalance', {}).get('band_relative_to_target', 0) or 0) * 100)}% of target weight"
    )
    sections.append(f"- Drawdown add trigger: {trigger_pct:.0f}% below peak NAV")
    sections.append(
        f"- Peak NAV reference set: {'yes' if drawdown_cfg.get('peak_investment_value_twd') is not None else 'no'}"
    )
    sections.append(
        f"- Rule events logged: {len(rule_events.get('events', []))} / "
        f"Rebalance logs: {len(rebalance_log.get('entries', []))}"
    )
    sections.append(
        f"- Income events logged: {len(income_events.get('events', []))}"
    )
    sections.append("")

    sections.append("## Data Coverage")
    sections.append("")
    sections.append(f"- Trades logged: {snapshot.get('trade_ledger', {}).get('count', 0)}")
    sections.append(f"- FX events logged: {len(snapshot.get('fx_events', []))}")
    sections.append(f"- NAV history days: {snapshot.get('nav_history_days', 0)}")
    sections.append(
        f"- Cash snapshots logged: {len(cash_snapshots)}"
        + (
            f" (latest: {latest_cash_snapshot.get('as_of', '—')})"
            if latest_cash_snapshot
            else " (missing)"
        )
    )
    sections.append("")

    sections.append("## Missing Information")
    sections.append("")
    if pending_followups:
        sections.extend(f"- {row}" for row in pending_followups)
    else:
        sections.append("- No pending follow-up items recorded.")
    sections.append("")

    sections.append("## Intake Checklist For Next AI")
    sections.append("")
    sections.extend(_intake_lines())
    sections.append("")

    sections.append("## Timeline")
    sections.append("")
    timeline_rows = _timeline(capital_events, trades, fx)[:20]
    if timeline_rows:
        sections.extend(f"- {when}: {text}" for when, text in timeline_rows)
    else:
        sections.append("- No timeline items recorded.")
    sections.append("")

    sections.append("## Files Of Truth")
    sections.append("")
    sections.extend(
        [
            "- `chronicle/data/portfolio.json`: current holdings and valuation config.",
            "- `chronicle/data/trades.json`: executed trade log.",
            "- `chronicle/data/investment_flows.json`: deployed capital into positions.",
            "- `chronicle/data/capital_events.json`: full strategy funding ledger.",
            "- `chronicle/data/cash_buckets.json`: strategy cash snapshots.",
            "- `chronicle/data/rule_events.json`: trigger history.",
            "- `chronicle/data/rebalance_log.json`: recommended vs executed rebalance actions.",
            "- `chronicle/data/income_events.json`: dividends and income routing.",
            "- `chronicle/data/ledger_intent.json`: human-approved intent and pending follow-ups.",
        ]
    )
    sections.append("")
    return "\n".join(sections).rstrip() + "\n"


def main() -> None:
    markdown = build_markdown()
    EXPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_PATH.write_text(markdown, encoding="utf-8")
    print(f"wrote {EXPORT_PATH}")


if __name__ == "__main__":
    main()
