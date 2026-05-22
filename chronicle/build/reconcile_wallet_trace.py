#!/usr/bin/env python3
"""Print FX+trade wallet replay vs portfolio.cash_usd and FX rate sanity."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from chronicle.build.paths import DATA_DIR  # noqa: E402

_DATA = DATA_DIR


def trade_cash_delta(trade: dict) -> float:
    side = str(trade.get("side", "")).lower()
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


def fx_dt(event: dict) -> datetime:
    day = str(event.get("date", ""))[:10]
    tl = event.get("time_local")
    if tl:
        ts = str(tl)
        if ts.count(":") == 1:
            ts = f"{ts}:00"
        return datetime.fromisoformat(f"{day}T{ts}")
    return datetime.fromisoformat(f"{day}T00:00:00")


def trade_dt(trade: dict) -> datetime:
    raw = str(trade.get("executed_at", "")).strip().replace("Z", "+00:00")
    if "+" in raw:
        raw = raw.split("+")[0]
    if len(raw) >= 19:
        return datetime.fromisoformat(raw[:19])
    return datetime.fromisoformat(f'{raw[:10]}T12:00:00')


def main() -> None:
    port = json.loads((_DATA / "portfolio.json").read_text(encoding="utf-8"))
    fxj = json.loads((_DATA / "fx.json").read_text(encoding="utf-8"))
    trj = json.loads((_DATA / "trades.json").read_text(encoding="utf-8"))
    trades = trj.get("trades", [])
    events = fxj.get("events", [])
    anchor = float(port["cash_usd"])

    net_fx = sum(float(e.get("usd_amount", 0) or 0) for e in events)
    net_tr = sum(trade_cash_delta(t) for t in trades)

    timeline: list[tuple[str, str, datetime, float]] = []
    for e in events:
        eid = str(e.get("id", ""))
        timeline.append(("FX", eid, fx_dt(e), float(e.get("usd_amount", 0) or 0)))
    for t in trades:
        lab = f'{t.get("symbol")} {t.get("side")}'
        timeline.append(("TR", lab, trade_dt(t), trade_cash_delta(t)))
    timeline.sort(key=lambda row: row[2])

    print("=== Replay from wallet START = 0 USD (only fx.json + trades.json) ===\n")
    wallet = 0.0
    row_no = 0
    for kind, label, dt, dlt in timeline:
        row_no += 1
        wallet += dlt
        ts = dt.isoformat(sep=" ", timespec="seconds")
        print(f"{row_no:>3}  {kind}  {ts}  delta={dlt:>12.2f}  running={wallet:>12.2f}  {label}")

    implied_end = wallet
    gap = implied_end - anchor
    ledger_seed = anchor - net_fx - net_tr

    print("\n=== Totals ===")
    print(f"Sum FX usd_amount (wallet legs):     {net_fx:>14.2f}")
    print(f"Sum trade wallet deltas:             {net_tr:>14.2f}")
    print(f"Implied end if start 0:              {implied_end:>14.2f}")
    print(f"portfolio.cash_usd (anchor):         {anchor:>14.2f}")
    print(f"GAP (implied_end - anchor):          {gap:>14.2f}  USD")
    print(f"ledger_seed (= anchor - fx - tr):    {ledger_seed:>14.2f}  USD")

    print("\n=== FX: logged usd_amount vs twd/rate (positive legs only) ===\n")
    for e in events:
        eid = e.get("id")
        twd = float(e.get("twd_amount", 0) or 0)
        rate = float(e.get("rate_twd_per_usd", 0) or 0)
        usd_log = float(e.get("usd_amount", 0) or 0)
        direction = e.get("direction")
        if rate <= 0:
            print(f"{eid}  SKIP rate<=0")
            continue
        implied = twd / rate
        delta_usd = usd_log - implied
        print(f"{eid}  date={e.get('date')}  direction={direction or 'twd_to_usd'}")
        print(f"  twd_amount={twd:g}  rate={rate}  twd/rate={implied:.6f}")
        print(f"  logged usd_amount={usd_log}  (logged - twd/rate)={delta_usd:+.6f}")
        print()


if __name__ == "__main__":
    sys.exit(main() or 0)
