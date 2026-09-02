"""Active allocation phase and current vs target sleeve weights (for dashboard)."""

from __future__ import annotations

from datetime import date
from typing import Any

from chronicle.build.amortization import parse_iso_date


def _maybe_buy_fee_rules(rebalance_cfg: dict[str, Any]) -> dict[str, Any] | None:
    fee = rebalance_cfg.get("broker_fee_usd_per_trade")
    pct_trade = rebalance_cfg.get("max_trade_fee_as_pct_of_notional")
    pct_buy = rebalance_cfg.get("max_buy_fee_as_pct_of_notional")
    pct = pct_trade if pct_trade is not None else pct_buy
    if fee is None or pct is None:
        return None
    pct_f = float(pct)
    out: dict[str, Any] = {
        "broker_fee_usd_per_trade": float(fee),
        "max_buy_fee_as_pct_of_notional": pct_f,
        "max_trade_fee_as_pct_of_notional": pct_f,
    }
    ps = rebalance_cfg.get("buy_fee_priority_symbols")
    if isinstance(ps, list):
        out["buy_fee_priority_symbols"] = [
            str(x).strip() for x in ps if str(x).strip()
        ]
    pri = rebalance_cfg.get("buy_fee_min_notional_multiplier_priority")
    oth = rebalance_cfg.get("buy_fee_min_notional_multiplier_other")
    dfl = rebalance_cfg.get("buy_fee_min_notional_multiplier_default")
    fl = rebalance_cfg.get("buy_min_notional_usd_floor")
    if pri is not None:
        out["buy_fee_min_notional_multiplier_priority"] = float(pri)
    if oth is not None:
        out["buy_fee_min_notional_multiplier_other"] = float(oth)
    if dfl is not None:
        out["buy_fee_min_notional_multiplier_default"] = float(dfl)
    if fl is not None:
        out["buy_min_notional_usd_floor"] = float(fl)
    return out


def _min_buy_notional_usd_for_fee(symbol: str, rules: dict[str, Any]) -> float:
    fee = float(rules["broker_fee_usd_per_trade"])
    pct = float(rules.get("max_trade_fee_as_pct_of_notional") or rules["max_buy_fee_as_pct_of_notional"])
    base = fee / pct
    priority_syms = frozenset(rules.get("buy_fee_priority_symbols") or [])
    if priority_syms:
        if symbol in priority_syms:
            mult = float(rules.get("buy_fee_min_notional_multiplier_priority", 0.85))
        else:
            mult = float(rules.get("buy_fee_min_notional_multiplier_other", 1.15))
    else:
        mult = float(rules.get("buy_fee_min_notional_multiplier_default", 1.0))
    floor_u = rules.get("buy_min_notional_usd_floor")
    raw = base * mult
    if floor_u is not None:
        raw = max(raw, float(floor_u))
    return raw


def active_phase(phases: list[dict], as_of: date) -> dict[str, Any] | None:
    """Pick the phase whose [effective_from, effective_to] contains as_of."""
    candidates: list[tuple[date, dict]] = []
    for ph in phases:
        ef = ph.get("effective_from")
        if not ef:
            continue
        fd = parse_iso_date(ef) if isinstance(ef, str) else ef
        et = ph.get("effective_to")
        td = parse_iso_date(et) if et else None
        if as_of < fd:
            continue
        if td is not None and as_of > td:
            continue
        candidates.append((fd, ph))
    if not candidates:
        return None
    candidates.sort(key=lambda x: x[0], reverse=True)
    return candidates[0][1]


