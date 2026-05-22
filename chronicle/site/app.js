const PAGE =
  typeof document !== "undefined" &&
  document.documentElement.dataset.page === "details"
    ? "details"
    : "overview";

const DETAIL_META = {
  allocation: { titleKey: "detail.allocation" },
  fx: { titleKey: "detail.fx" },
  loan: { titleKey: "detail.loan" },
  performance: { titleKey: "detail.performance" },
  portfolio: { titleKey: "detail.portfolio" },
};

function isEnLocale() {
  return typeof PLLocale !== "undefined" && PLLocale.isEn();
}

function pllT(key, vars) {
  return typeof PLLocale !== "undefined" ? PLLocale.t(key, vars) : key;
}

function hasCjk(text) {
  return /[\u4e00-\u9fff]/.test(String(text || ""));
}

function chartSeriesLabel(id) {
  return pllT(`chart.${id}`);
}

function phaseTransitionReason(phase) {
  const en = phase?.transition_reason;
  const zh = phase?.transition_reason_zh || phase?.transition_reason || "";
  if (isEnLocale()) {
    if (en && !hasCjk(en)) {
      return en;
    }
    return "";
  }
  return zh;
}

function formatLoanTwdDisplay(snapshot, twdValue) {
  if (twdValue == null || Number.isNaN(Number(twdValue))) {
    return "—";
  }
  if (isEnLocale()) {
    const usd = liveUsdFromTwd(snapshot, twdValue);
    return usd == null ? "—" : `USD ${fmtUsd(usd)}`;
  }
  return `${fmtTwd(twdValue)} TWD`;
}

const CHART_COLORS = {
  nav: "#496c59",
  spy_idx: "#8c5f34",
  spy_shadow: "#8c5f34",
  sso_shadow: "#6f5a9a",
  SPY: "#8c5f34",
  SSO: "#6f5a9a",
};

const THEME = {
  grid: "rgba(79, 58, 38, 0.12)",
  inkSoft: "#6f5b46",
  tooltipBg: "#2f241a",
  tooltipBorder: "rgba(255, 247, 235, 0.18)",
};

function fmtAmount(value, maximumFractionDigits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const locale =
    typeof PLLocale !== "undefined" ? PLLocale.numberLocale() : "zh-TW";
  return Number(value).toLocaleString(locale, { maximumFractionDigits });
}

function fmtTwd(value) {
  return fmtAmount(value, 0);
}

function fmtUsd(value) {
  return fmtAmount(value, 2);
}

function fmtUnits(value) {
  return fmtAmount(value, 4);
}

function fmtPct(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const locale =
    typeof PLLocale !== "undefined" ? PLLocale.numberLocale() : "zh-TW";
  return `${Number(value).toLocaleString(locale, {
    maximumFractionDigits: 2,
  })}%`;
}

function fmtRatioPct(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const locale =
    typeof PLLocale !== "undefined" ? PLLocale.numberLocale() : "zh-TW";
  return `${(Number(value) * 100).toLocaleString(locale, {
    maximumFractionDigits: 2,
  })}%`;
}

function fmtRate(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const locale =
    typeof PLLocale !== "undefined" ? PLLocale.numberLocale() : "zh-TW";
  return Number(value).toLocaleString(locale, {
    minimumFractionDigits: 3,
    maximumFractionDigits: 4,
  });
}

function fmtUsdSigned(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const amount = Number(value);
  const sign = amount < 0 ? "-" : "";
  return `${sign}${fmtUsd(Math.abs(amount))}`;
}

function twdToUsd(valueTwd, usdTwdRate) {
  if (
    valueTwd === null ||
    valueTwd === undefined ||
    Number.isNaN(Number(valueTwd)) ||
    usdTwdRate === null ||
    usdTwdRate === undefined ||
    Number.isNaN(Number(usdTwdRate)) ||
    Number(usdTwdRate) <= 0
  ) {
    return null;
  }
  return Number(valueTwd) / Number(usdTwdRate);
}

function usdToTwd(valueUsd, usdTwdRate) {
  if (
    valueUsd === null ||
    valueUsd === undefined ||
    Number.isNaN(Number(valueUsd)) ||
    usdTwdRate === null ||
    usdTwdRate === undefined ||
    Number.isNaN(Number(usdTwdRate)) ||
    Number(usdTwdRate) <= 0
  ) {
    return null;
  }
  return Number(valueUsd) * Number(usdTwdRate);
}

function liveUsdTwdRate(snapshot) {
  if (
    typeof snapshot?.usd_twd_source === "string" &&
    snapshot.usd_twd_source.startsWith("yahoo") &&
    snapshot.usd_twd != null &&
    !Number.isNaN(Number(snapshot.usd_twd))
  ) {
    return Number(snapshot.usd_twd);
  }
  return null;
}

function liveUsdFromTwd(snapshot, twdValue) {
  return twdToUsd(twdValue, liveUsdTwdRate(snapshot));
}

function liveTwdFromUsd(snapshot, usdValue) {
  return usdToTwd(usdValue, liveUsdTwdRate(snapshot));
}

function numberState(value, mode = "positive_good") {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "neutral";
  }
  const amount = Number(value);
  if (Math.abs(amount) < 1e-9) {
    return "neutral";
  }
  if (mode === "net_worth") {
    return amount > 0 ? "good" : "bad";
  }
  if (mode === "liability") {
    return amount > 0 ? "bad" : "good";
  }
  return amount > 0 ? "good" : "neutral";
}

function setAssetMetric(primaryId, altId, twdValue, usdValue, stateMode = "positive_good") {
  const primary = document.getElementById(primaryId);
  if (isEnLocale()) {
    setState(primary, fmtUsd(usdValue), numberState(usdValue, stateMode));
    PLLocale.setUnitForMetric(primaryId, "USD");
  } else {
    setState(primary, fmtTwd(twdValue), numberState(twdValue, stateMode));
    PLLocale.setUnitForMetric(primaryId, "TWD");
  }
  PLLocale.hideSubline(altId);
}

function setHtml(id, html) {
  const element = document.getElementById(id);
  if (element) {
    element.innerHTML = html;
  }
}

function moneyPairTwdPrimaryHtml(snapshot, twdValue) {
  if (isEnLocale()) {
    const usdValue = liveUsdFromTwd(snapshot, twdValue);
    return `<span class="money-stack"><span class="money-primary">USD ${fmtUsdSigned(usdValue)}</span></span>`;
  }
  return `<span class="money-stack"><span class="money-primary">TWD ${fmtTwd(twdValue)}</span></span>`;
}

function moneyPairUsdPrimaryHtml(snapshot, usdValue) {
  return `<span class="money-stack"><span class="money-primary">USD ${fmtUsdSigned(usdValue)}</span></span>`;
}

function setStockMetric(primaryId, usdValue, stateMode = "positive_good") {
  const primary = document.getElementById(primaryId);
  if (!primary) {
    return;
  }
  setState(primary, fmtUsd(usdValue), numberState(usdValue, stateMode));
  PLLocale.setUnitForMetric(primaryId, "USD");
  const note = primary?.closest(".focus-metric")?.querySelector(".focus-metric-note");
  if (note) {
    note.textContent = "";
    note.hidden = true;
  }
}

function setAggregateMetric(primaryId, twdValue, usdValue, stateMode = "positive_good") {
  const primary = document.getElementById(primaryId);
  if (!primary) {
    return;
  }
  if (isEnLocale()) {
    setState(primary, fmtUsd(usdValue), numberState(usdValue, stateMode));
    PLLocale.setUnitForMetric(primaryId, "USD");
  } else {
    setState(primary, fmtTwd(twdValue), numberState(twdValue, stateMode));
    PLLocale.setUnitForMetric(primaryId, "TWD");
  }
  const note = primary?.closest(".focus-metric")?.querySelector(".focus-metric-note");
  if (note) {
    note.textContent = "";
    note.hidden = true;
  }
}

function parseIsoDate(value) {
  if (!value) {
    return null;
  }
  const date = new Date(`${value}T00:00:00`);
  return Number.isNaN(date.getTime()) ? null : date;
}

function compareIsoDate(left, right) {
  const leftDate = parseIsoDate(left);
  const rightDate = parseIsoDate(right);
  if (!leftDate || !rightDate) {
    return 0;
  }
  return leftDate.getTime() - rightDate.getTime();
}

function compareIsoDateNewestFirst(left, right) {
  return compareIsoDate(right, left);
}

function referenceTodayFromSnapshot(snapshot) {
  const raw = snapshot?.generated_at;
  if (typeof raw === "string" && raw.length >= 10) {
    const parsed = parseIsoDate(raw.slice(0, 10));
    if (parsed) {
      return parsed;
    }
  }
  return new Date();
}

/** Closest calendar date to reference day first (for schedules with future rows). */
function compareDateClosestTodayFirst(left, right, today) {
  const leftDate = parseIsoDate(left);
  const rightDate = parseIsoDate(right);
  if (!leftDate && !rightDate) {
    return 0;
  }
  if (!leftDate) {
    return 1;
  }
  if (!rightDate) {
    return -1;
  }
  const todayMs = today.getTime();
  const leftDist = Math.abs(leftDate.getTime() - todayMs);
  const rightDist = Math.abs(rightDate.getTime() - todayMs);
  if (leftDist !== rightDist) {
    return leftDist - rightDist;
  }
  return rightDate.getTime() - leftDate.getTime();
}

function tradeExecutedAtSortKey(raw) {
  if (!raw || typeof raw !== "string") {
    return 0;
  }
  const trimmed = raw.trim();
  const normalized = trimmed.includes("T") ? trimmed.replace(" ", "T") : `${trimmed}T12:00:00`;
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? 0 : parsed.getTime();
}

function compareTradesNewestFirst(left, right) {
  const delta =
    tradeExecutedAtSortKey(right.executed_at || right.date) -
    tradeExecutedAtSortKey(left.executed_at || left.date);
  if (delta !== 0) {
    return delta;
  }
  const sy = `${left.symbol || ""}`.localeCompare(`${right.symbol || ""}`, undefined, {
    sensitivity: "base",
  });
  if (sy !== 0) {
    return sy;
  }
  return `${left.side || ""}`.localeCompare(`${right.side || ""}`, undefined, { sensitivity: "base" });
}

function fmtNavTouchPts(value) {
  if (value == null || Number.isNaN(Number(value))) {
    return "—";
  }
  const n = Number(value);
  const sign = n > 0 ? "+" : "";
  return `${sign}${fmtAmount(n, 4)} ${pllT("unit.pts")}`;
}

function setText(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.textContent = value;
  }
}

function setState(element, text, state = "neutral") {
  if (!element) {
    return;
  }
  element.textContent = text;
  element.dataset.state = state;
}

const PHASE_TARGET_SYMBOL_ORDER = ["RSSB", "RSST", "RSSY", "RSIT"];

function sortPhaseTargets(targets) {
  const rank = Object.fromEntries(
    PHASE_TARGET_SYMBOL_ORDER.map((symbol, index) => [symbol, index])
  );
  return [...(targets || [])].sort((left, right) => {
    const leftRank = rank[left.symbol] ?? 999;
    const rightRank = rank[right.symbol] ?? 999;
    if (leftRank !== rightRank) {
      return leftRank - rightRank;
    }
    return String(left.symbol).localeCompare(String(right.symbol));
  });
}

function phaseTargetsText(phase) {
  return sortPhaseTargets(phase?.targets)
    .map((target) => `${target.symbol} ${((target.weight || 0) * 100).toFixed(0)}%`)
    .join(" / ");
}

function setPhaseTargetsHtml(id, phase, variant = "inline") {
  const element = document.getElementById(id);
  if (!element) {
    return;
  }
  const chips = phaseTargetsChipsHtml(phase);
  if (chips === "—") {
    element.textContent = "—";
    return;
  }
  if (variant === "compact") {
    element.innerHTML = chips;
    return;
  }
  element.innerHTML = `<div class="phase-targets phase-targets-${variant}">${chips}</div>`;
}

function formatUsdPriceCell(usdValue) {
  if (usdValue == null || Number.isNaN(Number(usdValue))) {
    return "—";
  }
  return `<span class="cell-usd"><span class="cell-usd-amt">${fmtUsd(usdValue)}</span><span class="cell-usd-unit">USD</span></span>`;
}

function formatQuoteLastPriceCell(snapshot, row) {
  if (!row || row.listed === false) {
    return pllT("stock.unlisted");
  }
  if (row.last_usd == null || Number.isNaN(Number(row.last_usd))) {
    return "—";
  }
  return formatUsdPriceCell(row.last_usd);
}

function formatPositionStatusCell(sleeve, snapshot) {
  if (!sleeve) {
    return "—";
  }
  return `<div class="action-cell action-cell-compact">
    <span class="${portfolioStatusClass(sleeve.status)}">${portfolioStatusLabel(sleeve.status)}</span>
    <span class="action-cell-text">${recommendationText(sleeve, snapshot)}</span>
  </div>`;
}

function activePhase(snapshot) {
  return snapshot.portfolio_view?.phase || snapshot.allocations?.phases?.[0] || null;
}

function nextPhase(snapshot) {
  const asOf = snapshot.generated_at || "";
  return (snapshot.allocations?.phases || []).find(
    (phase) => phase.effective_from && compareIsoDate(phase.effective_from, asOf) > 0
  );
}

function getTrackedRows(snapshot) {
  return (snapshot.quotes || []).filter((row) => row.benchmark !== true);
}

function getHeldRows(snapshot) {
  return getTrackedRows(snapshot).filter((row) => Number(row.units || 0) > 0);
}

function tradeRows(snapshot) {
  return snapshot.trade_ledger?.trades || [];
}

function tradeSideLabel(side) {
  if (side === "buy") {
    return pllT("trade.buy");
  }
  if (side === "sell") {
    return pllT("trade.sell");
  }
  return side || "—";
}

function sumValues(rows, key) {
  return rows.reduce((total, row) => total + Number(row[key] || 0), 0);
}

function fxEventDirection(event) {
  if (!event || typeof event !== "object") {
    return "twd_to_usd";
  }
  if (event.direction === "usd_to_twd") {
    return "usd_to_twd";
  }
  const usd = Number(event.usd_amount);
  if (!Number.isNaN(usd) && usd < 0) {
    return "usd_to_twd";
  }
  return "twd_to_usd";
}

