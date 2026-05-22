#!/usr/bin/env python3
"""Emit chronological FX + trades + ending holdings for manual audit (UTF-8)."""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from chronicle.build.paths import DATA_DIR, SITE_DATA_DIR  # noqa: E402

_DATA = DATA_DIR
_OUT_DEFAULT = DATA_DIR / "timeline_flow_audit.txt"
_NAV_HISTORY_PATH = DATA_DIR / "nav_history.json"
_SNAPSHOT_PATH = SITE_DATA_DIR / "snapshot.json"


def _format_rate_twd_per_usd(rate: object | None) -> str | None:
    """Pretty rate for human-readable audit lines (avoids raw float junk)."""
    if rate is None:
        return None
    try:
        val = float(rate)
    except (TypeError, ValueError):
        return None
    if val <= 0:
        return None
    s = f"{val:.6f}".rstrip("0").rstrip(".")
    return s or None


def _infer_rate_implied(stored: str | None, twd_amt: float, usd_abs: float) -> str | None:
    """Use TWD per USD derived from notionals when canonical rate missing."""
    if stored:
        return stored
    usd_pay = abs(usd_abs)
    if twd_amt > 0 and usd_pay > 1e-9:
        return _format_rate_twd_per_usd(twd_amt / usd_pay)
    return None


def _fx_intro_lines(event: dict) -> tuple[list[str], float]:
    """Build title + detail lines and wallet usd delta for one fx event."""
    usd = float(event.get("usd_amount", 0) or 0)
    twd = float(event.get("twd_amount", 0) or 0)
    rate_raw = event.get("rate_twd_per_usd")
    rate_fmt = _format_rate_twd_per_usd(rate_raw)
    direction = event.get("direction")
    eid = str(event.get("id", "") or "")
    stored_or_implied = _infer_rate_implied(rate_fmt, twd, abs(usd) if direction == "usd_to_twd" else usd)

    if direction == "usd_to_twd":
        rate_show = stored_or_implied or "無牌告紀錄"
        title = f"換匯（美金換台幣）｜{eid}"
        detail = (
            f"  付出約美金 {abs(usd):,.2f} USD → 進帳台幣 {twd:,.2f} TWD（牌告約 {rate_show}）"
        )
        return [title, detail], usd

    # Ledger-only USD bump (no TWD leg) — not a TWD<->USD quote event
    if twd <= 1e-9 and usd > 0 and rate_raw in (None, "", 0, 0.0):
        title = f"錢包入帳 USD（非換匯）｜{eid}"
        note = str(event.get("note_en", "") or "").strip()
        detail = f"  進帳美金 {usd:,.2f} USD"
        if note:
            detail += f"（{note}）"
        return [title, detail], usd

    rate_show = stored_or_implied or "無牌告紀錄"
    title = f"換匯（台幣換美金）｜{eid}"
    detail = f"  付出台幣 {twd:,.2f} TWD（牌告約 {rate_show}）→ 進帳美金 {usd:,.2f} USD"
    return [title, detail], usd