def sleeve_rows(
    pos_rows: list[dict],
    series_map: dict,
    usd_twd: float | None,
    targets: list[dict],
    band: float,
    cash_usd_in_denominator: float | None = None,
    deploy_all_cash_usd: bool = False,
    exact_target_min_trade_usd: float = 5.0,
    buy_fee_rules: dict[str, Any] | None = None,
    cash_like_symbols: frozenset[str] | None = None,
    cash_target_symbol: str | None = None,
) -> tuple[list[dict[str, Any]], dict[str, float | None]]:
    """
    Current weight vs target for each symbol in targets.

    Denominator (for current_pct and target_mv_usd) is either:
    - sum of MV of target symbols only (cash_usd_in_denominator is None), or
    - that sum plus broker USD cash (when cash_usd_in_denominator is set).

    When cash_target_symbol is set, broker USD cash is shown in that explicit
    cash target row. It is kept separate from cash-like ETFs such as BOXX.

    When deploy_all_cash_usd is True, sleeve status uses exact target MV deltas
    (skip band) so recommendations deploy idle USD cash into sleeves.

    When buy_fee_rules is set, each intended trade (buy or sell) is checked:
    if broker_fee_usd_per_trade / abs(delta_mv_usd) exceeds max_trade_fee_as_pct_of_notional,
    the row is fee_suppressed (no trade text; drift status may still be low/high).
    Otherwise buys below min notional become defer_fee_buy. Sells use the same fee cap.
    """
    mv_by_symbol: dict[str, float] = {}
    units_by_symbol: dict[str, float] = {}
    last_usd_by_symbol: dict[str, float | None] = {}
    last_twd_by_symbol: dict[str, float | None] = {}
    listed_by_symbol: dict[str, bool] = {}
    ticker_by_symbol: dict[str, str | None] = {}
    for pr in pos_rows:
        sym = pr["symbol"]
        tkr = pr.get("yahoo_ticker")
        units = float(pr.get("units", 0))
        units_by_symbol[sym] = units
        listed_by_symbol[sym] = pr.get("listed") is not False
        ticker_by_symbol[sym] = tkr
        if pr.get("listed") is False or not tkr:
            mv_by_symbol[sym] = 0.0
            last_usd_by_symbol[sym] = None
            last_twd_by_symbol[sym] = None
            continue
        s = series_map.get(tkr)
        if s is None or s.empty:
            mv_by_symbol[sym] = 0.0
            last_usd_by_symbol[sym] = None
            last_twd_by_symbol[sym] = None
        else:
            last_usd = float(s.iloc[-1])
            mv_by_symbol[sym] = units * last_usd
            last_usd_by_symbol[sym] = last_usd
            last_twd_by_symbol[sym] = (
                round(last_usd * float(usd_twd), 2) if usd_twd is not None else None
            )

    cash_den = (
        max(0.0, float(cash_usd_in_denominator))
        if cash_usd_in_denominator is not None
        else 0.0
    )
    cash_symbol = str(cash_target_symbol or "").strip()
    positions_mv_total = sum(mv_by_symbol.get(t["symbol"], 0.0) for t in targets)
    denominator_usd = (
        positions_mv_total + cash_den
        if cash_usd_in_denominator is not None
        else positions_mv_total
    )
    denom_meta: dict[str, float | None] = {
        "cash_usd_applied": (
            cash_den if cash_usd_in_denominator is not None else None
        ),
        "denominator_usd": denominator_usd,
        "positions_mv_usd": positions_mv_total,
    }

    out: list[dict[str, Any]] = []
    eps_mv = max(0.0, float(exact_target_min_trade_usd))
    for t in targets:
        sym = t["symbol"]
        tgt = float(t["weight"])
        mv = mv_by_symbol.get(sym, 0.0)
        is_cash_target = sym == cash_symbol and cash_usd_in_denominator is not None
        if is_cash_target:
            mv = cash_den
        units = units_by_symbol.get(sym, 0.0)
        last_usd = last_usd_by_symbol.get(sym)
        last_twd = last_twd_by_symbol.get(sym)
        tgt_pct = tgt * 100.0
        lo = tgt_pct * (1.0 - band)
        hi = tgt_pct * (1.0 + band)
        cur_pct = 0.0
        st = "pending"
        target_mv_usd = None
        target_mv_twd = None
        delta_mv_usd = None
        delta_mv_twd = None
        if denominator_usd > 1e-12:
            cur_pct = (mv / denominator_usd) * 100.0
            target_mv_usd = round(denominator_usd * tgt, 4)
            delta_mv_usd = round(target_mv_usd - mv, 4)
            target_mv_twd = (
                round(target_mv_usd * float(usd_twd), 2)
                if usd_twd is not None
                else None
            )
            delta_mv_twd = (
                round(delta_mv_usd * float(usd_twd), 2)
                if usd_twd is not None
                else None
            )
            if deploy_all_cash_usd:
                if abs(delta_mv_usd) <= eps_mv:
                    st = "ok"
                elif delta_mv_usd > eps_mv:
                    st = "low"
                else:
                    st = "high"
            else:
                if cur_pct < lo - 1e-6:
                    st = "low"
                elif cur_pct > hi + 1e-6:
                    st = "high"
                else:
                    st = "ok"
        mv_twd = round(mv * float(usd_twd), 2) if usd_twd is not None else None
        trade_units = None
        trade_side = "hold"
        recommendation_mode = "await_first_buy"
        row_fee_pct: float | None = None
        if denominator_usd > 1e-12:
            if is_cash_target:
                # Broker USD cash has no quote or share count to trade here;
                # the row only reports whether the cash target is in band.
                recommendation_mode = "in_band" if st == "ok" else "cash_target_drift"
            elif last_usd is None or last_usd <= 0:
                recommendation_mode = "missing_quote"
                trade_side = "unknown"
            elif st == "ok":
                recommendation_mode = "in_band"
            elif delta_mv_usd is not None:
                trade_units = round(abs(delta_mv_usd) / last_usd, 4)
                trade_side = "buy" if delta_mv_usd > 0 else "sell"
                recommendation_mode = "rebalance"
                if buy_fee_rules is not None and abs(float(delta_mv_usd)) > 1e-12:
                    fee_u = float(buy_fee_rules["broker_fee_usd_per_trade"])
                    max_frac = float(
                        buy_fee_rules.get("max_trade_fee_as_pct_of_notional")
                        or buy_fee_rules["max_buy_fee_as_pct_of_notional"]
                    )
                    notional_abs = abs(float(delta_mv_usd))
                    fee_ratio = fee_u / notional_abs if notional_abs > 1e-12 else 0.0
                    if fee_ratio > max_frac + 1e-15:
                        trade_units = None
                        trade_side = "hold"
                        recommendation_mode = "fee_suppressed"
                        row_fee_pct = round(100.0 * fee_ratio, 4)
                    elif trade_side == "buy":
                        min_buy = _min_buy_notional_usd_for_fee(sym, buy_fee_rules)
                        if delta_mv_usd < min_buy:
                            trade_units = None
                            trade_side = "hold"
                            recommendation_mode = "defer_fee_buy"
                            st = "low_fee_deferred"
                            row_fee_pct = round(100.0 * fee_u / delta_mv_usd, 4)
                        else:
                            row_fee_pct = round(100.0 * fee_u / delta_mv_usd, 4)
                    else:
                        row_fee_pct = round(100.0 * fee_ratio, 4)
            else:
                row_fee_pct = None
        else:
            row_fee_pct = None
        fee_meta: dict[str, Any] = {}
        if recommendation_mode == "defer_fee_buy" and buy_fee_rules is not None:
            fee_meta["buy_fee_min_notional_usd"] = round(
                _min_buy_notional_usd_for_fee(sym, buy_fee_rules), 2
            )
            fee_meta["buy_fee_pct_if_traded"] = row_fee_pct
        elif (
            recommendation_mode == "rebalance"
            and trade_side == "buy"
            and row_fee_pct is not None
        ):
            fee_meta["buy_fee_pct_if_traded"] = row_fee_pct
        elif (
            recommendation_mode == "rebalance"
            and trade_side == "sell"
            and row_fee_pct is not None
        ):
            fee_meta["buy_fee_pct_if_traded"] = row_fee_pct
        out.append(
            {
                "band_high_pct": round(hi, 2),
                "band_low_pct": round(lo, 2),
                "buy_fee_min_notional_usd": fee_meta.get("buy_fee_min_notional_usd"),
                "buy_fee_pct_if_traded": fee_meta.get("buy_fee_pct_if_traded"),
                "current_pct": round(cur_pct, 2),
                "current_units": round(units, 4),
                "delta_mv_twd": delta_mv_twd,
                "delta_mv_usd": delta_mv_usd,
                "last_twd": last_twd,
                "last_usd": round(last_usd, 4) if last_usd is not None else None,
                "listed": listed_by_symbol.get(sym, True),
                "mv_twd": mv_twd,
                "mv_usd": round(mv, 4),
                "recommendation_mode": recommendation_mode,
                "target_mv_twd": target_mv_twd,
                "target_mv_usd": target_mv_usd,
                "status": st,
                "symbol": sym,
                "trade_side": trade_side,
                "trade_units": trade_units,
                "target_pct": round(tgt_pct, 2),
                "yahoo_ticker": ticker_by_symbol.get(sym),
            }
        )
    return out, denom_meta