function lastDefinedValue(values) {
  if (!Array.isArray(values)) {
    return null;
  }
  for (let index = values.length - 1; index >= 0; index -= 1) {
    const value = values[index];
    if (value !== null && value !== undefined && !Number.isNaN(Number(value))) {
      return Number(value);
    }
  }
  return null;
}

function formatExecutedAtDisplay(iso) {
  if (!iso || typeof iso !== "string") {
    return "—";
  }
  const trimmed = iso.trim();
  const normalized = trimmed.includes("T") ? trimmed : trimmed.replace(" ", "T");
  const parsed = new Date(normalized);
  if (Number.isNaN(parsed.getTime())) {
    return trimmed.replace("T", " ");
  }
  const locale =
    typeof PLLocale !== "undefined" ? PLLocale.numberLocale() : "zh-TW";
  return parsed.toLocaleString(locale, {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function formatChartAxisLabel(raw) {
  if (!raw || typeof raw !== "string") {
    return raw;
  }
  if (/^\d{4}-\d{2}-\d{2}T/.test(raw)) {
    return formatExecutedAtDisplay(raw);
  }
  return raw;
}

function positionSymbolLabel(row) {
  const sym = row.symbol || "—";
  const t = row.yahoo_ticker;
  if (!t || t === sym) {
    return sym;
  }
  return `${sym}（${t}）`;
}

function positionUnrealizedPct(row) {
  if (
    row.listed === false ||
    row.unrealized_pnl_usd == null ||
    row.avg_entry_usd == null ||
    row.units == null
  ) {
    return null;
  }
  const units = Number(row.units);
  const avg = Number(row.avg_entry_usd);
  const cost = avg * units;
  if (!Number.isFinite(cost) || Math.abs(cost) < 1e-9) {
    return null;
  }
  return (Number(row.unrealized_pnl_usd) / cost) * 100;
}

function unrealizedPnlState(amountUsd) {
  if (amountUsd == null || Number.isNaN(Number(amountUsd))) {
    return "neutral";
  }
  const n = Number(amountUsd);
  if (Math.abs(n) < 1e-9) {
    return "neutral";
  }
  return n > 0 ? "good" : "bad";
}

function formatPositionMvCell(sleeve) {
  if (!sleeve) {
    return "—";
  }
  if (isEnLocale() && sleeve.mv_usd != null) {
    return `${fmtUsd(sleeve.mv_usd)} USD`;
  }
  if (sleeve.mv_twd != null) {
    return `${fmtTwd(sleeve.mv_twd)} TWD`;
  }
  if (sleeve.mv_usd != null) {
    return `${fmtUsd(sleeve.mv_usd)} USD`;
  }
  return "—";
}

function formatPositionUnrealizedCell(row) {
  if (row.listed === false || row.unrealized_pnl_usd == null) {
    return "—";
  }
  const pnl = Number(row.unrealized_pnl_usd);
  const pct = positionUnrealizedPct(row);
  const state = unrealizedPnlState(pnl);
  const pctHtml =
    pct != null && !Number.isNaN(pct)
      ? ` <span class="pnl-pct">（${fmtPct(pct)}）</span>`
      : "";
  return `<span class="pnl-cell" data-state="${state}"><span class="pnl-amt">${fmtUsdSigned(
    pnl
  )} USD</span>${pctHtml}</span>`;
}

function positionsTableWrapHtml(tableBodyHtml, caption = "") {
  const captionHtml = caption
    ? `<p class="table-scroll-hint" aria-hidden="true">${caption}</p>`
    : "";
  return (
    `${captionHtml}` +
    '<div class="table-wrap table-wrap-positions">' +
    `<table class="quotes positions-table">${tableBodyHtml}</table>` +
    "</div>"
  );
}

function phaseWeightMap(phase) {
  const map = {};
  for (const target of phase?.targets || []) {
    if (target?.symbol) {
      map[target.symbol] = Number(target.weight) || 0;
    }
  }
  return map;
}

function phaseTargetsChipsHtml(phase) {
  const chips = sortPhaseTargets(phase?.targets)
    .map(
      (t) =>
        `<span class="phase-target-chip">${t.symbol} ${((t.weight || 0) * 100).toFixed(0)}%</span>`
    )
    .join("");
  return chips || "—";
}

function phaseTargetsChipsWithDeltaHtml(phase, priorPhase) {
  const prior = priorPhase ? phaseWeightMap(priorPhase) : null;
  const currentMap = phaseWeightMap(phase);
  const symbols = [
    ...new Set([
      ...sortPhaseTargets(phase?.targets).map((t) => t.symbol),
      ...(prior ? Object.keys(prior) : []),
    ]),
  ];
  const ordered = sortPhaseTargets(
    symbols.map((symbol) => ({ symbol, weight: currentMap[symbol] || 0 }))
  );
  if (!ordered.length) {
    return "—";
  }
  return ordered
    .map((target) => {
      const sym = target.symbol;
      const pct = (currentMap[sym] || 0) * 100;
      const hasCurrent = (currentMap[sym] || 0) > 0;
      const label = hasCurrent ? `${sym} ${pct.toFixed(0)}%` : `${sym} 0%`;
      let deltaHtml = "";
      if (prior) {
        const prevPct = (prior[sym] || 0) * 100;
        if (!hasCurrent && prevPct > 0) {
          deltaHtml = `<span class="phase-target-delta is-down">${pllT("phase.removed")}</span>`;
        } else if (hasCurrent && (prior[sym] == null || prior[sym] === 0)) {
          deltaHtml = `<span class="phase-target-delta is-new">${pllT("phase.added")}</span>`;
        } else {
          const delta = pct - prevPct;
          if (Math.abs(delta) >= 0.5) {
            const cls = delta > 0 ? "is-up" : "is-down";
            const sign = delta > 0 ? "+" : "";
            deltaHtml = `<span class="phase-target-delta ${cls}">${sign}${delta.toFixed(
              0
            )}</span>`;
          }
        }
      }
      return `<span class="phase-target-chip">${label}${deltaHtml}</span>`;
    })
    .join("");
}

function loanProgressPct(numerator, denominator) {
  const num = Number(numerator);
  const den = Number(denominator);
  if (!Number.isFinite(num) || !Number.isFinite(den) || den <= 0) {
    return null;
  }
  return Math.min(100, Math.max(0, (num / den) * 100));
}

function loanProgressBarHtml(label, valueText, pct) {
  const width = pct == null ? 0 : pct;
  const pctText = pct == null ? "—" : `${pct.toFixed(1)}%`;
  return `
    <div class="loan-progress-item">
      <div class="loan-progress-head">
        <span class="loan-progress-label">${label}</span>
        <span class="loan-progress-value">${valueText}</span>
        <span class="loan-progress-pct">${pctText}</span>
      </div>
      <div class="loan-progress-track" role="progressbar" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${width.toFixed(1)}">
        <div class="loan-progress-fill" style="width:${width}%"></div>
      </div>
    </div>
  `;
}

function loanDlSectionHtml(title, rows) {
  const body = rows
    .map(
      ([label, value]) => `
        <dt>${label}</dt>
        <dd>${value}</dd>
      `
    )
    .join("");
  return `
    <section class="loan-dl-section">
      <h3 class="loan-dl-section-title">${title}</h3>
      <dl class="dl-grid loan-dl-section-grid">${body}</dl>
    </section>
  `;
}

function renderRealizedPnlPanel(snapshot) {
  renderSellHistory(snapshot);
}

function tradeHistoryTableHtml(trades, emptyKey) {
  if (!trades.length) {
    return emptyState(emptyKey);
  }
  return `
    <div class="table-wrap table-scroll portfolio-scroll-panel pll-scroll trade-history-panel">
      <table class="quotes trade-history-table">
        <thead>
          <tr>
            <th>${pllT("th.time")}</th>
            <th>${pllT("th.symbol")}</th>
            <th>${pllT("th.side")}</th>
            <th>${pllT("th.units")}</th>
            <th>${pllT("th.price")}</th>
            <th>${pllT("th.notional")}</th>
            <th>${pllT("th.fee")}</th>
          </tr>
        </thead>
        <tbody>
          ${trades.map((trade) => tradeHistoryRowHtml(trade)).join("")}
        </tbody>
      </table>
    </div>
  `;
}

function sellHistoryTableHtml(rows) {
  if (!rows.length) {
    return emptyState("realized.none");
  }
  return `
    <div class="table-wrap table-scroll portfolio-scroll-panel pll-scroll trade-history-panel">
      <table class="quotes sell-history-table">
        <thead>
          <tr>
            <th>${pllT("th.time")}</th>
            <th>${pllT("th.symbol")}</th>
            <th>${pllT("th.shares")}</th>
            <th>${pllT("th.net_proceeds")}</th>
            <th>${pllT("th.cost_usd")}</th>
            <th>${pllT("th.realized_usd")}</th>
          </tr>
        </thead>
        <tbody>
          ${rows
            .map(
              (r) => `
            <tr>
              <td>${r.executed_at ? formatExecutedAtDisplay(r.executed_at) : "—"}</td>
              <td class="sym">${r.symbol || "—"}</td>
              <td>${fmtUnits(r.units)}</td>
              <td>${fmtUsd(r.net_proceeds_usd)}</td>
              <td>${fmtUsd(r.cost_basis_usd)}</td>
              <td>${fmtUsdSigned(r.realized_pnl_usd)}</td>
            </tr>
          `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function renderSellHistory(snapshot) {
  const root = document.getElementById("sell-history-root");
  if (!root) {
    return;
  }
  const rp = snapshot.realized_pnl || {};
  const rows = (rp.rows || [])
    .filter((r) => r.realized_pnl_usd != null)
    .sort((left, right) =>
      compareTradesNewestFirst(
        { executed_at: left.executed_at, date: left.date },
        { executed_at: right.executed_at, date: right.date }
      )
    );
  root.innerHTML = sellHistoryTableHtml(rows);
}

function renderBuyHistory(snapshot) {
  const root = document.getElementById("buy-history-root");
  if (!root) {
    return;
  }
  const trades = [...tradeRows(snapshot)]
    .filter((trade) => String(trade.side || "").toLowerCase() === "buy")
    .sort(compareTradesNewestFirst);
  root.innerHTML = tradeHistoryTableHtml(trades, "empty.no_trades");
}

function applyRealizedPnlUi(snapshot) {
  const rp = snapshot.realized_pnl || {};
  const usd = rp.total_realized_pnl_usd;
  const twd =
    rp.total_realized_pnl_twd != null
      ? Number(rp.total_realized_pnl_twd)
      : liveTwdFromUsd(snapshot, usd);
  const has = rp.sell_count > 0 && usd != null && !Number.isNaN(Number(usd));

  const portfolioTwd = document.getElementById("portfolio-realized-twd");
  if (portfolioTwd) {
    if (isEnLocale()) {
      setState(
        portfolioTwd,
        has ? fmtUsdSigned(usd) : "—",
        has ? unrealizedPnlState(usd) : "neutral"
      );
      PLLocale.setUnitForMetric("portfolio-realized-twd", "USD");
    } else {
      setState(
        portfolioTwd,
        has ? fmtTwd(twd) : "—",
        has ? unrealizedPnlState(usd) : "neutral"
      );
      PLLocale.setUnitForMetric("portfolio-realized-twd", "TWD");
    }
  }
  PLLocale.hideSubline("portfolio-realized-sub");

  const perfUsd = document.getElementById("perf-realized-usd");
  if (perfUsd) {
    if (isEnLocale()) {
      setState(perfUsd, has ? fmtUsdSigned(usd) : "—", has ? unrealizedPnlState(usd) : "neutral");
      PLLocale.setUnitForMetric("perf-realized-usd", "USD");
    } else {
      setState(perfUsd, has ? fmtTwd(twd) : "—", has ? unrealizedPnlState(usd) : "neutral");
      PLLocale.setUnitForMetric("perf-realized-usd", "TWD");
    }
  }
  PLLocale.hideSubline("perf-realized-twd");

}

function samePeriodPerformance(snapshot) {
  const labels = snapshot.nav_chart?.labels || [];
  const sourceDatasets = snapshot.nav_chart?.datasets || [];
  if (!labels.length || !sourceDatasets.length) {
    return null;
  }

  const rawById = Object.fromEntries(
    sourceDatasets.map((row) => [row.id, row.data || []])
  );
  const seriesIds = ["nav", "spy_shadow", "sso_shadow"].filter((id) => rawById[id]);
  const limit = Math.min(labels.length, ...seriesIds.map((id) => rawById[id].length));
  if (!limit) {
    return null;
  }

  let startIndex = -1;
  for (let index = 0; index < limit; index += 1) {
    const navValue = rawById.nav?.[index];
    if (navValue !== null && navValue !== undefined && !Number.isNaN(Number(navValue))) {
      startIndex = index;
      break;
    }
  }
  if (startIndex < 0) {
    return null;
  }

  const bases = {};
  for (const id of seriesIds) {
    const base = Number(rawById[id][startIndex]);
    if (!Number.isFinite(base) || base <= 0) {
      return null;
    }
    bases[id] = base;
  }

  const outLabels = [];
  const scaled = Object.fromEntries(seriesIds.map((id) => [id, []]));
  for (let index = startIndex; index < limit; index += 1) {
    let ok = true;
    for (const id of seriesIds) {
      const value = Number(rawById[id][index]);
      if (!Number.isFinite(value)) {
        ok = false;
        break;
      }
    }
    if (!ok) {
      continue;
    }
    outLabels.push(formatChartAxisLabel(labels[index]));
    for (const id of seriesIds) {
      scaled[id].push((Number(rawById[id][index]) / bases[id]) * 100);
    }
  }
  if (!outLabels.length) {
    return null;
  }

  const datasetMeta = {
    nav: { id: "nav", label: chartSeriesLabel("nav"), borderColor: CHART_COLORS.nav },
    spy_shadow: {
      id: "spy_shadow",
      label: chartSeriesLabel("spy_shadow"),
      borderColor: CHART_COLORS.spy_shadow,
    },
    sso_shadow: {
      id: "sso_shadow",
      label: chartSeriesLabel("sso_shadow"),
      borderColor: CHART_COLORS.sso_shadow,
    },
  };
  const chartDatasets = seriesIds.map((id) => ({
    ...datasetMeta[id],
    data: scaled[id],
  }));

  return {
    startDate: outLabels[0],
    endDate: outLabels[outLabels.length - 1],
    navChart: { labels: outLabels, datasets: chartDatasets.filter((d) => d.id === "nav") },
    spyChart: {
      labels: outLabels,
      datasets: chartDatasets.filter((d) => d.id !== "nav"),
    },
    combinedChart: { labels: outLabels, datasets: chartDatasets },
  };
}

const TRADING_DAYS_PER_YEAR = 252;
const RISK_FREE_RATE_ANNUAL = 0.01;

function riskFreeDailyRate() {
  return Math.pow(1 + RISK_FREE_RATE_ANNUAL, 1 / TRADING_DAYS_PER_YEAR) - 1;
}

const PERF_METRIC_SERIES = [
  { id: "nav" },
  { id: "spy_shadow" },
  { id: "sso_shadow" },
];

function extractAlignedNavSeries(snapshot) {
  const labels = snapshot.nav_chart?.labels || [];
  const sourceDatasets = snapshot.nav_chart?.datasets || [];
  if (!labels.length || !sourceDatasets.length) {
    return null;
  }
  const rawById = Object.fromEntries(
    sourceDatasets.map((row) => [row.id, row.data || []])
  );
  const seriesIds = PERF_METRIC_SERIES.map((row) => row.id).filter((id) => rawById[id]);
  const limit = Math.min(labels.length, ...seriesIds.map((id) => rawById[id].length));
  if (!limit) {
    return null;
  }
  let startIndex = -1;
  for (let index = 0; index < limit; index += 1) {
    const navValue = rawById.nav?.[index];
    if (navValue !== null && navValue !== undefined && !Number.isNaN(Number(navValue))) {
      startIndex = index;
      break;
    }
  }
  if (startIndex < 0) {
    return null;
  }
  const outLabels = [];
  const series = Object.fromEntries(seriesIds.map((id) => [id, []]));
  for (let index = startIndex; index < limit; index += 1) {
    let ok = true;
    for (const id of seriesIds) {
      const value = Number(rawById[id][index]);
      if (!Number.isFinite(value) || value <= 0) {
        ok = false;
        break;
      }
    }
    if (!ok) {
      continue;
    }
    outLabels.push(labels[index]);
    for (const id of seriesIds) {
      series[id].push(Number(rawById[id][index]));
    }
  }
  if (outLabels.length < 2) {
    return null;
  }
  return {
    fromLabel: formatChartAxisLabel(outLabels[0]),
    toLabel: formatChartAxisLabel(outLabels[outLabels.length - 1]),
    series,
  };
}

function dailySimpleReturns(levels) {
  const out = [];
  for (let index = 1; index < levels.length; index += 1) {
    const prev = levels[index - 1];
    const cur = levels[index];
    if (prev > 1e-12) {
      out.push(cur / prev - 1);
    }
  }
  return out;
}

function maxDrawdownFraction(levels) {
  let peak = levels[0];
  let maxDd = 0;
  for (const level of levels) {
    if (level > peak) {
      peak = level;
    }
    if (peak > 1e-12) {
      const dd = level / peak - 1;
      if (dd < maxDd) {
        maxDd = dd;
      }
    }
  }
  return maxDd;
}

function maxDrawdownDurationDays(levels) {
  let peak = levels[0];
  let duration = 0;
  let maxDuration = 0;
  for (let index = 1; index < levels.length; index += 1) {
    if (levels[index] >= peak) {
      peak = levels[index];
      duration = 0;
    } else {
      duration += 1;
      maxDuration = Math.max(maxDuration, duration);
    }
  }
  return maxDuration;
}

function streakStats(rets) {
  let maxUpStreak = 0;
  let maxDownStreak = 0;
  let up = 0;
  let down = 0;
  for (const value of rets) {
    if (value > 0) {
      up += 1;
      down = 0;
      maxUpStreak = Math.max(maxUpStreak, up);
    } else if (value < 0) {
      down += 1;
      up = 0;
      maxDownStreak = Math.max(maxDownStreak, down);
    } else {
      up = 0;
      down = 0;
    }
  }
  return { maxUpStreak, maxDownStreak };
}

function historicalVarPct(rets, tailFraction) {
  if (!rets.length) {
    return null;
  }
  const sorted = [...rets].sort((left, right) => left - right);
  const idx = Math.max(0, Math.floor(tailFraction * sorted.length) - 1);
  return sorted[idx] * 100;
}

function historicalCvarPct(rets, tailFraction) {
  if (!rets.length) {
    return null;
  }
  const sorted = [...rets].sort((left, right) => left - right);
  const count = Math.max(1, Math.floor(tailFraction * sorted.length));
  const tail = sorted.slice(0, count);
  const mean = tail.reduce((sum, value) => sum + value, 0) / tail.length;
  return mean * 100;
}

function performanceRiskStats(levels) {
  if (!levels || levels.length < 2) {
    return null;
  }
  const rets = dailySimpleReturns(levels);
  if (!rets.length) {
    return null;
  }
  const first = levels[0];
  const last = levels[levels.length - 1];
  const totalReturn = last / first - 1;
  const annReturn =
    Math.pow(1 + totalReturn, TRADING_DAYS_PER_YEAR / rets.length) - 1;
  const mean = rets.reduce((sum, value) => sum + value, 0) / rets.length;
  const variance =
    rets.reduce((sum, value) => sum + (value - mean) ** 2, 0) /
    Math.max(rets.length - 1, 1);
  const vol = Math.sqrt(variance) * Math.sqrt(TRADING_DAYS_PER_YEAR);
  const sharpe =
    vol > 1e-12 ? (annReturn - RISK_FREE_RATE_ANNUAL) / vol : null;
  const rfDaily = riskFreeDailyRate();
  const excessDaily = rets.map((value) => value - rfDaily);
  const downsideSq =
    excessDaily.reduce((sum, value) => sum + Math.min(value, 0) ** 2, 0) / rets.length;
  const downDevSortino = Math.sqrt(downsideSq);
  const sortino =
    downDevSortino > 1e-12
      ? ((mean - rfDaily) / downDevSortino) * Math.sqrt(TRADING_DAYS_PER_YEAR)
      : null;
  const neg = rets.filter((value) => value < 0);
  const maxDd = maxDrawdownFraction(levels);
  const calmar =
    maxDd < -1e-6 ? annReturn / Math.abs(maxDd) : null;
  const bestDayPct = Math.max(...rets) * 100;
  const worstDayPct = Math.min(...rets) * 100;
  const winRatePct = (rets.filter((value) => value > 0).length / rets.length) * 100;
  const positiveDays = rets.filter((value) => value > 0).length;
  const negativeDays = rets.filter((value) => value < 0).length;
  let downsideVolPct = null;
  if (neg.length > 0) {
    const downDev = Math.sqrt(neg.reduce((sum, value) => sum + value ** 2, 0) / neg.length);
    downsideVolPct = downDev * Math.sqrt(TRADING_DAYS_PER_YEAR) * 100;
  }
  const avgDailyReturnPct = mean * 100;
  const gains = rets.filter((value) => value > 0).reduce((sum, value) => sum + value, 0);
  const losses = Math.abs(
    rets.filter((value) => value < 0).reduce((sum, value) => sum + value, 0)
  );
  const profitFactor = losses > 1e-12 ? gains / losses : null;
  let skewness = null;
  let kurtosis = null;
  if (rets.length >= 3 && variance > 1e-18) {
    const sd = Math.sqrt(variance);
    const centered = rets.map((value) => value - mean);
    const m3 = centered.reduce((sum, value) => sum + value ** 3, 0) / rets.length;
    const m4 = centered.reduce((sum, value) => sum + value ** 4, 0) / rets.length;
    skewness = m3 / sd ** 3;
    kurtosis = m4 / sd ** 4 - 3;
  }
  const upDays = rets.filter((value) => value > 0);
  const downDays = rets.filter((value) => value < 0);
  const avgWinDayPct = upDays.length
    ? (upDays.reduce((sum, value) => sum + value, 0) / upDays.length) * 100
    : null;
  const avgLossDayPct = downDays.length
    ? (downDays.reduce((sum, value) => sum + value, 0) / downDays.length) * 100
    : null;
  const gainLossRatio =
    avgWinDayPct != null && avgLossDayPct != null && avgLossDayPct < -1e-12
      ? Math.abs(avgWinDayPct / avgLossDayPct)
      : null;
  const recoveryFactor = maxDd < -1e-6 ? totalReturn / Math.abs(maxDd) : null;
  const { maxUpStreak, maxDownStreak } = streakStats(rets);
  return {
    intervalReturnPct: totalReturn * 100,
    annReturnPct: annReturn * 100,
    volPct: vol * 100,
    downsideVolPct,
    sharpe,
    sortino,
    maxDrawdownPct: maxDd * 100,
    maxDdDurationDays: maxDrawdownDurationDays(levels),
    calmar,
    recoveryFactor,
    bestDayPct,
    worstDayPct,
    avgDailyReturnPct,
    avgWinDayPct,
    avgLossDayPct,
    gainLossRatio,
    winRatePct,
    profitFactor,
    var95DailyPct: historicalVarPct(rets, 0.05),
    cvar95DailyPct: historicalCvarPct(rets, 0.05),
    skewness,
    kurtosis,
    positiveDays,
    negativeDays,
    maxUpStreak,
    maxDownStreak,
    observationDays: rets.length,
  };
}

function performanceRelativeStats(levels, benchLevels) {
  const rets = dailySimpleReturns(levels);
  const benchRets = dailySimpleReturns(benchLevels);
  const n = Math.min(rets.length, benchRets.length);
  if (n < 2 || levels.length < 2 || benchLevels.length < 2) {
    return null;
  }
  const alignedRets = rets.slice(rets.length - n);
  const alignedBench = benchRets.slice(benchRets.length - n);
  const meanR = alignedRets.reduce((sum, value) => sum + value, 0) / n;
  const meanB = alignedBench.reduce((sum, value) => sum + value, 0) / n;
  let cov = 0;
  let varBench = 0;
  let varSeries = 0;
  for (let index = 0; index < n; index += 1) {
    const dr = alignedRets[index] - meanR;
    const db = alignedBench[index] - meanB;
    cov += dr * db;
    varBench += db ** 2;
    varSeries += dr ** 2;
  }
  const denom = Math.max(n - 1, 1);
  cov /= denom;
  varBench /= denom;
  varSeries /= denom;
  const corr =
    varBench > 1e-18 && varSeries > 1e-18 ? cov / Math.sqrt(varBench * varSeries) : null;
  const beta = varBench > 1e-18 ? cov / varBench : null;
  const teDaily = alignedRets.map((value, index) => value - alignedBench[index]);
  const teMean = teDaily.reduce((sum, value) => sum + value, 0) / n;
  const teVar =
    teDaily.reduce((sum, value) => sum + (value - teMean) ** 2, 0) / Math.max(n - 1, 1);
  const trackingErrorPct = Math.sqrt(teVar) * Math.sqrt(TRADING_DAYS_PER_YEAR) * 100;
  const totalReturn = levels[levels.length - 1] / levels[0] - 1;
  const benchReturn = benchLevels[benchLevels.length - 1] / benchLevels[0] - 1;
  const excessReturnPct = (totalReturn - benchReturn) * 100;
  const periodExcess = totalReturn - benchReturn;
  const annExcess =
    n > 0 ? Math.pow(1 + periodExcess, TRADING_DAYS_PER_YEAR / n) - 1 : null;
  const informationRatio =
    trackingErrorPct > 1e-6 && annExcess != null
      ? (annExcess * 100) / trackingErrorPct
      : null;
  let upPort = 0;
  let upBench = 0;
  let downPort = 0;
  let downBench = 0;
  for (let index = 0; index < n; index += 1) {
    if (alignedBench[index] > 0) {
      upBench += alignedBench[index];
      upPort += alignedRets[index];
    }
    if (alignedBench[index] < 0) {
      downBench += alignedBench[index];
      downPort += alignedRets[index];
    }
  }
  const upCapturePct = upBench > 1e-12 ? (upPort / upBench) * 100 : null;
  const downCapturePct = downBench < -1e-12 ? (downPort / downBench) * 100 : null;
  return {
    excessReturnPct,
    informationRatio,
    beta,
    corr,
    trackingErrorPct,
    upCapturePct,
    downCapturePct,
  };
}

function fmtMetricPct(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const sign = Number(value) >= 0 ? "+" : "";
  return `${sign}${Number(value).toFixed(2)}%`;
}

function fmtRatio(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return fmtAmount(Number(value), 2);
}

function fmtMetricPlainPct(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  return `${Number(value).toFixed(2)}%`;
}

const PERF_METRIC_ROWS = [
  { key: "intervalReturnPct", format: "pct" },
  { key: "annReturnPct", format: "pct" },
  { key: "excessReturnPct", format: "pct" },
  { key: "sharpe", format: "ratio" },
  { key: "sortino", format: "ratio" },
  { key: "calmar", format: "ratio" },
  { key: "recoveryFactor", format: "ratio" },
  { key: "maxDrawdownPct", format: "pct" },
  { key: "maxDdDurationDays", format: "int" },
  { key: "volPct", format: "pct" },
  { key: "downsideVolPct", format: "plainPct" },
  { key: "var95DailyPct", format: "pct" },
  { key: "cvar95DailyPct", format: "pct" },
  { key: "winRatePct", format: "plainPct" },
  { key: "profitFactor", format: "ratio" },
  { key: "gainLossRatio", format: "ratio" },
  { key: "upCapturePct", format: "plainPct" },
  { key: "downCapturePct", format: "plainPct" },
  { key: "beta", format: "ratio" },
  { key: "corr", format: "ratio" },
  { key: "trackingErrorPct", format: "pct" },
  { key: "bestDayPct", format: "pct" },
  { key: "worstDayPct", format: "pct" },
  { key: "avgDailyReturnPct", format: "pct" },
  { key: "avgWinDayPct", format: "pct" },
  { key: "avgLossDayPct", format: "pct" },
  { key: "positiveDays", format: "int" },
  { key: "negativeDays", format: "int" },
  { key: "maxUpStreak", format: "int" },
  { key: "maxDownStreak", format: "int" },
  { key: "observationDays", format: "int" },
  { key: "skewness", format: "ratio" },
  { key: "kurtosis", format: "ratio" },
];

const PERF_METRIC_COMPARE_MODE = {
  intervalReturnPct: "higher",
  annReturnPct: "higher",
  excessReturnPct: "higher",
  sharpe: "higher",
  sortino: "higher",
  calmar: "higher",
  recoveryFactor: "higher",
  maxDrawdownPct: "higher",
  maxDdDurationDays: "lower",
  volPct: "lower",
  downsideVolPct: "lower",
  var95DailyPct: "higher",
  cvar95DailyPct: "higher",
  winRatePct: "higher",
  profitFactor: "higher",
  gainLossRatio: "higher",
  upCapturePct: "higher",
  downCapturePct: "lower",
  beta: "skip",
  corr: "skip",
  trackingErrorPct: "lower",
  bestDayPct: "higher",
  worstDayPct: "higher",
  avgDailyReturnPct: "higher",
  avgWinDayPct: "higher",
  avgLossDayPct: "higher",
  positiveDays: "higher",
  negativeDays: "lower",
  maxUpStreak: "higher",
  maxDownStreak: "lower",
  observationDays: "skip",
  skewness: "skip",
  kurtosis: "skip",
};

function formatPerfMetricCell(raw, format) {
  if (raw === null || raw === undefined || Number.isNaN(Number(raw))) {
    return "—";
  }
  if (format === "ratio") {
    return fmtRatio(raw);
  }
  if (format === "plainPct") {
    return fmtMetricPlainPct(raw);
  }
  if (format === "int") {
    return String(Math.round(Number(raw)));
  }
  return fmtMetricPct(raw);
}

function winnerIndicesForMetric(columns, rowKey) {
  const mode = PERF_METRIC_COMPARE_MODE[rowKey] || "skip";
  if (mode === "skip") {
    return new Set();
  }
  const candidates = columns
    .map((col, index) => {
      if (!col.stats) {
        return { index, value: null };
      }
      const raw = col.stats[rowKey];
      if (raw === null || raw === undefined || Number.isNaN(Number(raw))) {
        return { index, value: null };
      }
      return { index, value: Number(raw) };
    })
    .filter((entry) => entry.value !== null);
  if (candidates.length < 2) {
    return new Set();
  }
  let best = candidates[0];
  for (let i = 1; i < candidates.length; i += 1) {
    const entry = candidates[i];
    if (mode === "higher" && entry.value > best.value) {
      best = entry;
    } else if (mode === "lower" && entry.value < best.value) {
      best = entry;
    }
  }
  const eps = 1e-6;
  const winners = candidates.filter((entry) =>
    Math.abs(entry.value - best.value) <= eps
  );
  if (winners.length >= candidates.length) {
    return new Set();
  }
  return new Set(winners.map((entry) => entry.index));
}

function perfMetricCellMarkup(raw, format, isWinner) {
  const text = formatPerfMetricCell(raw, format);
  if (text === "—") {
    return `<td class="tabular perf-metric-data-cell">—</td>`;
  }
  const badge = isWinner
    ? `<span class="perf-metric-winner" title="${pllT("perf.best")}" aria-label="${pllT("perf.best")}">♛</span>`
    : "";
  const winnerClass = isWinner ? " perf-metric-winner-cell" : "";
  return `<td class="tabular perf-metric-data-cell${winnerClass}"><span class="perf-metric-cell-inner"><span class="perf-metric-value">${text}</span><span class="perf-metric-badge-slot">${badge}</span></span></td>`;
}

function renderPerformanceMetrics(snapshot) {
  const root = document.getElementById("perf-metrics-root");
  const rangeEl = document.getElementById("perf-metrics-range");
  if (!root) {
    return;
  }
  const aligned = extractAlignedNavSeries(snapshot);
  if (!aligned) {
    root.innerHTML = emptyState("empty.perf_history");
    if (rangeEl) {
      rangeEl.textContent = "—";
    }
    return;
  }
  if (rangeEl) {
    rangeEl.textContent = `${aligned.fromLabel} → ${aligned.toLabel}`;
  }
  const metricRows = PERF_METRIC_ROWS;
  const benchLevels = aligned.series.spy_shadow || [];
  const columns = PERF_METRIC_SERIES.map((meta) => {
    const levels = aligned.series[meta.id] || [];
    const base = performanceRiskStats(levels);
    if (!base) {
      return { ...meta, stats: null };
    }
    if (meta.id === "spy_shadow") {
      return {
        ...meta,
        stats: {
          ...base,
          excessReturnPct: 0,
          informationRatio: null,
          beta: 1,
          corr: 1,
          trackingErrorPct: 0,
          upCapturePct: 100,
          downCapturePct: 100,
        },
      };
    }
    const rel = performanceRelativeStats(levels, benchLevels);
    return { ...meta, stats: { ...base, ...(rel || {}) } };
  });
  root.innerHTML = `
    <div class="table-wrap table-scroll perf-metrics-table-wrap">
      <table class="quotes perf-metrics-table">
        <thead>
          <tr>
            <th>${pllT("th.metric")}</th>
            ${columns.map((col) => `<th>${chartSeriesLabel(col.id)}</th>`).join("")}
          </tr>
        </thead>
        <tbody>
          ${metricRows
            .map((row) => {
              const winners = winnerIndicesForMetric(columns, row.key);
              const cells = columns
                .map((col, colIndex) => {
                  const stats = col.stats;
                  if (!stats) {
                    return "<td>—</td>";
                  }
                  const raw = stats[row.key];
                  return perfMetricCellMarkup(raw, row.format, winners.has(colIndex));
                })
                .join("");
              return `<tr><th scope="row">${pllT(`perf.${row.key}`)}</th>${cells}</tr>`;
            })
            .join("")}
        </tbody>
      </table>
    </div>
  `;
  schedulePerfLayoutHeightSync();
}

function benchmarkSummary(snapshot) {
  const held = getHeldRows(snapshot);
  if (!held.length) {
    return { state: "neutral", text: pllT("bench.none") };
  }
  const comparison = samePeriodPerformance(snapshot);
  if (!comparison) {
    return { state: "neutral", text: pllT("bench.insufficient") };
  }
  const navValue = lastDefinedValue(comparison.navChart.datasets[0]?.data);
  const spyValue = lastDefinedValue(
    comparison.combinedChart.datasets.find((row) => row.id === "spy_shadow")?.data
  );
  if (navValue === null || spyValue === null) {
    return { state: "neutral", text: pllT("bench.insufficient") };
  }
  const diff = navValue - spyValue;
  if (Math.abs(diff) < 0.5) {
    return { state: "neutral", text: pllT("bench.flat") };
  }
  if (diff > 0) {
    return {
      state: "good",
      text: pllT("bench.ahead", { n: fmtAmount(diff, 2) }),
    };
  }
  return {
    state: "bad",
    text: pllT("bench.behind", { n: fmtAmount(Math.abs(diff), 2) }),
  };
}

function displayDateChip(raw) {
  if (!raw || typeof raw !== "string") {
    return "—";
  }
  const head = raw.split("T")[0];
  return head.length >= 10 ? head.slice(0, 10) : head;
}

function fmtSignedRatioPercent(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const num = Number(value);
  const sign = num >= 0 ? "+" : "";
  return `${sign}${num.toFixed(digits)}%`;
}

function fmtSignedPtsCompact(value, digits = 2) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) {
    return "—";
  }
  const num = Number(value);
  const sign = num >= 0 ? "+" : "−";
  return `${sign}${Math.abs(num).toFixed(digits)}`;
}

function buildSpyBenchmarkMarkup(snapshot) {
  const s = snapshot.nav_summary?.spy_nav_benchmark_stats;
  if (!s?.ready) {
    return "";
  }
  const pr = s.prior_row;
  const pdFrom = displayDateChip(pr.prior_date);
  const pdTo = displayDateChip(pr.last_date);
  const mvInline =
    pr.mv_usd_delta != null &&
    pr.mv_usd_pct != null &&
    pr.mv_usd_prior != null &&
    pr.mv_usd_last != null
      ? `<span class="spy-compare-dot" aria-hidden="true">·</span><span class="spy-compare-mv">${pllT("spy.total_mv", {
          from: fmtUsd(pr.mv_usd_prior),
          to: fmtUsd(pr.mv_usd_last),
          pct: fmtSignedRatioPercent(pr.mv_usd_pct),
        })}</span>`
      : "";
  const excessPts = pllT("spy.excess_pts", {
    n: fmtSignedPtsCompact(pr.excess_pct_points),
  });
  return (
    '<div class="spy-compare-strip">' +
    `<span class="spy-compare-kicker">${pllT("spy.vs_prior")}</span>` +
    `<span class="spy-compare-range">${pdFrom} → ${pdTo}</span>` +
    '<span class="spy-compare-dot" aria-hidden="true">·</span>' +
    '<span class="spy-compare-metric"><span class="spy-compare-k">NAV</span> ' +
    `<span class="spy-compare-v">${fmtSignedRatioPercent(pr.nav_1d_pct)}</span></span>` +
    '<span class="spy-compare-dot" aria-hidden="true">·</span>' +
    `<span class="spy-compare-metric"><span class="spy-compare-k">${chartSeriesLabel("spy_shadow")}</span> ` +
    `<span class="spy-compare-v">${fmtSignedRatioPercent(pr.spy_1d_pct)}</span></span>` +
    '<span class="spy-compare-dot" aria-hidden="true">·</span>' +
    `<span class="spy-compare-metric"><span class="spy-compare-k">${pllT("spy.excess")}</span> ` +
    `<span class="spy-compare-v">${excessPts}</span></span>` +
    mvInline +
    "</div>"
  );
}

function renderSpyNavBenchmarkPanels(snapshot) {
  const wrapOv = document.getElementById("ov-spy-stats");
  const rootPerf = document.getElementById("perf-spy-stats-root");
  const html = buildSpyBenchmarkMarkup(snapshot);
  if (!html) {
    if (wrapOv) {
      wrapOv.innerHTML = "";
      wrapOv.hidden = true;
    }
    if (rootPerf) {
      rootPerf.innerHTML = "";
      rootPerf.hidden = true;
    }
    scheduleOverviewLayoutHeightSync();
    return;
  }
  if (wrapOv) {
    wrapOv.innerHTML = html;
    wrapOv.hidden = false;
  }
  if (rootPerf) {
    rootPerf.innerHTML = html;
    rootPerf.hidden = false;
  }
  scheduleOverviewLayoutHeightSync();
}

function rebalanceSummary(snapshot) {
  const held = getHeldRows(snapshot);
  if (!held.length) {
    return { state: "neutral", text: pllT("rebalance.unbuilt") };
  }
  if (snapshot.portfolio_view?.rebalance_needed === true) {
    return { state: "warn", text: pllT("rebalance.review") };
  }
  const deferred = snapshot.portfolio_view?.deferred_buy_actions || [];
  if (deferred.length > 0) {
    return {
      state: "neutral",
      text: pllT("rebalance.deferred", { n: deferred.length }),
    };
  }
  if (snapshot.portfolio_view?.rebalance_needed === false) {
    return { state: "good", text: pllT("rebalance.in_band") };
  }
  return { state: "neutral", text: pllT("rebalance.unknown") };
}

function nextFocus(snapshot) {
  const options = [];
  if (snapshot.loan?.next_due_date) {
    options.push({
      date: snapshot.loan.next_due_date,
      text: pllT("focus.payment", { date: snapshot.loan.next_due_date }),
    });
  }
  const phase = nextPhase(snapshot);
  if (phase?.effective_from) {
    options.push({
      date: phase.effective_from,
      text: pllT("focus.phase_switch", { date: phase.effective_from }),
    });
  }
  options.sort((left, right) => compareIsoDate(left.date, right.date));
  return options[0]?.text || pllT("focus.wait_buy");
}

function fxStats(snapshot) {
  const events = snapshot.fx_events || [];
  const twdToUsd = [];
  const usdToTwd = [];
  for (const row of events) {
    if (fxEventDirection(row) === "usd_to_twd") {
      usdToTwd.push(row);
    } else {
      twdToUsd.push(row);
    }
  }
  const totalTwdOut = sumValues(twdToUsd, "twd_amount");
  const totalUsdIn = sumValues(twdToUsd, "usd_amount");
  const totalUsdSold = usdToTwd.reduce(
    (total, row) => total + Math.abs(Number(row.usd_amount || 0)),
    0
  );
  const totalTwdIn = sumValues(usdToTwd, "twd_amount");
  const netUsdDelta = sumValues(events, "usd_amount");
  return {
    count: events.length,
    netUsdDelta,
    twdToUsd: {
      avgRate: totalUsdIn > 1e-9 ? totalTwdOut / totalUsdIn : null,
      count: twdToUsd.length,
      totalTwd: totalTwdOut,
      totalUsd: totalUsdIn,
    },
    usdToTwd: {
      avgRate: totalUsdSold > 1e-9 ? totalTwdIn / totalUsdSold : null,
      count: usdToTwd.length,
      totalTwd: totalTwdIn,
      totalUsdSold,
    },
  };
}

function sleeveRows(snapshot) {
  return snapshot.portfolio_view?.sleeves || [];
}

function quoteMap(snapshot) {
  return new Map(getTrackedRows(snapshot).map((row) => [row.symbol, row]));
}

function recommendationText(sleeve, snapshot) {
  if (!sleeve) {
    return "—";
  }
  if (sleeve.recommendation_mode === "fee_suppressed") {
    return "—";
  }
  if (sleeve.recommendation_mode === "await_first_buy") {
    return pllT("rec.await_build", { pct: fmtPct(sleeve.target_pct) });
  }
  if (sleeve.recommendation_mode === "defer_fee_buy") {
    const d = sleeve.delta_mv_usd != null ? fmtUsd(Math.abs(Number(sleeve.delta_mv_usd))) : "—";
    return pllT("rec.defer_buy", { d });
  }
  if (sleeve.recommendation_mode === "in_band" || sleeve.trade_side === "hold") {
    return pllT("rec.no_change");
  }
  if (sleeve.recommendation_mode === "missing_quote") {
    return pllT("rec.missing_quote");
  }
  if (sleeve.trade_side === "buy") {
    return pllT("rec.buy", { n: fmtUnits(sleeve.trade_units) });
  }
  if (sleeve.trade_side === "sell") {
    return pllT("rec.sell", { n: fmtUnits(sleeve.trade_units) });
  }
  return "—";
}

function rebalanceActionCardHtml(action, snapshot) {
  const sleeve = action.sleeve;
  const sideLabel = tradeSideLabel(action.trade_side);
  const units =
    action.trade_units != null ? fmtAmount(Number(action.trade_units), 2) : "—";
  const policy = snapshot?.portfolio_view?.buy_fee_policy;
  const feeUsd = policy?.broker_fee_usd_per_trade;
  const tgt =
    action.target_pct != null
      ? fmtPct(action.target_pct)
      : sleeve
        ? fmtPct(sleeve.target_pct)
        : "—";
  const cur = sleeve ? fmtPct(sleeve.current_pct) : "—";
  const feeBit =
    feeUsd != null && !Number.isNaN(Number(feeUsd))
      ? pllT("rec.fee", { fee: fmtUsd(Number(feeUsd)) })
      : "";
  const meta = [feeBit, pllT("rec.target_current", { tgt, cur })].filter(Boolean).join(" · ");
  return `
    <article class="rebalance-action-item rebalance-action-item-simple">
      <div class="rebalance-action-primary">
        <span class="rebalance-action-symbol">${action.symbol}</span>
        <span class="rebalance-action-side">${sideLabel} ${units} ${pllT("trade.shares")}</span>
      </div>
      <div class="rebalance-action-amount">
        ${moneyPairUsdPrimaryHtml(snapshot, Math.abs(action.delta_mv_usd))}
      </div>
      <p class="rebalance-action-meta">${meta}</p>
    </article>
  `;
}

function rebalanceDeferredCardHtml(row, snapshot) {
  const gap = moneyPairUsdPrimaryHtml(snapshot, Math.abs(row.delta_mv_usd ?? 0));
  const minU =
    row.buy_fee_min_notional_usd != null ? fmtUsd(row.buy_fee_min_notional_usd) : "—";
  return `
    <article class="rebalance-action-item rebalance-action-item-simple rebalance-action-item-deferred">
      <div class="rebalance-action-primary">
        <span class="rebalance-action-symbol">${row.symbol}</span>
        <span class="rebalance-action-side">${pllT("rec.defer_later")}</span>
      </div>
      <p class="rebalance-action-meta">${pllT("rec.gap_min", { gap, min: minU })}</p>
    </article>
  `;
}

function renderOverviewPositionTable(snapshot) {
  const root = document.getElementById("overview-position-root");
  if (!root) {
    return;
  }
  const sleeves = sleeveRows(snapshot);
  const quotes = quoteMap(snapshot);
  if (!sleeves.length) {
    root.innerHTML = emptyState("empty.no_positions");
    return;
  }
  root.innerHTML = `
    <div class="overview-pos-grid pll-scroll" role="table" aria-label="${pllT("section.positions_table")}">
      <div class="overview-pos-row overview-pos-head" role="row">
        <div class="ov-col ov-col-sym" role="columnheader">${pllT("th.symbol")}</div>
        <div class="ov-col ov-col-pct" role="columnheader">${pllT("th.target")}</div>
        <div class="ov-col ov-col-pct" role="columnheader">${pllT("th.current")}</div>
        <div class="ov-col ov-col-money" role="columnheader">${pllT("th.entry_avg")}</div>
        <div class="ov-col ov-col-money" role="columnheader">${pllT("th.last_price")}</div>
        <div class="ov-col ov-col-mv" role="columnheader">${pllT("th.mv")}</div>
        <div class="ov-col ov-col-pnl" role="columnheader">${pllT("th.unrealized")}</div>
        <div class="ov-col ov-col-units" role="columnheader">${pllT("th.units")}</div>
        <div class="ov-col ov-col-advice" role="columnheader">${pllT("th.advice")}</div>
      </div>
      ${sleeves
        .map((sleeve) => {
          const quote = quotes.get(sleeve.symbol);
          const entryCell =
            quote?.listed === false || quote?.avg_entry_usd == null
              ? "—"
              : `${fmtUsd(quote.avg_entry_usd)} USD`;
          const lastCell =
            quote?.listed === false
              ? pllT("stock.unlisted")
              : quote?.last_usd != null
                ? `${fmtUsd(quote.last_usd)} USD`
                : "—";
          return `
            <div class="overview-pos-row" role="row">
              <div class="ov-col ov-col-sym sym" role="cell">${sleeve.symbol}</div>
              <div class="ov-col ov-col-pct" role="cell">${fmtPct(sleeve.target_pct)}</div>
              <div class="ov-col ov-col-pct" role="cell">${fmtPct(sleeve.current_pct)}</div>
              <div class="ov-col ov-col-money" role="cell">${entryCell}</div>
              <div class="ov-col ov-col-money" role="cell">${lastCell}</div>
              <div class="ov-col ov-col-mv" role="cell">${formatPositionMvCell(sleeve)}</div>
              <div class="ov-col ov-col-pnl" role="cell">${quote ? formatPositionUnrealizedCell(quote) : "—"}</div>
              <div class="ov-col ov-col-units" role="cell">${fmtUnits(quote?.units ?? sleeve.current_units)}</div>
              <div class="ov-col ov-col-advice" role="cell">
                <div class="action-cell action-cell-compact action-cell-overview">
                  <span class="${portfolioStatusClass(sleeve.status)}">${portfolioStatusLabel(
                    sleeve.status,
                    true
                  )}</span>
                  <span class="action-cell-text">${recommendationText(sleeve, snapshot)}</span>
                </div>
              </div>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
  scheduleOverviewLayoutHeightSync();
}

function renderRebalanceActions(snapshot, rootId) {
  const root = document.getElementById(rootId);
  if (!root) {
    return;
  }
  const sleeves = sleeveRows(snapshot);
  const actions = (snapshot.portfolio_view?.rebalance_actions || []).map((action) => {
    const sleeve = sleeves.find((row) => row.symbol === action.symbol);
    return { ...action, sleeve };
  });
  if (!sleeves.length) {
    root.innerHTML = emptyState("empty.no_allocation");
    return;
  }
  const deferred = snapshot.portfolio_view?.deferred_buy_actions || [];
  const deferredBlock =
    deferred.length === 0
      ? ""
      : `
    <div class="rebalance-deferred-block">
      <p class="rebalance-deferred-title">${pllT("rebalance.deferred_title")}</p>
      <div class="rebalance-action-list">
        ${deferred.map((row) => rebalanceDeferredCardHtml(row, snapshot)).join("")}
      </div>
    </div>
  `;

  if (!actions.length) {
    if (sleeves.every((row) => row.recommendation_mode === "await_first_buy")) {
      root.innerHTML = `
        <div class="rebalance-action-list">
          ${sleeves
            .map(
              (sleeve) => `
                <article class="rebalance-action-item">
                  <div class="rebalance-action-line">
                    <strong>${sleeve.symbol}</strong>
                    <span>${fmtPct(sleeve.target_pct)}</span>
                  </div>
                  <p class="rebalance-action-note">${pllT("rebalance.await_build_note")}</p>
                </article>
              `
            )
            .join("")}
        </div>
      `;
      return;
    }
    if (!deferred.length) {
      root.innerHTML = emptyState("empty.no_rebalance");
      return;
    }
    root.innerHTML = deferredBlock;
    return;
  }
  root.innerHTML = `
    <div class="rebalance-action-list rebalance-action-list-simple">
      ${actions.map((action) => rebalanceActionCardHtml(action, snapshot)).join("")}
    </div>
    ${deferredBlock}
  `;
}

function renderLoanSnapshot(snapshot) {
  const debtUsd = liveUsdFromTwd(snapshot, snapshot.loan?.outstanding_twd);
  const marketUsd =
    snapshot.investment_mv_usd != null ? Number(snapshot.investment_mv_usd) : null;
  const coverageRatio =
    debtUsd != null && debtUsd > 0 && marketUsd != null ? marketUsd / debtUsd : null;

  if (isEnLocale()) {
    setText(
      "ov-loan-main",
      debtUsd == null ? "—" : `USD ${fmtUsdSigned(debtUsd)}`
    );
    setText("ov-loan-sub", "");
    setText(
      "ov-loan-next-payment",
      snapshot.loan?.next_due_date
        ? `${snapshot.loan.next_due_date} · USD ${fmtUsd(
            liveUsdFromTwd(snapshot, snapshot.loan.next_due_amount_twd)
          )}`
        : "—"
    );
  } else {
    setText(
      "ov-loan-main",
      snapshot.loan?.outstanding_twd == null ? "—" : `TWD ${fmtTwd(snapshot.loan.outstanding_twd)}`
    );
    setText("ov-loan-sub", "");
    setText(
      "ov-loan-next-payment",
      snapshot.loan?.next_due_date
        ? `${snapshot.loan.next_due_date} · TWD\u00a0${fmtTwd(snapshot.loan.next_due_amount_twd)}`
        : "—"
    );
  }
  const sub = document.getElementById("ov-loan-sub");
  if (sub) {
    sub.hidden = true;
  }
  setText(
    "ov-loan-breakdown",
    snapshot.loan?.next_due_principal_twd == null && snapshot.loan?.next_due_interest_twd == null
      ? "—"
      : isEnLocale()
        ? `${fmtUsd(liveUsdFromTwd(snapshot, snapshot.loan?.next_due_principal_twd))}\u00a0/\u00a0${fmtUsd(
            liveUsdFromTwd(snapshot, snapshot.loan?.next_due_interest_twd)
          )}`
        : `${fmtTwd(snapshot.loan?.next_due_principal_twd)}\u00a0/\u00a0${fmtTwd(
            snapshot.loan?.next_due_interest_twd
          )}`
  );
  setText(
    "ov-loan-after",
    snapshot.loan?.outstanding_after_next_due_twd == null
      ? "—"
      : isEnLocale()
        ? `USD\u00a0${fmtUsd(
            liveUsdFromTwd(snapshot, snapshot.loan.outstanding_after_next_due_twd)
          )}`
        : `TWD\u00a0${fmtTwd(snapshot.loan.outstanding_after_next_due_twd)}`
  );
  setText(
    "ov-loan-coverage",
    coverageRatio == null ? pllT("coverage.none") : fmtPct(coverageRatio * 100)
  );
}

function renderErrors(snapshot) {
  const box = document.getElementById("errors");
  if (!box) {
    return;
  }
  if (snapshot.errors?.length) {
    box.textContent = pllT("errors.warn", {
      msg: snapshot.errors.join(isEnLocale() ? "; " : "；"),
    });
    box.hidden = false;
    return;
  }
  box.hidden = true;
}

function emptyState(i18nKey) {
  return `<div class="empty-state">${pllT(i18nKey)}</div>`;
}

function renderHeldPositions(snapshot) {
  const root = document.getElementById("positions-root");
  if (!root) {
    return;
  }
  const tracked = getTrackedRows(snapshot);
  const sleeveBySymbol = new Map(sleeveRows(snapshot).map((row) => [row.symbol, row]));
  if (!tracked.length) {
    root.innerHTML = emptyState("empty.no_tracked");
    return;
  }
  root.innerHTML = `
    <div class="overview-pos-grid portfolio-pos-grid portfolio-pos-panel" role="table" aria-label="${pllT("section.positions_table")}">
      <div class="overview-pos-row overview-pos-head" role="row">
        <div class="ov-col ov-col-sym" role="columnheader">${pllT("th.symbol")}</div>
        <div class="ov-col ov-col-pct" role="columnheader">${pllT("th.target")}</div>
        <div class="ov-col ov-col-pct" role="columnheader">${pllT("th.current")}</div>
        <div class="ov-col ov-col-money" role="columnheader">${pllT("th.entry_avg")}</div>
        <div class="ov-col ov-col-pnl" role="columnheader">${pllT("th.unrealized")}</div>
        <div class="ov-col ov-col-money" role="columnheader">${pllT("th.last_price")}</div>
        <div class="ov-col ov-col-units" role="columnheader">${pllT("th.units")}</div>
        <div class="ov-col ov-col-advice" role="columnheader">${pllT("th.status")}</div>
      </div>
      ${tracked
        .map((row) => {
          const sleeve = sleeveBySymbol.get(row.symbol);
          const entryCell =
            row.listed === false || row.avg_entry_usd == null
              ? "—"
              : `${fmtUsd(row.avg_entry_usd)} USD`;
          return `
            <div class="overview-pos-row" role="row">
              <div class="ov-col ov-col-sym sym" role="cell">${positionSymbolLabel(row)}</div>
              <div class="ov-col ov-col-pct" role="cell">${fmtPct(sleeve?.target_pct)}</div>
              <div class="ov-col ov-col-pct" role="cell">${fmtPct(sleeve?.current_pct)}</div>
              <div class="ov-col ov-col-money" role="cell">${entryCell}</div>
              <div class="ov-col ov-col-pnl" role="cell">${formatPositionUnrealizedCell(row)}</div>
              <div class="ov-col ov-col-money" role="cell">${fmtUsd(row.last_usd)}</div>
              <div class="ov-col ov-col-units" role="cell">${fmtUnits(row.units)}</div>
              <div class="ov-col ov-col-advice" role="cell">
                <span class="${portfolioStatusClass(sleeve?.status)}">${portfolioStatusLabel(
                  sleeve?.status
                )}</span>
              </div>
            </div>
          `;
        })
        .join("")}
    </div>
  `;
}

let portfolioHistoryTab = "all";

function initPortfolioHistoryTabs() {
  const tablist = document.querySelector(".portfolio-history-tabs");
  if (!tablist) {
    return;
  }
  if (tablist.dataset.bound !== "1") {
    tablist.dataset.bound = "1";
    tablist.addEventListener("click", (event) => {
      const tab = event.target.closest("[data-portfolio-history-tab]");
      if (!tab) {
        return;
      }
      setPortfolioHistoryTab(tab.dataset.portfolioHistoryTab);
    });
  }
  setPortfolioHistoryTab(portfolioHistoryTab);
}

function setPortfolioHistoryTab(tabId) {
  const allowed = new Set(["all", "buy", "sell"]);
  portfolioHistoryTab = allowed.has(tabId) ? tabId : "all";
  document.querySelectorAll("[data-portfolio-history-tab]").forEach((btn) => {
    const active = btn.dataset.portfolioHistoryTab === portfolioHistoryTab;
    btn.classList.toggle("is-active", active);
    btn.setAttribute("aria-selected", active ? "true" : "false");
  });
  document.querySelectorAll("[data-portfolio-history-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.portfolioHistoryPanel !== portfolioHistoryTab;
  });
  const meta = document.getElementById("portfolio-history-meta");
  if (meta) {
    meta.hidden = portfolioHistoryTab !== "sell";
  }
}

function tradeHistoryRowHtml(trade) {
  return `
    <tr>
      <td>${trade.executed_at ? formatExecutedAtDisplay(trade.executed_at) : "—"}</td>
      <td class="sym">${trade.symbol || "—"}</td>
      <td>${tradeSideLabel(trade.side)}</td>
      <td>${trade.units != null ? fmtUnits(trade.units) : "—"}</td>
      <td>${trade.price_usd != null ? `${fmtUsd(trade.price_usd)} USD` : "—"}</td>
      <td>${trade.total_usd != null ? `${fmtUsd(trade.total_usd)} USD` : "—"}</td>
      <td>${trade.fee_usd != null ? `${fmtUsd(trade.fee_usd)} USD` : "—"}</td>
    </tr>
  `;
}

function cardVerticalPadding(card) {
  const style = getComputedStyle(card);
  return (
    (parseFloat(style.paddingTop) || 0) + (parseFloat(style.paddingBottom) || 0)
  );
}

function sectionHeadBlockHeight(card) {
  const head = card.querySelector(".section-head");
  if (!head) {
    return 0;
  }
  const style = getComputedStyle(head);
  return (
    head.offsetHeight +
    (parseFloat(style.marginTop) || 0) +
    (parseFloat(style.marginBottom) || 0)
  );
}

function visibleElementHeight(el) {
  if (!el || el.hidden) {
    return 0;
  }
  const style = getComputedStyle(el);
  return (
    el.offsetHeight +
    (parseFloat(style.marginTop) || 0) +
    (parseFloat(style.marginBottom) || 0)
  );
}

function sideLoanSummaryBlockHeight(loanCard, summaryCard) {
  if (!loanCard || !summaryCard) {
    return 0;
  }
  return (
    summaryCard.offsetTop + summaryCard.offsetHeight - loanCard.offsetTop
  );
}

function syncOverviewLayoutHeights() {
  const chartBox = document.querySelector(".overview-chart-box");
  const chartCard = document.querySelector(".overview-chart-card");
  const loanCard = document.querySelector(".overview-loan-card");
  const summaryCard = document.querySelector(".overview-summary-card");

  if (!chartBox || !chartCard) {
    return;
  }

  chartCard.style.height = "";
  chartCard.style.minHeight = "";
  chartCard.style.maxHeight = "";
  chartBox.style.height = "";
  chartBox.style.minHeight = "";
  chartBox.style.maxHeight = "";
  chartBox.style.flex = "";

  if (window.innerWidth < 920 || !loanCard || !summaryCard) {
    resizeChartInBox(chartBox);
    return;
  }

  const blockHeight = sideLoanSummaryBlockHeight(loanCard, summaryCard);
  if (blockHeight <= 0) {
    resizeChartInBox(chartBox);
    return;
  }

  const reserved =
    cardVerticalPadding(chartCard) +
    sectionHeadBlockHeight(chartCard) +
    visibleElementHeight(chartCard.querySelector(".spy-compare-wrap"));
  const chartMin = 220;

  chartCard.style.minHeight = `${Math.max(blockHeight, reserved + chartMin)}px`;
  chartBox.style.flex = "1 1 auto";
  chartBox.style.minHeight = `${chartMin}px`;
  chartBox.style.maxHeight = "none";

  resizeChartInBox(chartBox);
}

function scheduleOverviewLayoutHeightSync() {
  requestAnimationFrame(() => {
    syncOverviewLayoutHeights();
    requestAnimationFrame(() => {
      syncOverviewLayoutHeights();
      window.setTimeout(syncOverviewLayoutHeights, 120);
    });
  });
}

function resizeChartInBox(box) {
  const canvas = box?.querySelector("canvas");
  if (!canvas || typeof Chart === "undefined") {
    return;
  }
  const chart = Chart.getChart(canvas);
  if (chart) {
    chart.resize();
  }
}

function syncPerfLayoutHeights() {
  const stack = document.querySelector(
    '.detail-panel[data-detail-panel="performance"]:not([hidden]) .perf-layout-stack'
  );
  if (!stack) {
    return;
  }
  const chartCard = stack.querySelector(".perf-chart-card");
  const chartBox = stack.querySelector(".perf-main-chart");
  if (!chartCard || !chartBox) {
    return;
  }

  chartCard.style.height = "";
  chartCard.style.minHeight = "";
  chartCard.style.maxHeight = "";
  chartBox.style.height = "";
  chartBox.style.minHeight = "";
  chartBox.style.maxHeight = "";

  resizeChartInBox(chartBox);
}

function schedulePerfLayoutHeightSync() {
  requestAnimationFrame(() => {
    syncPerfLayoutHeights();
    requestAnimationFrame(syncPerfLayoutHeights);
  });
}

function renderTradeHistory(snapshot) {
  const root = document.getElementById("trade-history-root");
  if (!root) {
    return;
  }
  const trades = [...tradeRows(snapshot)].sort(compareTradesNewestFirst);
  root.innerHTML = tradeHistoryTableHtml(trades, "empty.no_trades");
}

function renderAllocationTable(snapshot) {
  const root = document.getElementById("alloc-status-root");
  if (!root) {
    return;
  }
  const sleeves = snapshot.portfolio_view?.sleeves || [];
  if (!sleeves.length) {
    root.innerHTML = emptyState("empty.no_allocation");
    return;
  }
  root.innerHTML = `
    <div class="table-wrap">
      <table class="quotes">
        <thead>
          <tr>
            <th>${pllT("th.symbol")}</th>
            <th>${pllT("th.current")}</th>
            <th>${pllT("th.target")}</th>
            <th>${pllT("th.band")}</th>
            <th>${pllT("th.mv")}</th>
            <th>${pllT("th.status")}</th>
          </tr>
        </thead>
        <tbody>
          ${sleeves
            .map(
              (sleeve) => `
                <tr>
                  <td class="sym">${sleeve.symbol}</td>
                  <td>${fmtPct(sleeve.current_pct)}</td>
                  <td>${fmtPct(sleeve.target_pct)}</td>
                  <td>${fmtPct(sleeve.band_low_pct)} - ${fmtPct(sleeve.band_high_pct)}</td>
                  <td>${
                    isEnLocale() && sleeve.mv_usd != null
                      ? `${fmtUsd(sleeve.mv_usd)} USD`
                      : `${fmtTwd(sleeve.mv_twd)} TWD`
                  }</td>
                  <td><span class="${portfolioStatusClass(sleeve.status)}">${portfolioStatusLabel(
                    sleeve.status
                  )}</span></td>
                </tr>
              `
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `;
}

function monthlyContributionNote(snapshot) {
  const mc = snapshot.allocations?.monthly_contribution;
  if (isEnLocale()) {
    return mc?.note || pllT("alloc.contrib_default");
  }
  const raw = mc?.note_zh;
  if (typeof raw !== "string" || !raw.trim()) {
    return pllT("alloc.contrib_default");
  }
  return raw
    .replace(/\bpreferred_ticker\b/gi, "偏好標的")
    .replace(/\bmonthly_contribution\b/gi, "每月再投入設定")
    .replace(/\bbuy_fee_priority_symbols\b/gi, "優先加碼標的");
}

function drawdownPeakDisplayText(drawdown) {
  const parts = [];
  if (drawdown.effective_peak_nav_index != null) {
    parts.push(`${fmtAmount(drawdown.effective_peak_nav_index, 2)} ${pllT("unit.pts")}`);
  } else if (drawdown.effective_peak_twd != null) {
    parts.push(`${fmtTwd(drawdown.effective_peak_twd)} TWD`);
  } else if (drawdown.effective_peak_usd != null) {
    parts.push(`${fmtUsd(drawdown.effective_peak_usd)} USD`);
  } else if (drawdown.peak_investment_value_twd != null) {
    parts.push(`${fmtTwd(drawdown.peak_investment_value_twd)} TWD`);
  } else {
    parts.push(pllT("alloc.not_set"));
  }
  return parts.join(" ");
}

function renderAllocationPhases(snapshot) {
  const root = document.getElementById("alloc-root");
  if (!root) {
    return;
  }
  const phases = [...(snapshot.allocations?.phases || [])].sort((left, right) =>
    compareIsoDateNewestFirst(left.effective_from, right.effective_from)
  );
  if (!phases.length) {
    root.innerHTML = "";
    return;
  }
  root.innerHTML = phases
    .map((phase, index) => {
      const priorPhase = phases[index + 1] || null;
      const reason = phaseTransitionReason(phase);
      const reasonHtml = reason
        ? `<details class="alloc-phase-reason">
            <summary>${pllT("alloc.reason_summary")}</summary>
            <p>${String(reason)
              .replace(/&/g, "&amp;")
              .replace(/</g, "&lt;")
              .replace(/>/g, "&gt;")}</p>
          </details>`
        : "";
      const deltaHint = priorPhase
        ? `<p class="alloc-phase-delta-hint">${pllT("alloc.vs_prior", {
            id: priorPhase.id || "—",
          })}</p>`
        : `<p class="alloc-phase-delta-hint">${pllT("alloc.baseline")}</p>`;
      return `
        <article class="sub-card alloc-phase-card">
          <span class="sub-card-label">${phase.id || "phase"}</span>
          <strong class="sub-card-value">${phase.effective_from || "—"} → ${
        phase.effective_to || "—"
      }</strong>
          ${deltaHint}
          <div class="phase-targets" aria-label="Target weights">${phaseTargetsChipsWithDeltaHtml(
        phase,
        priorPhase
      )}</div>
          ${reasonHtml}
        </article>
      `;
    })
    .join("");
}

function renderDrawdown(snapshot) {
  const root = document.getElementById("dd-dl");
  if (!root) {
    return;
  }
  const drawdown = snapshot.drawdown_reinvest || {};
  const rows = [
    [pllT("alloc.monthly"), monthlyContributionNote(snapshot)],
    [
      pllT("alloc.drawdown"),
      drawdown.trigger_drawdown_from_peak_pct != null
        ? fmtRatioPct(drawdown.trigger_drawdown_from_peak_pct)
        : "—",
    ],
    [pllT("alloc.drawdown_peak"), drawdownPeakDisplayText(drawdown)],
    [
      pllT("alloc.drawdown_now"),
      drawdown.current_vs_peak_pct != null ? fmtPct(drawdown.current_vs_peak_pct) : "—",
    ],
  ];
  root.innerHTML = rows
    .map(
      ([label, value]) => `
        <dt>${label}</dt>
        <dd>${value}</dd>
      `
    )
    .join("");
}

function renderLoan(snapshot) {
  const root = document.getElementById("loan-info-root");
  if (!root) {
    return;
  }
  const loan = snapshot.loan;
  if (!loan) {
    root.innerHTML = "";
    return;
  }
  const termMonths = Number(loan.term_months) || 0;
  const paymentsDone = Number(loan.payments_assumed_count) || 0;
  const principalPaid = Number(loan.cumulative_principal_paid_twd) || 0;
  const contractPrincipal = Number(loan.contract_principal_twd) || 0;
  const termPct = loanProgressPct(paymentsDone, termMonths);
  const principalPct = loanProgressPct(principalPaid, contractPrincipal);
  const outstanding = loan.outstanding_twd;

  const kpiUnit = isEnLocale() ? "USD" : "TWD";
  const kpiOutstanding = isEnLocale()
    ? formatLoanTwdDisplay(snapshot, outstanding)
    : fmtTwd(outstanding);
  const kpiPrincipalPaid = isEnLocale()
    ? formatLoanTwdDisplay(snapshot, principalPaid)
    : fmtTwd(principalPaid);
  root.innerHTML = `
    <div class="loan-kpi-row">
      <article class="loan-kpi loan-kpi-primary">
        <span class="loan-kpi-label">${pllT("loan.approx")}</span>
        <strong class="loan-kpi-value">${kpiOutstanding}</strong>
        <span class="loan-kpi-unit">${kpiUnit}</span>
      </article>
      <article class="loan-kpi">
        <span class="loan-kpi-label">${pllT("loan.next")}</span>
        <strong class="loan-kpi-value">${loan.next_due_date || "—"}</strong>
        <span class="loan-kpi-note">${formatLoanTwdDisplay(snapshot, loan.next_due_amount_twd)}</span>
      </article>
      <article class="loan-kpi">
        <span class="loan-kpi-label">${pllT("loan.paid_principal")}</span>
        <strong class="loan-kpi-value">${kpiPrincipalPaid}</strong>
        <span class="loan-kpi-note">${
          principalPct == null
            ? "—"
            : pllT("loan.principal_pct", { n: principalPct.toFixed(1) })
        }</span>
      </article>
    </div>
    <div class="loan-dl-sections">
      ${loanDlSectionHtml(pllT("loan.next_block"), [
        [pllT("loan.due_date"), loan.next_due_date || "—"],
        [pllT("loan.period_principal"), formatLoanTwdDisplay(snapshot, loan.next_due_principal_twd)],
        [pllT("loan.period_interest"), formatLoanTwdDisplay(snapshot, loan.next_due_interest_twd)],
        [pllT("loan.after_payment"), formatLoanTwdDisplay(snapshot, loan.outstanding_after_next_due_twd)],
        [pllT("loan.monthly_due"), formatLoanTwdDisplay(snapshot, loan.monthly_payment_twd)],
      ])}
      ${loanDlSectionHtml(pllT("loan.terms"), [
        [pllT("loan.contract_principal"), formatLoanTwdDisplay(snapshot, loan.contract_principal_twd)],
        [pllT("loan.annual_rate"), fmtRatioPct(loan.annual_nominal_rate)],
        [pllT("loan.first_due"), loan.first_due_date || "—"],
        [
          pllT("loan.lock_in"),
          loan.lock_in_months ? pllT("loan.lock_months", { n: loan.lock_in_months }) : "—",
        ],
        [
          pllT("loan.total_terms"),
          loan.term_months ? pllT("loan.terms_count", { n: loan.term_months }) : "—",
        ],
      ])}
      ${loanDlSectionHtml(pllT("loan.cumulative"), [
        [pllT("loan.paid_principal"), formatLoanTwdDisplay(snapshot, loan.cumulative_principal_paid_twd)],
        [pllT("loan.paid_interest"), formatLoanTwdDisplay(snapshot, loan.cumulative_interest_paid_twd)],
      ])}
    </div>
    <div class="loan-progress-block">
      <p class="loan-progress-heading">${pllT("loan.progress")}</p>
      ${loanProgressBarHtml(
        pllT("loan.term_progress"),
        termMonths
          ? pllT("loan.term_ratio", { done: paymentsDone, total: termMonths })
          : "—",
        termPct
      )}
      ${loanProgressBarHtml(
        pllT("th.principal"),
        contractPrincipal
          ? `${formatLoanTwdDisplay(snapshot, principalPaid)} / ${formatLoanTwdDisplay(snapshot, contractPrincipal)}`
          : "—",
        principalPct
      )}
    </div>
  `;
}

function renderLoanComputedTable(snapshot) {
  const caption = document.getElementById("loan-computed-caption");
  const tbody = document.getElementById("loan-computed-body");
  if (!tbody) {
    return;
  }
  const computed = snapshot.loan_schedule_computed || {};
  if (caption) {
    const cap = isEnLocale()
      ? computed.caption_en || computed.caption || ""
      : computed.caption_zh || computed.caption || "";
    caption.textContent = cap;
    caption.hidden = !cap || (isEnLocale() && hasCjk(cap));
  }
  const today = referenceTodayFromSnapshot(snapshot);
  const rows = [...(computed.rows || [])].sort((left, right) =>
    compareDateClosestTodayFirst(left.payment_date, right.payment_date, today)
  );
  if (!rows.length) {
    tbody.innerHTML = `<tr><td colspan="7">${pllT("empty.no_data")}</td></tr>`;
    return;
  }
  tbody.innerHTML = rows
    .map(
      (row) => `
        <tr>
          <td>${row.period}</td>
          <td>${row.payment_date || "—"}</td>
          <td>${row.days != null ? row.days : "—"}</td>
          <td>${fmtTwd(row.payment_twd)}</td>
          <td>${fmtTwd(row.principal_twd)}</td>
          <td>${fmtTwd(row.interest_twd)}</td>
          <td>${fmtTwd(row.balance_after_twd)}</td>
        </tr>
      `
    )
    .join("");
}

function fxEventSortKey(event) {
  const day = event.date || "";
  const tl = event.time_local != null ? String(event.time_local).trim() : "";
  if (!tl) {
    return `${day}T00:00:00`;
  }
  const parts = tl.split(":");
  if (parts.length === 2) {
    return `${day}T${parts[0].padStart(2, "0")}:${parts[1].padStart(2, "0")}:00`;
  }
  return `${day}T${tl}`;
}

function renderFxTable(snapshot) {
  const bodyTwdToUsd = document.getElementById("fx-body-twd-to-usd");
  const bodyUsdToTwd = document.getElementById("fx-body-usd-to-twd");
  if (!bodyTwdToUsd || !bodyUsdToTwd) {
    return;
  }
  const events = snapshot.fx_events || [];
  const sortFx = (left, right) =>
    fxEventSortKey(right).localeCompare(fxEventSortKey(left));
  const twdToUsd = events.filter((row) => fxEventDirection(row) === "twd_to_usd").sort(sortFx);
  const usdToTwd = events.filter((row) => fxEventDirection(row) === "usd_to_twd").sort(sortFx);
  const emptyRow = `<tr><td colspan="5" class="fx-history-empty">${pllT("empty.no_fx")}</td></tr>`;

  if (!events.length) {
    bodyTwdToUsd.innerHTML = emptyRow;
    bodyUsdToTwd.innerHTML = emptyRow;
    return;
  }

  bodyTwdToUsd.innerHTML = twdToUsd.length
    ? twdToUsd
        .map(
          (event) => `
        <tr>
          <td>${event.date || "—"}</td>
          <td>${event.time_local || "—"}</td>
          <td>${fmtTwd(event.twd_amount)}</td>
          <td>${fmtRate(event.rate_twd_per_usd)}</td>
          <td>${fmtUsd(event.usd_amount)}</td>
        </tr>`
        )
        .join("")
    : emptyRow;

  bodyUsdToTwd.innerHTML = usdToTwd.length
    ? usdToTwd
        .map((event) => {
          const usdSold = Math.abs(Number(event.usd_amount || 0));
          return `
        <tr>
          <td>${event.date || "—"}</td>
          <td>${event.time_local || "—"}</td>
          <td>${fmtUsd(usdSold)}</td>
          <td>${fmtRate(event.rate_twd_per_usd)}</td>
          <td>${fmtTwd(event.twd_amount)}</td>
        </tr>`;
        })
        .join("")
    : emptyRow;
}

function portfolioStatusLabel(status, brief = false) {
  if (status === null || status === undefined) {
    return pllT("status.disabled");
  }
  if (status === "pending") {
    return brief ? pllT("status.pending_short") : pllT("status.pending");
  }
  if (status === "low_fee_deferred") {
    return brief ? pllT("status.deferred_short") : pllT("status.deferred");
  }
  if (status === "low") {
    return pllT("status.low");
  }
  if (status === "high") {
    return pllT("status.high");
  }
  return brief ? pllT("status.ok_short") : pllT("status.ok");
}

function portfolioStatusClass(status) {
  if (status === null || status === undefined) {
    return "pv-status pv-pending";
  }
  if (status === "pending") {
    return "pv-status pv-pending";
  }
  if (status === "low_fee_deferred") {
    return "pv-status pv-defer";
  }
  if (status === "low") {
    return "pv-status pv-low";
  }
  if (status === "high") {
    return "pv-status pv-high";
  }
  return "pv-status pv-ok";
}

function renderLineChart(canvas, chartBlock, yAxisText) {
  const labels = chartBlock?.labels || [];
  const datasets = chartBlock?.datasets || [];
  if (!labels.length || !datasets.length) {
    return null;
  }
  return new Chart(canvas, {
    type: "line",
    data: {
      labels,
      datasets: datasets.map((dataset) => ({
        backgroundColor: "transparent",
        borderColor: dataset.borderColor || CHART_COLORS[dataset.id] || "#8c765f",
        borderWidth: 2.2,
        data: dataset.data,
        label: dataset.label,
        pointRadius: 0,
        spanGaps: true,
        tension: 0.18,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: "index" },
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: THEME.inkSoft,
            font: { family: "Noto Sans TC" },
            usePointStyle: true,
          },
        },
        tooltip: {
          backgroundColor: THEME.tooltipBg,
          borderColor: THEME.tooltipBorder,
          borderWidth: 1,
          titleColor: "#fff7eb",
          bodyColor: "#f1e6d7",
        },
      },
      scales: {
        x: {
          ticks: { color: THEME.inkSoft, maxTicksLimit: 8 },
          grid: { color: THEME.grid },
        },
        y: {
          ticks: { color: THEME.inkSoft },
          grid: { color: THEME.grid },
          title: {
            display: true,
            text: yAxisText,
            color: THEME.inkSoft,
            font: { family: "Noto Sans TC", size: 11 },
          },
        },
      },
    },
  });
}

function showChartEmpty(container, i18nKey) {
  container.innerHTML = emptyState(i18nKey);
}

function renderOverviewPerformanceChart(snapshot) {
  const root = document.getElementById("overview-performance-chart");
  if (!root) {
    return;
  }

  const comparison = samePeriodPerformance(snapshot);
  if (!comparison) {
    showChartEmpty(root, "empty.compare_chart");
    return;
  }

  if (typeof Chart === "undefined") {
    showChartEmpty(root, "empty.chart_module");
    return;
  }

  root.innerHTML = "";
  const canvas = document.createElement("canvas");
  root.appendChild(canvas);
  const chart = renderLineChart(canvas, comparison.combinedChart, pllT("chart.index_base"));
  if (chart) {
    chart.options.maintainAspectRatio = false;
    chart.resize();
  }
  scheduleOverviewLayoutHeightSync();
}

function renderPerformanceCharts(snapshot) {
  const navBox = document.getElementById("nav-chart-container");
  const metricsRoot = document.getElementById("perf-metrics-root");
  if (!navBox) {
    return;
  }
  const comparison = samePeriodPerformance(snapshot);
  if (!comparison) {
    showChartEmpty(navBox, "empty.nav_chart");
    if (metricsRoot) {
      metricsRoot.innerHTML = emptyState("empty.perf_history");
    }
    return;
  }
  navBox.innerHTML = "";
  const combinedCanvas = document.createElement("canvas");
  navBox.appendChild(combinedCanvas);
  const chart = renderLineChart(combinedCanvas, comparison.combinedChart, pllT("chart.index_base"));
  if (chart) {
    chart.options.maintainAspectRatio = false;
    chart.resize();
  }
  renderPerformanceMetrics(snapshot);
  schedulePerfLayoutHeightSync();
}

function renderOverview(snapshot) {
  const held = getHeldRows(snapshot);
  const trades = tradeRows(snapshot);
  const benchmark = benchmarkSummary(snapshot);
  const rebalance = rebalanceSummary(snapshot);
  const phase = activePhase(snapshot);
  const next = nextPhase(snapshot);
  const recordHealth = snapshot.record_health || {};
  const investmentCost = snapshot.investment_cost || {};
  const netWorth = snapshot.net_worth || {};
  const realAssetsTwd = netWorth.net_worth_twd;
  const marketAssetsTwd = netWorth.investment_positions_twd;
  const cashAssetsTwd = netWorth.cash_total_twd;
  const liabilitiesTwd = netWorth.liabilities_twd;
  const realAssetsUsd = liveUsdFromTwd(snapshot, realAssetsTwd);
  const unrealizedPnlTwd =
    investmentCost.unrealized_pnl_twd != null
      ? Number(investmentCost.unrealized_pnl_twd)
      : snapshot.nav_summary?.unrealized_pnl_usd != null
        ? liveTwdFromUsd(snapshot, Number(snapshot.nav_summary.unrealized_pnl_usd))
        : null;
  const marketAssetsUsd =
    snapshot.investment_mv_usd != null
      ? Number(snapshot.investment_mv_usd)
      : liveUsdFromTwd(snapshot, marketAssetsTwd);
  const unrealizedPnlUsd =
    snapshot.nav_summary?.unrealized_pnl_usd != null
      ? Number(snapshot.nav_summary.unrealized_pnl_usd)
      : liveUsdFromTwd(snapshot, unrealizedPnlTwd);
  const cashAssetsUsd = liveUsdFromTwd(snapshot, cashAssetsTwd);
  const liabilitiesUsd = liveUsdFromTwd(snapshot, liabilitiesTwd);

  setText("meta-generated", snapshot.generated_at || "—");
  setPhaseTargetsHtml("ov-phase-targets", phase, "compact");
  setText("ov-next-focus", nextFocus(snapshot));
  setAssetMetric(
    "ov-real-assets",
    "ov-real-assets-alt",
    realAssetsTwd,
    realAssetsUsd,
    "net_worth"
  );
  setAssetMetric(
    "ov-market-assets",
    "ov-market-assets-alt",
    marketAssetsTwd,
    marketAssetsUsd
  );
  const pnlLabel =
    unrealizedPnlTwd == null
      ? "—"
      : unrealizedPnlTwd >= 0
        ? pllT("profit")
        : pllT("loss");
  setState(
    document.getElementById("ov-market-assets-pnl"),
    unrealizedPnlTwd == null
      ? "—"
      : pllT("pnl.unrealized", {
          label: pnlLabel,
          amt: isEnLocale()
            ? fmtUsd(Math.abs(unrealizedPnlUsd || 0))
            : fmtTwd(Math.abs(unrealizedPnlTwd)),
        }),
    unrealizedPnlTwd == null ? "neutral" : unrealizedPnlTwd >= 0 ? "good" : "bad"
  );
  setAssetMetric(
    "ov-cash-assets",
    "ov-cash-assets-alt",
    cashAssetsTwd,
    cashAssetsUsd
  );
  setAssetMetric(
    "ov-remaining-liability",
    "ov-remaining-liability-alt",
    liabilitiesTwd,
    liabilitiesUsd,
    "liability"
  );
  setState(document.getElementById("ov-beat-market"), benchmark.text, benchmark.state);
  setState(document.getElementById("ov-rebalance-pill"), rebalance.text, rebalance.state);
  if (isEnLocale()) {
    setText(
      "ov-liability-chip",
      snapshot.loan?.outstanding_twd == null
        ? "—"
        : `USD ${fmtUsd(liveUsdFromTwd(snapshot, snapshot.loan.outstanding_twd))}`
    );
  } else {
    setText(
      "ov-liability-chip",
      snapshot.loan?.outstanding_twd == null ? "—" : `${fmtTwd(snapshot.loan.outstanding_twd)} TWD`
    );
  }
  PLLocale.hideSubline("ov-liability-chip-note");
  if (isEnLocale()) {
    setText(
      "ov-due-chip",
      snapshot.loan?.next_due_date
        ? `${snapshot.loan.next_due_date} / USD ${fmtUsd(
            liveUsdFromTwd(snapshot, snapshot.loan.next_due_amount_twd)
          )}`
        : "—"
    );
  } else {
    setText(
      "ov-due-chip",
      snapshot.loan?.next_due_date
        ? `${snapshot.loan.next_due_date} / ${fmtTwd(snapshot.loan.next_due_amount_twd)} TWD`
        : "—"
    );
  }
  PLLocale.hideSubline("ov-due-chip-note");
  setText(
    "ov-position-note",
    held.length
      ? pllT("position.built", {
          n: held.length,
          mv: fmtUsd(snapshot.investment_mv_usd),
        })
      : pllT("position.empty")
  );
  const rebalanceActions = snapshot.portfolio_view?.rebalance_actions || [];
  const rebalanceHeadline = document.getElementById("ov-rebalance-headline");
  const rebalanceDetail = document.getElementById("ov-rebalance-detail");
  if (rebalanceActions.length > 0) {
    if (rebalanceHeadline) {
      rebalanceHeadline.hidden = true;
      rebalanceHeadline.textContent = "";
    }
    if (rebalanceDetail) {
      rebalanceDetail.hidden = true;
      rebalanceDetail.textContent = "";
    }
  } else {
    if (rebalanceHeadline) {
      rebalanceHeadline.hidden = false;
      setText(
        "ov-rebalance-headline",
        held.length
          ? rebalance.text
          : `${pllT("ov.await_build")}${
              phase?.targets?.length
                ? ` ${pllT("ov.holdings_count", { n: phase.targets.length })}`
                : ""
            }`
      );
    }
    if (rebalanceDetail) {
      rebalanceDetail.hidden = false;
      setText(
        "ov-rebalance-detail",
        held.length
          ? next?.effective_from
            ? pllT("ov.phase_next", { date: next.effective_from })
            : pllT("ov.hold_config")
          : pllT("ov.pre_build")
      );
    }
  }
  setText("ov-trade-count", pllT("ov.trade_count", { n: trades.length }));
  setText(
    "ov-capital-event-count",
    pllT("ov.trade_count", { n: recordHealth.capital_event_count || 0 })
  );
  setText(
    "ov-cash-snapshot-count",
    recordHealth.latest_cash_snapshot_as_of
      ? pllT("ov.cash_snap", {
          n: recordHealth.cash_snapshot_count || 0,
          date: recordHealth.latest_cash_snapshot_as_of,
        })
      : pllT("ov.trade_count", { n: recordHealth.cash_snapshot_count || 0 })
  );
  setText(
    "ov-rule-count",
    `${recordHealth.rule_event_count || 0} / ${recordHealth.rebalance_log_count || 0}`
  );
  setText("ov-income-count", pllT("ov.trade_count", { n: recordHealth.income_event_count || 0 }));

  renderOverviewPositionTable(snapshot);
  renderOverviewPerformanceChart(snapshot);
  renderSpyNavBenchmarkPanels(snapshot);
  renderRebalanceActions(snapshot, "ov-rebalance-actions-root");
  renderLoanSnapshot(snapshot);

  renderErrors(snapshot);
  PLLocale.applyStaticLabels();
  scheduleOverviewLayoutHeightSync();
}

function renderDetails(snapshot) {
  const held = getHeldRows(snapshot);
  const trades = tradeRows(snapshot);
  const fx = fxStats(snapshot);
  const benchmark = benchmarkSummary(snapshot);
  const phase = activePhase(snapshot);
  const rebalance = rebalanceSummary(snapshot);
  const investmentCost = snapshot.investment_cost || {};
  const investedTwd =
    investmentCost.historical_cost_twd != null
      ? Number(investmentCost.historical_cost_twd)
      : investmentCost.current_fx_equivalent_twd != null
        ? Number(investmentCost.current_fx_equivalent_twd)
        : null;
  const unrealizedPnlUsdFromNav =
    snapshot.nav_summary?.unrealized_pnl_usd != null
      ? Number(snapshot.nav_summary.unrealized_pnl_usd)
      : null;
  const unrealizedPnlUsdDisplay =
    unrealizedPnlUsdFromNav != null && !Number.isNaN(unrealizedPnlUsdFromNav)
      ? unrealizedPnlUsdFromNav
      : investmentCost.unrealized_pnl_twd != null
        ? liveUsdFromTwd(snapshot, Number(investmentCost.unrealized_pnl_twd))
        : null;
  const unrealizedPnlTwd =
    investmentCost.unrealized_pnl_twd != null
      ? Number(investmentCost.unrealized_pnl_twd)
      : liveTwdFromUsd(snapshot, unrealizedPnlUsdDisplay);
  const comp = samePeriodPerformance(snapshot);
  const navIndex = comp
    ? lastDefinedValue(comp.navChart.datasets[0]?.data)
    : snapshot.nav_summary?.nav_index_100 != null
      ? Number(snapshot.nav_summary.nav_index_100)
      : null;

  setText("meta-generated", snapshot.generated_at || "—");

  if (isEnLocale()) {
    const investedUsd =
      investedTwd != null ? liveUsdFromTwd(snapshot, investedTwd) : null;
    setAggregateMetric(
      "portfolio-invested-twd",
      investedTwd,
      investedUsd,
      "positive_good"
    );
    setStockMetric("portfolio-held-mv", snapshot.investment_mv_usd);
    setAggregateMetric(
      "portfolio-unrealized-pnl",
      unrealizedPnlTwd,
      unrealizedPnlUsdDisplay,
      "positive_good"
    );
  } else {
    setText("portfolio-invested-twd", fmtTwd(investedTwd));
    PLLocale.setUnitForMetric("portfolio-invested-twd", "TWD");
    const heldMvTwd = liveTwdFromUsd(snapshot, snapshot.investment_mv_usd);
    setState(
      document.getElementById("portfolio-held-mv"),
      fmtTwd(heldMvTwd),
      numberState(heldMvTwd)
    );
    PLLocale.setUnitForMetric("portfolio-held-mv", "TWD");
    setState(
      document.getElementById("portfolio-unrealized-pnl"),
      fmtTwd(unrealizedPnlTwd),
      numberState(unrealizedPnlTwd)
    );
    PLLocale.setUnitForMetric("portfolio-unrealized-pnl", "TWD");
  }
  applyRealizedPnlUi(snapshot);
  setState(
    document.getElementById("portfolio-nav-index"),
    fmtAmount(navIndex, 2),
    navIndex == null ? "neutral" : navIndex >= 100 ? "good" : "bad"
  );

  setState(document.getElementById("detail-beat-market"), benchmark.text, benchmark.state);
  setText("nav-index-kpi", fmtAmount(navIndex, 2));
  setAggregateMetric(
    "nav-mv-usd",
    liveTwdFromUsd(snapshot, snapshot.nav_summary?.mv_usd),
    snapshot.nav_summary?.mv_usd,
    "positive_good"
  );
  if (isEnLocale()) {
    setAggregateMetric(
      "nav-pnl-usd",
      unrealizedPnlTwd,
      unrealizedPnlUsdDisplay,
      "positive_good"
    );
    setAggregateMetric(
      "loan-out",
      snapshot.loan?.outstanding_twd,
      liveUsdFromTwd(snapshot, snapshot.loan?.outstanding_twd),
      "liability"
    );
    setAggregateMetric(
      "loan-next-principal",
      snapshot.loan?.next_due_principal_twd,
      liveUsdFromTwd(snapshot, snapshot.loan?.next_due_principal_twd)
    );
    setAggregateMetric(
      "loan-next-interest",
      snapshot.loan?.next_due_interest_twd,
      liveUsdFromTwd(snapshot, snapshot.loan?.next_due_interest_twd)
    );
    setAggregateMetric(
      "loan-after-next",
      snapshot.loan?.outstanding_after_next_due_twd,
      liveUsdFromTwd(snapshot, snapshot.loan?.outstanding_after_next_due_twd),
      "liability"
    );
  } else {
    setState(
      document.getElementById("nav-pnl-usd"),
      fmtTwd(unrealizedPnlTwd),
      unrealizedPnlUsdDisplay == null || Number.isNaN(Number(unrealizedPnlUsdDisplay))
        ? "neutral"
        : numberState(Number(unrealizedPnlUsdDisplay))
    );
    PLLocale.setUnitForMetric("nav-pnl-usd", "TWD");
    setText("loan-out", fmtTwd(snapshot.loan?.outstanding_twd));
    setText("loan-next-principal", fmtTwd(snapshot.loan?.next_due_principal_twd));
    setText("loan-next-interest", fmtTwd(snapshot.loan?.next_due_interest_twd));
    setText("loan-after-next", fmtTwd(snapshot.loan?.outstanding_after_next_due_twd));
  }

  setPhaseTargetsHtml("detail-phase-line", phase, "inline");
  setState(document.getElementById("allocation-rebalance-state"), rebalance.text, rebalance.state);
  setText(
    "allocation-band-label",
    snapshot.allocations?.rebalance?.band_relative_to_target != null
      ? fmtRatioPct(snapshot.allocations.rebalance.band_relative_to_target)
      : "—"
  );

  setText("fx-twd-buy-usd-count", String(fx.twdToUsd.count));
  setText(
    "fx-twd-buy-usd-rate",
    fx.twdToUsd.count > 0 ? fmtRate(fx.twdToUsd.avgRate) : "—"
  );
  setText(
    "fx-twd-buy-usd-twd",
    fx.twdToUsd.count > 0 ? fmtTwd(fx.twdToUsd.totalTwd) : "—"
  );
  setText(
    "fx-twd-buy-usd-usd",
    fx.twdToUsd.count > 0 ? fmtUsd(fx.twdToUsd.totalUsd) : "—"
  );
  setText("fx-usd-sell-twd-count", String(fx.usdToTwd.count));
  setText(
    "fx-usd-sell-twd-rate",
    fx.usdToTwd.count > 0 ? fmtRate(fx.usdToTwd.avgRate) : "—"
  );
  setText(
    "fx-usd-sell-twd-usd",
    fx.usdToTwd.count > 0 ? fmtUsd(fx.usdToTwd.totalUsdSold) : "—"
  );
  setText(
    "fx-usd-sell-twd-twd",
    fx.usdToTwd.count > 0 ? fmtTwd(fx.usdToTwd.totalTwd) : "—"
  );
  setText(
    "alloc-status-caption",
    snapshot.allocations?.rebalance?.band_relative_to_target != null
      ? pllT("ov.alloc_band", {
          n: Math.round(Number(snapshot.allocations.rebalance.band_relative_to_target) * 100),
        })
      : "—"
  );

  renderRealizedPnlPanel(snapshot);
  renderHeldPositions(snapshot);
  renderTradeHistory(snapshot);
  renderBuyHistory(snapshot);
  initPortfolioHistoryTabs();
  renderLoan(snapshot);
  renderLoanComputedTable(snapshot);
  renderDrawdown(snapshot);
  renderAllocationTable(snapshot);
  renderRebalanceActions(snapshot, "alloc-action-root");
  renderAllocationPhases(snapshot);
  renderFxTable(snapshot);
  renderSpyNavBenchmarkPanels(snapshot);
  renderErrors(snapshot);
  syncDetailSection(snapshot);
  PLLocale.applyStaticLabels();
  window.addEventListener("hashchange", () => syncDetailSection(snapshot));
}

function currentDetailKey() {
  const key = (window.location.hash || "#performance").replace("#", "");
  return DETAIL_META[key] ? key : "performance";
}

function syncDetailSection(snapshot) {
  if (PAGE !== "details") {
    return;
  }
  const key = currentDetailKey();
  document.querySelectorAll("[data-detail-panel]").forEach((panel) => {
    panel.hidden = panel.dataset.detailPanel !== key;
  });
  document.querySelectorAll("[data-detail-link]").forEach((link) => {
    const active = link.dataset.detailLink === key;
    link.classList.toggle("is-active", active);
    if (active) {
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
  setText("detail-page-title", pllT(DETAIL_META[key].titleKey));
  if (key === "portfolio") {
    setText(
      "detail-page-meta",
      getHeldRows(snapshot).length
        ? pllT("meta.portfolio_built", {
            n: getHeldRows(snapshot).length,
            t: tradeRows(snapshot).length,
          })
        : pllT("meta.not_built")
    );
    initPortfolioHistoryTabs();
    return;
  }
  if (key === "performance") {
    renderPerformanceCharts(snapshot);
    schedulePerfLayoutHeightSync();
    setText("detail-page-meta", benchmarkSummary(snapshot).text);
    return;
  }
  if (key === "loan") {
    setText(
      "detail-page-meta",
      snapshot.loan?.next_due_date
        ? isEnLocale()
          ? pllT("meta.loan_due", {
              date: snapshot.loan.next_due_date,
              p: fmtUsd(liveUsdFromTwd(snapshot, snapshot.loan.next_due_principal_twd)),
              i: fmtUsd(liveUsdFromTwd(snapshot, snapshot.loan.next_due_interest_twd)),
            })
          : pllT("meta.loan_due", {
              date: snapshot.loan.next_due_date,
              p: fmtTwd(snapshot.loan.next_due_principal_twd),
              i: fmtTwd(snapshot.loan.next_due_interest_twd),
            })
        : "—"
    );
    return;
  }
  if (key === "allocation") {
    setText("detail-page-meta", phaseTargetsText(activePhase(snapshot)) || "—");
    return;
  }
  if (key === "fx") {
    const fx = fxStats(snapshot);
    setText(
      "detail-page-meta",
      fx.count
        ? pllT("meta.fx_summary", {
            n: fx.count,
            a: fx.twdToUsd.count,
            b: fx.usdToTwd.count,
          })
        : pllT("meta.no_fx")
    );
  }
}

async function loadSnapshot() {
  if (
    typeof window !== "undefined" &&
    window.__PERSONAL_LEDGER_SNAPSHOT__ &&
    typeof window.__PERSONAL_LEDGER_SNAPSHOT__ === "object"
  ) {
    return window.__PERSONAL_LEDGER_SNAPSHOT__;
  }
  const response = await fetch("data/snapshot.json", { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();
}

async function main() {
  try {
    cachedSnapshot = await loadSnapshot();
    if (PAGE === "overview") {
      renderOverview(cachedSnapshot);
      return;
    }
    renderDetails(cachedSnapshot);
  } catch (error) {
    if (PAGE === "overview") {
      const overviewError = document.getElementById("overview-error");
      if (overviewError) {
        overviewError.textContent = pllT("error.load");
        overviewError.hidden = false;
      }
      return;
    }
    setText("meta-generated", "—");
    const errorBox = document.getElementById("errors");
    if (errorBox) {
      errorBox.textContent = pllT("error.data");
      errorBox.hidden = false;
    }
    const navBox = document.getElementById("nav-chart-container");
    const metricsRoot = document.getElementById("perf-metrics-root");
    if (navBox) {
      showChartEmpty(navBox, "empty.snapshot");
    }
    if (metricsRoot) {
      metricsRoot.innerHTML = emptyState("empty.snapshot");
    }
  }
}

let cachedSnapshot = null;

function rerenderApp() {
  if (!cachedSnapshot) {
    return;
  }
  PLLocale.applyStaticLabels();
  if (PAGE === "overview") {
    renderOverview(cachedSnapshot);
    return;
  }
  renderDetails(cachedSnapshot);
}

document.addEventListener("DOMContentLoaded", () => {
  const ready = () => {
    main();
  };
  PLLocale.initGate(ready);
});
window.addEventListener("resize", () => {
  schedulePerfLayoutHeightSync();
  scheduleOverviewLayoutHeightSync();
});