def _append_nav_spy_audit(lines_out: list[str]) -> None:
    """Append NAV vs SPY shadow return summary from nav_history.json (chart basis)."""
    lines_out.append("=== NAV 與 SPY 影子對照（nav_history.json，與儀表板棕線一致）===")
    path = _NAV_HISTORY_PATH
    if not path.is_file():
        lines_out.append("（略過：找不到 nav_history.json，可先執行 build_dashboard_data）")
        lines_out.append("")
        return
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        lines_out.append("（略過：nav_history.json 結構異常）")
        lines_out.append("")
        return
    rows_u = []
    for r in raw:
        if not isinstance(r, dict):
            continue
        nav_i = r.get("nav_index")
        spy_i = r.get("spy_shadow_index")
        if nav_i is None or spy_i is None:
            continue
        mv_raw = r.get("position_mv_usd")
        mv_val: float | None
        try:
            mv_val = float(mv_raw) if mv_raw is not None else None
        except (TypeError, ValueError):
            mv_val = None
        rows_u.append(
            {
                "date": str(r.get("date", "")),
                "nav_index": float(nav_i),
                "spy_index": float(spy_i),
                "position_mv_usd": mv_val,
            }
        )
    if len(rows_u) < 2:
        lines_out.append("（資料不足：需至少兩個含 nav_index / spy_shadow_index 的列）")
        lines_out.append("")
        return

    head, tail = rows_u[0], rows_u[-1]
    nav_a, nav_b = head["nav_index"], tail["nav_index"]
    spy_a, spy_b = head["spy_index"], tail["spy_index"]
    nav_pct = (nav_b / nav_a - 1.0) * 100.0 if nav_a > 1e-9 else float("nan")
    spy_pct = (spy_b / spy_a - 1.0) * 100.0 if spy_a > 1e-9 else float("nan")
    excess = (
        nav_pct - spy_pct
        if nav_pct == nav_pct and spy_pct == spy_pct
        else float("nan")
    )

    lines_out.append(
        f"區間起始（列）：{head['date']}  NAV={nav_a:.4f}  SPY影子={spy_a:.4f}"
    )
    lines_out.append(
        f"區間末尾（列）：{tail['date']}  NAV={nav_b:.4f}  SPY影子={spy_b:.4f}"
    )
    if nav_pct == nav_pct:
        lines_out.append(f"區間內 NAV 總報酬（指數比值）：{nav_pct:+.2f}%")
    if spy_pct == spy_pct:
        lines_out.append(f"同期 SPY 影子總報酬（指數比值）：{spy_pct:+.2f}%")
    if excess == excess:
        lines_out.append(f"相對 SPY 影子（超額）：{excess:+.2f} 個百分點")

    prev_row, last_row = rows_u[-2], rows_u[-1]
    pn, sn = prev_row["nav_index"], prev_row["spy_index"]
    ln, ls = last_row["nav_index"], last_row["spy_index"]
    nav_1d = (ln / pn - 1.0) * 100.0 if pn > 1e-9 else float("nan")
    spy_1d = (ls / sn - 1.0) * 100.0 if sn > 1e-9 else float("nan")
    xs_1d = (
        nav_1d - spy_1d
        if nav_1d == nav_1d and spy_1d == spy_1d
        else float("nan")
    )

    lines_out.append("--- 與前一個交易日比較（nav_history 序列中，最末列 vs 倒數第二列）---")
    lines_out.append(f"前一列日期：{prev_row['date']}  NAV={pn:.4f}  SPY影子={sn:.4f}")
    lines_out.append(f"最新列日期：{last_row['date']}  NAV={ln:.4f}  SPY影子={ls:.4f}")
    if nav_1d == nav_1d:
        lines_out.append(f"NAV 單日變動（指數）：{nav_1d:+.2f}%")
    if spy_1d == spy_1d:
        lines_out.append(f"SPY 影子單日變動（指數）：{spy_1d:+.2f}%")
    if xs_1d == xs_1d:
        lines_out.append(f"相對 SPY 影子（單日超額）：{xs_1d:+.2f} 個百分點")

    pmv = prev_row.get("position_mv_usd")
    lmv = last_row.get("position_mv_usd")
    if pmv is not None and lmv is not None:
        try:
            pmv_f = float(pmv)
            lmv_f = float(lmv)
        except (TypeError, ValueError):
            pmv_f = lmv_f = None
        if pmv_f is not None and lmv_f is not None and pmv_f > 1e-9:
            mv_d = lmv_f - pmv_f
            mv_pct = (lmv_f / pmv_f - 1.0) * 100.0
            lines_out.append(
                f"權益持股市值 position_mv_usd：{pmv_f:,.2f} -> {lmv_f:,.2f} USD"
                f"（變動 {mv_d:+,.2f}，{mv_pct:+.2f}%）"
            )

    lines_out.append(
        "說明：綠線=NAV 單位淨值（僅權益持股市值）；棕線=SPY 影子（跟你的股票買賣名目）。"
        "閒置 USD、BOXX 不進 NAV 分子；換匯不動單位；僅股票買賣調整單位。"
    )
    lines_out.append(
        "單日比較：若同一曆日有多筆列（例如盤中補點），「前一個交易日」指時間序列的上一筆，未必等於曆日的前一天。"
    )
    lines_out.append("")


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