def build_portfolio_view(
    alloc: dict,
    pos_rows: list[dict],
    series_map: dict,
    usd_twd: float | None,
    as_of: date,
    inv_mv_twd: float | None,
    inv_mv_usd: float,
    rebalance_cash_usd: float | None = None,
    deploy_all_cash_usd: bool = False,
    exact_target_min_trade_usd: float = 5.0,
    cash_like_symbols: frozenset[str] | None = None,
    cash_target_symbol: str | None = None,
) -> dict[str, Any]:
    phases = alloc.get("phases", [])
    reb_all = alloc.get("rebalance") or {}
    band = float(reb_all.get("band_relative_to_target", 0.2))
    buy_fee_rules = _maybe_buy_fee_rules(reb_all)
    phase = active_phase(phases, as_of)
    if not phase:
        return {
            "as_of": as_of.isoformat(),
            "phase": None,
            "rebalance_needed": False,
            "sleeves": [],
            "total_mv_twd": inv_mv_twd,
            "total_mv_usd": round(inv_mv_usd, 4),
        }
    targets = phase.get("targets", [])
    sleeves, denom_meta = sleeve_rows(
        pos_rows,
        series_map,
        usd_twd,
        targets,
        band,
        rebalance_cash_usd,
        deploy_all_cash_usd,
        exact_target_min_trade_usd,
        buy_fee_rules,
        cash_like_symbols,
        cash_target_symbol,
    )
    need = any(s.get("recommendation_mode") == "rebalance" for s in sleeves)
    deferred_buy_actions = [
        {
            "buy_fee_min_notional_usd": s.get("buy_fee_min_notional_usd"),
            "buy_fee_pct_if_traded": s.get("buy_fee_pct_if_traded"),
            "delta_mv_twd": s.get("delta_mv_twd"),
            "delta_mv_usd": s.get("delta_mv_usd"),
            "symbol": s["symbol"],
        }
        for s in sleeves
        if s.get("recommendation_mode") == "defer_fee_buy"
    ]
    actions = [
        {
            "delta_mv_twd": s.get("delta_mv_twd"),
            "delta_mv_usd": s.get("delta_mv_usd"),
            "symbol": s["symbol"],
            "target_pct": s["target_pct"],
            "trade_side": s.get("trade_side"),
            "trade_units": s.get("trade_units"),
        }
        for s in sleeves
        if s.get("recommendation_mode") == "rebalance"
    ]
    den_usd = float(denom_meta.get("denominator_usd") or 0.0)
    den_twd = round(den_usd * float(usd_twd), 2) if usd_twd is not None else None
    buy_fee_policy: dict[str, Any] = {"active": buy_fee_rules is not None}
    if buy_fee_rules:
        buy_fee_policy["broker_fee_usd_per_trade"] = buy_fee_rules[
            "broker_fee_usd_per_trade"
        ]
        buy_fee_policy["max_buy_fee_as_pct_of_notional"] = buy_fee_rules[
            "max_buy_fee_as_pct_of_notional"
        ]
        buy_fee_policy["max_trade_fee_as_pct_of_notional"] = buy_fee_rules[
            "max_trade_fee_as_pct_of_notional"
        ]
        if "buy_fee_priority_symbols" in buy_fee_rules:
            buy_fee_policy["buy_fee_priority_symbols"] = buy_fee_rules[
                "buy_fee_priority_symbols"
            ]
        if "buy_fee_min_notional_multiplier_priority" in buy_fee_rules:
            buy_fee_policy["buy_fee_min_notional_multiplier_priority"] = (
                buy_fee_rules["buy_fee_min_notional_multiplier_priority"]
            )
        if "buy_fee_min_notional_multiplier_other" in buy_fee_rules:
            buy_fee_policy["buy_fee_min_notional_multiplier_other"] = buy_fee_rules[
                "buy_fee_min_notional_multiplier_other"
            ]
        if "buy_fee_min_notional_multiplier_default" in buy_fee_rules:
            buy_fee_policy["buy_fee_min_notional_multiplier_default"] = (
                buy_fee_rules["buy_fee_min_notional_multiplier_default"]
            )
        if "buy_min_notional_usd_floor" in buy_fee_rules:
            buy_fee_policy["buy_min_notional_usd_floor"] = buy_fee_rules[
                "buy_min_notional_usd_floor"
            ]
        buy_fee_policy["note_zh"] = reb_all.get(
            "buy_fee_note_zh",
            "每筆買／賣各計 broker_fee_usd_per_trade；若手續費÷調整名目大於門檻，不顯示下單建議。"
            "買進時名目低於最少建議名目則標示稍後再大額調整。"
            "buy_fee_priority_symbols 為優先加碼標的（名目門檻較低）；"
            "未列入者用 other 倍數；清單可空改 default。max_trade_fee_as_pct_of_notional 可統一為買賣上限。",
        )
    return {
        "as_of": as_of.isoformat(),
        "buy_fee_policy": buy_fee_policy,
        "cash_usd_in_rebalance_denominator": denom_meta.get("cash_usd_applied"),
        "deferred_buy_actions": deferred_buy_actions,
        "deploy_all_cash_usd": deploy_all_cash_usd,
        "exact_target_min_trade_usd": round(exact_target_min_trade_usd, 4),
        "phase": {
            "effective_from": phase.get("effective_from"),
            "effective_to": phase.get("effective_to"),
            "id": phase.get("id"),
            "note": phase.get("note"),
            "targets": targets,
        },
        "positions_mv_usd_for_targets": round(
            float(denom_meta.get("positions_mv_usd") or 0.0), 4
        ),
        "rebalance_actions": actions,
        "rebalance_denominator_twd": den_twd,
        "rebalance_denominator_usd": round(den_usd, 4),
        "rebalance_needed": need,
        "sleeves": sleeves,
        "total_mv_twd": inv_mv_twd,
        "total_mv_usd": round(inv_mv_usd, 4),
    }
