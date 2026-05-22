"""Investment totals and drawdown-from-peak reinvest trigger (config-driven)."""

from __future__ import annotations


def investment_assets_twd(
    port: dict,
    portfolio_mv_usd: float,
    cash_twd: float,
    cash_usd: float | None,
    usd_twd: float,
) -> float:
    """
    Total for drawdown rule: listed ETF/position MV in TWD (RSSB, RSST, ...).
    By default excludes cash (cash is pre-deployment; not in the market).
    Optional flags can add cash back for special cases.
    """
    cfg = port.get("drawdown_reinvest") or {}
    inc_twd = cfg.get("include_cash_twd_in_investment_total", False)
    inc_usd_cash = cfg.get("include_cash_usd_in_investment_total", False)
    cusd = 0.0 if cash_usd is None else float(cash_usd)
    part = portfolio_mv_usd * usd_twd
    if inc_usd_cash:
        part += cusd * usd_twd
    if inc_twd:
        part += cash_twd
    return part


def drawdown_reinvest_status(
    port: dict,
    investment_assets_twd: float,
) -> tuple[float | None, float | None, float | None, bool]:
    """
    Returns (peak_twd, trigger_level_twd, drawdown_pct_from_peak, trigger_hit).
    peak_twd None if not set in JSON.
    drawdown_pct_from_peak is (peak - current) / peak when peak > 0.
    trigger_hit True when current <= peak * (1 - pct) and peak is set.
    """
    cfg = port.get("drawdown_reinvest") or {}
    peak = cfg.get("peak_investment_value_twd")
    pct = float(cfg.get("trigger_drawdown_from_peak_pct", 0.2))
    if peak is None:
        return None, None, None, False
    peak_f = float(peak)
    if peak_f <= 0:
        return peak_f, None, None, False
    trigger_level = peak_f * (1.0 - pct)
    dd = (peak_f - investment_assets_twd) / peak_f
    hit = investment_assets_twd <= trigger_level + 1e-6
    return peak_f, trigger_level, dd, hit