@dataclass(frozen=True)
class Row:
    sort_key: datetime
    kind: str
    lines: list[str]
    wallet_delta: float


def main() -> int:
    port = json.loads((_DATA / "portfolio.json").read_text(encoding="utf-8"))
    fxj = json.loads((_DATA / "fx.json").read_text(encoding="utf-8"))
    trj = json.loads((_DATA / "trades.json").read_text(encoding="utf-8"))
    trades = trj.get("trades", [])
    shadow_by_executed_at: dict[str, dict] = {}
    if _SNAPSHOT_PATH.is_file():
        try:
            snap = json.loads(_SNAPSHOT_PATH.read_text(encoding="utf-8"))
            for row in (snap.get("trade_ledger") or {}).get("trades") or []:
                at = str(row.get("executed_at", "") or "")
                fills = row.get("shadow_benchmark_fills")
                if at and fills:
                    shadow_by_executed_at[at] = fills
        except (OSError, json.JSONDecodeError):
            pass
    if shadow_by_executed_at:
        merged_trades: list[dict] = []
        for row in trades:
            copy = dict(row)
            at = str(row.get("executed_at", "") or "")
            if at in shadow_by_executed_at:
                copy["shadow_benchmark_fills"] = shadow_by_executed_at[at]
            merged_trades.append(copy)
        trades = merged_trades
    events = fxj.get("events", [])
    anchor = float(port["cash_usd"])

    rows: list[Row] = []

    for e in events:
        dt = fx_dt(e)
        intro, usd = _fx_intro_lines(e)
        lines = [
            *intro,
            f"  錢包 USD 變化：{'+' if usd >= 0 else ''}{usd:,.2f} USD",
        ]
        rows.append(Row(dt, "FX", lines, usd))

    for t in trades:
        dt = trade_dt(t)
        sym = t.get("symbol", "")
        side = str(t.get("side", "")).lower()
        units = float(t.get("units", 0) or 0)
        px = float(t.get("price_usd", 0) or 0)
        total = float(t.get("total_usd", 0) or 0)
        fee = float(t.get("fee_usd", 0) or 0)
        other = float(t.get("other_fees_usd", 0) or 0)
        dlt = trade_cash_delta(t)
        side_zh = "買入" if side == "buy" else "賣出" if side == "sell" else side
        if side == "buy":
            cash_note = f"錢包扣款（本金+費用）約 {-dlt:,.2f} USD（principal {total:,.2f} + fee {fee:,.2f}"
            if other:
                cash_note += f" + other {other:,.2f}"
            cash_note += "）"
        else:
            cash_note = (
                f"錢包入帳（毛額-費用）約 {dlt:,.2f} USD（gross {total:,.2f} - fee {fee:,.2f}"
            )
            if other:
                cash_note += f" - other {other:,.2f}"
            cash_note += "）"
        lines = [
            f"成交｜{sym} {side_zh}",
            f"  時間（紀錄）：{t.get('executed_at')}",
            f"  數量 {units:g} @ {px:.6g} USD；名目 principal（total_usd）{total:,.2f} USD",
            f"  {cash_note}",
            f"  錢包 USD 變化：{'+' if dlt >= 0 else ''}{dlt:,.2f} USD",
        ]
        shadow_fills = t.get("shadow_benchmark_fills") or {}
        for bench_ticker in ("SPY", "SSO"):
            fill = shadow_fills.get(bench_ticker)
            if not fill:
                continue
            src = fill.get("source", "")
            bar_at = fill.get("bar_at")
            interval = fill.get("interval")
            px_b = fill.get("price_usd")
            bar_note = f"；K 線 {bar_at}" if bar_at else ""
            interval_note = f"（{interval}）" if interval else ""
            lines.append(
                f"  影子 {bench_ticker} 參考價 {px_b} USD [{src}]{interval_note}{bar_note}"
            )
        rows.append(Row(dt, "TR", lines, dlt))

    rows.sort(key=lambda r: r.sort_key)

    lines_out: list[str] = []
    lines_out.append("=== 個人帳本：依時間排序完整流程（換匯 + 成交）===")
    lines_out.append("")
    lines_out.append(
        "說明：錢包欄位是「若期初 USD 現金 = 0」，只靠 fx.json + trades.json 推移的模擬餘額。"
    )
    if shadow_by_executed_at:
        lines_out.append(
            "影子 SPY/SSO 參考價：成交 executed_at（視為 Asia/Taipei）對齊美東 1m/5m K 線；"
            "請先執行 build_dashboard_data.py 產生 snapshot。"
        )
    lines_out.append("")

    wallet = 0.0
    for i, row in enumerate(rows, 1):
        ts = row.sort_key.isoformat(sep=" ", timespec="seconds")
        lines_out.append(f"── 第 {i} 步 [{row.kind}] {ts} ──")
        lines_out.extend(row.lines)
        wallet += row.wallet_delta
        lines_out.append(f"  => 累計錢包 USD（期初=0）：{wallet:,.2f}")
        lines_out.append("")

    net_fx = sum(float(e.get("usd_amount", 0) or 0) for e in events)
    net_tr = sum(trade_cash_delta(t) for t in trades)
    implied = net_fx + net_tr
    gap = implied - anchor

    lines_out.append("=== 尾段核對 ===")
    lines_out.append(f"換匯 usd_amount 淨加總：{net_fx:,.2f} USD")
    lines_out.append(f"成交對錢包淨加總：{net_tr:,.2f} USD")
    lines_out.append(f"期初假設 0 → 推算期末錢包：{implied:,.2f} USD")
    lines_out.append(f"portfolio.cash_usd（你填的）：{anchor:,.2f} USD")
    lines_out.append(f"差距（推算 - 你填的）：{gap:+,.2f} USD")
    lines_out.append("")

    lines_out.append("=== 目前 portfolio.json 持倉（units）與美金餘額 ===")
    lines_out.append(f"現金 USD（broker）：{anchor:,.2f}")
    for p in port.get("positions", []):
        sym = p.get("symbol", "")
        listed = p.get("listed", True)
        units = float(p.get("units", 0) or 0)
        note = p.get("note") or ""
        flag = "" if listed is not False else "（未上市標記）"
        lines_out.append(f"  {sym}{flag}：{units:g} 單位{cost_line(p)}{note_suffix(note)}")
    lines_out.append("")

    _append_nav_spy_audit(lines_out)

    text = "\n".join(lines_out)
    _OUT_DEFAULT.parent.mkdir(parents=True, exist_ok=True)
    _OUT_DEFAULT.write_text(text, encoding="utf-8")
    if getattr(sys.stdout, "reconfigure", None):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass
    print(text)
    print(f"\n（已另存）{_OUT_DEFAULT}", file=sys.stderr)
    return 0


def cost_line(p: dict) -> str:
    cb = p.get("cost_basis_usd")
    if cb is None:
        return ""
    return f"；成本基準 cost_basis_usd ≈ {float(cb):,.2f} USD"


def note_suffix(note: object) -> str:
    if not note:
        return ""
    return f"  # {note}"


if __name__ == "__main__":
    raise SystemExit(main())
