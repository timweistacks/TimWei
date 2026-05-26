/** Language gate, i18n strings, and locale-aware display mode for personal-ledger. */
(function initPersonalLedgerLocale(global) {
  const STORAGE_KEY = "personal-ledger-lang";
  const LANG_ZH = "zh-Hant";
  const LANG_EN = "en";
  const URL_LANG_PARAM = "lang";

  function readLangFromUrl() {
    try {
      const params = new URLSearchParams(global.location.search);
      const raw = params.get(URL_LANG_PARAM);
      if (raw === "en") {
        return LANG_EN;
      }
      if (raw === "zh" || raw === "zh-Hant") {
        return LANG_ZH;
      }
    } catch {
      /* ignore */
    }
    return "";
  }

  function syncLangToUrl(lang) {
    try {
      const url = new URL(global.location.href);
      if (lang === LANG_ZH) {
        url.searchParams.delete(URL_LANG_PARAM);
      } else if (lang === LANG_EN) {
        url.searchParams.set(URL_LANG_PARAM, "en");
      }
      global.history.replaceState(null, "", url.toString());
    } catch {
      /* ignore */
    }
  }

  const STRINGS = {
    "layer.equity": { en: "Equity Layer 100%", zh: "股票部位 100%" },
    "layer.equity_label": { en: "Equity Exp.", zh: "股票曝險" },
    "layer.alt_bond": { en: "Alt & Bond Layer 100%", zh: "替代與債券 100%" },
    "layer.alt_bond_label": { en: "Alt & Bond", zh: "替代與債券" },
    "viz.title_3d": { en: "Return Stacking Strategy", zh: "報酬疊加策略拆解" },
    "viz.desc_3d": { en: "This custom configuration leverages 100% principal to get 200% total exposure. Below is the granular breakdown of the double layers (100% Equity + 100% Alt & Bonds).", zh: "此配置由Tim Wei 自製搭建，將 100% 的本金放大一倍，提供 200% 的總資產曝險。以下是為您拆解至最細顆粒度的雙層（股票 100% + 替代與債券 100%）底層持倉與量化策略佔比。" },
    "legend.core": { en: "Equity exposure (100% total)", zh: "股票部位 (總佔比 100%)" },
    "legend.alt": { en: "Alt & Bond exposure (100% total)", zh: "替代與債券部位 (總佔比 100%)" },
    "gate.title": { en: "Choose language", zh: "選擇語言" },
    "gate.subtitle": {
      en: "You can switch anytime from the top bar.",
      zh: "之後可在頂部列隨時切換。",
    },
    "gate.zh": { en: "中文（台幣）", zh: "中文（台幣）" },
    "gate.en": { en: "English (USD)", zh: "English (USD)" },
    "nav.brand": { en: "25y Debt Investing Ledger", zh: "25歲貸款投資實錄" },
    "nav.title": { en: "Return Stacking Lab", zh: "Tim Wei 報酬疊加實驗" },
    "nav.overview": { en: "Overview", zh: "實測總覽" },
    "nav.learn": { en: "Learn", zh: "認識實驗" },
    "nav.layer2": { en: "Layer 2", zh: "第二層策略" },
    "nav.etfs": { en: "ETF Guide", zh: "ETF 百科" },
    "nav.details": { en: "Details", zh: "明細" },
    "nav.lang.zh": { en: "中文", zh: "中文" },
    "nav.lang.en": { en: "EN", zh: "EN" },
    "hero.overview": { en: "Overview", zh: "總覽" },
    "hero.overview_title": { en: "Asset Overview", zh: "資產總覽" },
    "layer.total_exposure": { en: "Total Exp.", zh: "總曝險" },
    "hero.details": { en: "Details", zh: "明細" },
    "meta.snapshot": { en: "Snapshot", zh: "快照" },
    "meta.phase": { en: "Phase", zh: "目前階段" },
    "meta.next": { en: "Next", zh: "下個事件" },
    "metric.real_assets": { en: "Net assets", zh: "真實資產" },
    "metric.market_assets": { en: "Equity holdings", zh: "股市資產" },
    "metric.cash": { en: "Cash", zh: "手上現金" },
    "metric.liability": { en: "Remaining debt", zh: "剩餘負債" },
    "section.overview_assets": { en: "Asset snapshot", zh: "資產快照" },
    "a11y.skip": { en: "Skip to main content", zh: "跳至主要內容" },
    "banner.new.title": { en: "First time here?", zh: "第一次來？" },
    "banner.new.body": {
      en: "This site is the full curriculum: learn Return Stacking and the ETF family first, then explore the live data below. Social posts only highlight a few points; everything lives here.",
      zh: "這個網站是完整教材：先懂 Return Stacking 與 ETF 家族，再看下方實測數據。Threads、FB 等社群貼文只挑重點，完整內容都在這裡。",
    },
    "banner.learn_cta": { en: "Start with Learn", zh: "從認識實驗開始" },
    "banner.etfs_cta": { en: "ETF Guide", zh: "ETF 百科" },
    "banner.dismiss_label": { en: "Dismiss welcome banner", zh: "關閉新訪客提示" },
    "chip.benchmark": { en: "vs market", zh: "大盤比較" },
    "chip.rebalance": { en: "Rebalance", zh: "再平衡" },
    "chip.debt": { en: "Debt", zh: "負債" },
    "chip.due": { en: "Next payment", zh: "下期還款" },
    "section.positions": { en: "Positions", zh: "部位" },
    "section.positions_table": { en: "Current holdings", zh: "目前部位表" },
    "section.nav_vs_spy": { en: "My NAV vs SPY", zh: "我的 NAV vs SPY" },
    "section.compare": { en: "Comparison", zh: "同期比較" },
    "section.rebalance": { en: "Rebalance", zh: "再平衡" },
    "section.rebalance_actions": { en: "Buy / Sell", zh: "應買 / 應賣" },
    "section.loan": { en: "Loan", zh: "貸款" },
    "section.debt_status": { en: "Debt status", zh: "債務現況" },
    "section.summary": { en: "Summary", zh: "摘要" },
    "section.records": { en: "Records", zh: "當前紀錄" },
    "section.social": { en: "Socials", zh: "社群" },
    "section.social_links": { en: "Community & Links", zh: "交流與連結" },
    "social.join_fb": { en: "Join FB Return Stacking Group", zh: "加入 FB 報酬疊加交流社團" },
    "link.view_positions": { en: "Positions", zh: "看部位" },
    "link.view_performance": { en: "Performance", zh: "看績效" },
    "link.view_allocation": { en: "Allocation", zh: "看配置" },
    "link.view_loan": { en: "Debt", zh: "看負債" },
    "link.view_fx": { en: "FX", zh: "看換匯" },
    "detail.performance": { en: "Performance", zh: "績效" },
    "detail.portfolio": { en: "Positions", zh: "部位" },
    "detail.loan": { en: "Debt", zh: "負債" },
    "detail.allocation": { en: "Allocation", zh: "配置" },
    "detail.fx": { en: "FX", zh: "換匯" },
    "label.nav": { en: "NAV", zh: "NAV" },
    "label.vs_spy": { en: "vs SPY", zh: "相對大盤" },
    "label.position_mv": { en: "Position MV", zh: "部位市值" },
    "label.unrealized": { en: "Unrealized P/L", zh: "未實現損益" },
    "label.realized": { en: "Realized P/L (cum.)", zh: "已實現損益（累計）" },
    "label.invested_cost": { en: "Cost basis", zh: "場內成本" },
    "label.holdings_mv": { en: "Holdings MV", zh: "持股市值" },
    "profit": { en: "Gain", zh: "獲利" },
    "loss": { en: "Loss", zh: "虧損" },
    "realized.cum": { en: "Realized (cum.)", zh: "已實現累計" },
    "error.load": { en: "Could not load snapshot", zh: "無法載入快照" },
    "error.data": {
      en: "Data unavailable. Regenerate snapshot.json first.",
      zh: "資料無法載入，請先重新生成 snapshot.json。",
    },
    "chart.summary_a11y": {
      en: "Indexed performance from {start} to {end}. {series}",
      zh: "指數化績效 {start} 至 {end}。{series}",
    },
    "chart.series_latest": {
      en: "{label} latest index {value}",
      zh: "{label} 最新指數 {value}",
    },
    "a11y.chart_overview": {
      en: "NAV vs benchmark indexed performance chart",
      zh: "NAV 與基準指數化績效圖",
    },
    "state.good": { en: "positive", zh: "偏多" },
    "state.bad": { en: "negative", zh: "偏空" },
    "state.warn": { en: "caution", zh: "注意" },
    "state.neutral": { en: "neutral", zh: "中性" },
    "bench.none": { en: "No performance yet", zh: "尚無績效" },
    "bench.insufficient": { en: "Insufficient data", zh: "資料不足" },
    "bench.flat": { en: "About flat vs SPY shadow", zh: "約與 SPY 影子持平" },
    "bench.ahead": { en: "Ahead of SPY shadow by {n}", zh: "領先 SPY 影子 {n}" },
    "bench.behind": { en: "Behind SPY shadow by {n}", zh: "落後 SPY 影子 {n}" },
    "spy.day_ahead": { en: "Beat market yesterday", zh: "昨日贏大盤" },
    "spy.day_behind": { en: "Trailed market yesterday", zh: "昨日輸大盤" },
    "spy.day_flat": { en: "Flat vs market yesterday", zh: "昨日與大盤持平" },
    "rebalance.unbuilt": { en: "Not invested", zh: "未建倉" },
    "rebalance.review": { en: "Review needed", zh: "需檢視" },
    "rebalance.deferred": {
      en: "{n} deferred buy(s) (fee threshold)",
      zh: "含 {n} 筆延後買入（手續費門檻）",
    },
    "rebalance.in_band": { en: "Within band", zh: "容許帶內" },
    "rebalance.unknown": { en: "Not evaluated", zh: "尚未判定" },
    "focus.payment": { en: "Payment {date}", zh: "還款 {date}" },
    "focus.phase_switch": { en: "Phase switch {date}", zh: "配置切換 {date}" },
    "focus.wait_buy": { en: "Awaiting first buy", zh: "等待第一筆買入" },
    "position.built": {
      en: "{n} holdings / USD {mv}",
      zh: "已建倉 {n} 檔 / 持倉 USD {mv}",
    },
    "position.empty": { en: "No holdings yet", zh: "未建倉，先追蹤現行配置" },
    "loan.next": { en: "Next payment", zh: "下期還款" },
    "loan.principal_interest": { en: "Principal / interest", zh: "本金 / 利息" },
    "loan.after": { en: "After payment", zh: "繳後負債" },
    "loan.coverage": { en: "Equity coverage", zh: "股市覆蓋" },
    "loan.approx": { en: "Outstanding", zh: "剩餘負債" },
    "summary.trades": { en: "Trades", zh: "交易筆數" },
    "summary.capital": { en: "Capital events", zh: "資金事件" },
    "summary.cash_snap": { en: "Cash snapshots", zh: "現金快照" },
    "summary.rules": { en: "Rules / rebalance", zh: "規則 / 再平衡" },
    "summary.income": { en: "Income", zh: "配息紀錄" },
    "alloc.active": { en: "Active", zh: "作用中" },
    "alloc.status": { en: "Status", zh: "狀態" },
    "alloc.band": { en: "Band", zh: "容許帶" },
    "alloc.vs_target": { en: "vs target", zh: "相對目標" },
    "alloc.phase_delta_hint": {
      en: "Weight tags show change vs prior phase (percentage points).",
      zh: "權重旁標示為相較前一階段之增減（百分點）",
    },
    "alloc.baseline": { en: "Baseline", zh: "基準配置" },
    "alloc.vs_prior": { en: "vs {id}", zh: "相較 {id}" },
    "loan.progress": { en: "Repayment progress", zh: "還款進度" },
    "loan.terms": { en: "Contract", zh: "合約條款" },
    "loan.cumulative": { en: "Paid to date", zh: "累計償還" },
    "loan.next_block": { en: "Next payment", zh: "下期還款" },
    "fx.twd_usd": { en: "TWD → USD", zh: "台幣 → 美金" },
    "fx.usd_twd": { en: "USD → TWD", zh: "美金 → 台幣" },
    "realized.none": { en: "No sells yet", zh: "尚無賣出紀錄" },
    "coverage.none": { en: "No equity yet", zh: "尚未建倉" },
    "unit.pts": { en: "pts", zh: "點" },
    "unit.trades": { en: "trades", zh: "筆" },
    "trade.buy": { en: "Buy", zh: "買入" },
    "trade.sell": { en: "Sell", zh: "賣出" },
    "trade.shares": { en: "sh", zh: "股" },
    "phase.removed": { en: "Removed", zh: "移除" },
    "phase.added": { en: "New", zh: "新增" },
    "stock.unlisted": { en: "Unlisted", zh: "未上市" },
    "realized.kicker": { en: "Realized", zh: "已實現" },
    "realized.sells": { en: "Sell detail", zh: "賣出明細" },
    "realized.avg_cost": { en: "Average cost", zh: "平均成本法" },
    "th.metric": { en: "Metric", zh: "指標" },
    "th.time": { en: "Time", zh: "時間" },
    "th.symbol": { en: "Symbol", zh: "標的" },
    "th.target": { en: "Target", zh: "目標" },
    "th.current": { en: "Current", zh: "目前" },
    "th.entry_avg": { en: "Avg cost", zh: "入場均價" },
    "th.last_price": { en: "Last", zh: "最新價" },
    "th.unrealized": { en: "Unrealized P/L", zh: "未實現損益" },
    "th.units": { en: "Units", zh: "單位" },
    "th.advice": { en: "Action", zh: "建議" },
    "th.status": { en: "Status", zh: "狀態" },
    "th.band": { en: "Band", zh: "容許帶" },
    "th.mv": { en: "MV", zh: "持股市值" },
    "th.side": { en: "Side", zh: "方向" },
    "th.price": { en: "Price", zh: "價格" },
    "th.notional": { en: "Notional", zh: "成交金額" },
    "th.fee": { en: "Fee", zh: "手續費" },
    "th.shares": { en: "Shares", zh: "股數" },
    "th.net_proceeds": { en: "Net USD", zh: "淨入帳 USD" },
    "th.cost_usd": { en: "Cost USD", zh: "成本 USD" },
    "th.realized_usd": { en: "Realized USD", zh: "已實現 USD" },
    "th.date": { en: "Date", zh: "日期" },
    "th.period": { en: "#", zh: "期" },
    "th.due_date": { en: "Due", zh: "還款日" },
    "th.days": { en: "Days", zh: "天數" },
    "th.payment": { en: "Payment", zh: "還款" },
    "th.principal": { en: "Principal", zh: "本金" },
    "th.interest": { en: "Interest", zh: "利息" },
    "th.balance": { en: "Balance", zh: "餘額" },
    "th.twd_out": { en: "TWD out", zh: "付出台幣" },
    "th.rate": { en: "Rate", zh: "匯率" },
    "th.usd_in": { en: "USD in", zh: "進帳美元" },
    "th.usd_out": { en: "USD sold", zh: "賣出美元" },
    "th.twd_in": { en: "TWD in", zh: "進帳台幣" },
    "chart.nav": { en: "My NAV", zh: "我的 NAV" },
    "chart.spy_shadow": { en: "SPY shadow", zh: "SPY 影子" },
    "chart.sso_shadow": { en: "SSO 2x shadow", zh: "SSO 正二影子" },
    "chart.index_base": {
      en: "Indexed",
      zh: "區間指數",
    },
    "chart.portfolio_nav": { en: "Portfolio NAV", zh: "組合 NAV" },
    "spy.vs_prior": { en: "vs prior day", zh: "較前一日" },
    "spy.total_mv": { en: "Total MV USD {from} → {to} ({pct})", zh: "總市值 USD {from} → {to}（{pct}）" },
    "spy.excess": { en: "Excess", zh: "超額" },
    "spy.excess_pts": { en: "{n} pts", zh: "{n} 點" },
    "empty.no_positions": { en: "No position data.", zh: "無部位資料。" },
    "empty.no_allocation": { en: "No allocation data.", zh: "無配置資料。" },
    "empty.no_tracked": { en: "No tracked symbols.", zh: "無追蹤標的。" },
    "empty.no_trades": {
      en: "No trades yet. Report buys/sells to add rows.",
      zh: "尚無交易紀錄。之後直接回報買賣，我會補進來。",
    },
    "empty.no_rebalance": {
      en: "No rebalance actions needed.",
      zh: "目前沒有需要執行的再平衡動作。",
    },
    "empty.perf_history": {
      en: "Not enough history for metrics.",
      zh: "歷史不足，尚無法計算指標。",
    },
    "empty.nav_chart": {
      en: "Not enough history for NAV chart.",
      zh: "持倉歷史不足，尚無法畫出 NAV。",
    },
    "empty.compare_chart": {
      en: "Comparison starts after first buy.",
      zh: "首筆買入後開始比較 NAV / SPY。",
    },
    "empty.chart_module": { en: "Chart module not loaded.", zh: "圖表模組未載入。" },
    "empty.snapshot": { en: "Could not load snapshot.", zh: "無法載入快照" },
    "empty.no_data": { en: "No data", zh: "無資料" },
    "empty.no_fx": { en: "No records", zh: "無紀錄" },
    "perf.best": { en: "Best", zh: "最佳" },
    "rec.await_build": { en: "Await build {pct}", zh: "待建倉 {pct}" },
    "rec.defer_buy": {
      en: "Defer buy (gap ~ USD {d})",
      zh: "待較大金額再買（缺口約 USD {d}）",
    },
    "rec.no_change": { en: "No change", zh: "不需調整" },
    "rec.missing_quote": { en: "Missing quote", zh: "缺價格" },
    "rec.buy": { en: "Buy {n} sh", zh: "買 {n} 股" },
    "rec.sell": { en: "Sell {n} sh", zh: "賣 {n} 股" },
    "rec.fee": { en: "Fee {fee} USD", zh: "手續費 {fee} USD" },
    "rec.target_current": { en: "Target {tgt} → now {cur}", zh: "目標 {tgt} → 目前 {cur}" },
    "rec.defer_later": { en: "Buy later", zh: "稍後再買" },
    "rec.gap_min": { en: "Gap {gap} · min {min} USD", zh: "缺口 {gap} · 單筆至少 {min} USD" },
    "rebalance.deferred_title": { en: "Deferred buys", zh: "買進延後" },
    "rebalance.await_build_note": { en: "Await build", zh: "待建倉" },
    "status.disabled": { en: "Off", zh: "未啟用" },
    "status.pending": { en: "Pending", zh: "待建倉" },
    "status.pending_short": { en: "Pending", zh: "待建" },
    "status.deferred": { en: "Deferred", zh: "買入延後" },
    "status.deferred_short": { en: "Defer", zh: "延後" },
    "status.low": { en: "Underweight", zh: "偏低" },
    "status.high": { en: "Overweight", zh: "偏高" },
    "status.ok": { en: "In band", zh: "區間內" },
    "status.ok_short": { en: "OK", zh: "區內" },
    "ov.await_build": { en: "Await build", zh: "待建倉" },
    "ov.holdings_count": { en: "{n} names", zh: "{n} 檔" },
    "ov.phase_next": { en: "Next phase {date}", zh: "下一次配置切換 {date}" },
    "ov.hold_config": { en: "Hold current allocation", zh: "目前維持現行配置" },
    "ov.pre_build": { en: "No rebalance before first buy", zh: "建倉前不計應買應賣" },
    "ov.trade_count": { en: "{n} trades", zh: "{n} 筆" },
    "ov.cash_snap": { en: "{n} snaps / {date}", zh: "{n} 筆 / {date}" },
    "ov.alloc_band": { en: "Band: target ± {n}%", zh: "容許帶：目標 ± {n}%" },
    "meta.portfolio_built": {
      en: "{n} holdings / {t} trades",
      zh: "已建倉 {n} 檔 / {t} 筆交易",
    },
    "meta.not_built": { en: "Not invested yet", zh: "尚未建倉" },
    "meta.loan_due": {
      en: "{date} / principal {p} / interest {i}",
      zh: "{date} / 本金 {p} / 利息 {i}",
    },
    "meta.fx_summary": {
      en: "{n} events · TWD→USD {a} · USD→TWD {b}",
      zh: "{n} 筆 · 台→美 {a} · 美→台 {b}",
    },
    "meta.no_fx": { en: "No FX yet", zh: "尚無換匯紀錄" },
    "pnl.unrealized": { en: "{label} USD {amt}", zh: "{label} TWD {amt}" },
    "alloc.contrib_default": {
      en: "Add to the worst-performing sleeve",
      zh: "加在相對跌最深的那一檔",
    },
    "alloc.reason_summary": { en: "Why", zh: "查看原因" },
    "alloc.monthly": { en: "Monthly add", zh: "每月再投入" },
    "alloc.drawdown": { en: "Drawdown rule", zh: "回撤觸發" },
    "alloc.drawdown_peak": { en: "Drawdown peak", zh: "回撤基準" },
    "alloc.drawdown_now": { en: "Drawdown vs peak", zh: "目前相對高點回撤" },
    "alloc.not_set": { en: "Not set", zh: "尚未設定" },
    "loan.principal_pct": { en: "~{n}% principal", zh: "約 {n}% 本金" },
    "loan.paid_principal": { en: "Principal repaid", zh: "已還本金" },
    "loan.due_date": { en: "Due date", zh: "還款日" },
    "loan.period_principal": { en: "Period principal", zh: "本期本金" },
    "loan.period_interest": { en: "Period interest", zh: "本期利息" },
    "loan.after_payment": { en: "After payment", zh: "繳後負債" },
    "loan.monthly_due": { en: "Monthly payment", zh: "每月應繳" },
    "loan.contract_principal": { en: "Contract principal", zh: "合約本金" },
    "loan.annual_rate": { en: "Nominal rate", zh: "年利率" },
    "loan.first_due": { en: "First due", zh: "首期還款日" },
    "loan.lock_in": { en: "Lock-in", zh: "綁約" },
    "loan.lock_months": { en: "{n} months", zh: "{n} 個月" },
    "loan.total_terms": { en: "Total terms", zh: "總期數" },
    "loan.terms_count": { en: "{n} periods", zh: "{n} 期" },
    "loan.paid_interest": { en: "Interest paid", zh: "已付利息" },
    "loan.term_progress": { en: "Term", zh: "期數" },
    "loan.term_ratio": { en: "{done} / {total}", zh: "{done} / {total} 期" },
    "errors.warn": { en: "Data warnings: {msg}", zh: "資料警告：{msg}" },
    "back.overview": { en: "Back to overview", zh: "返回總覽" },
    "detail.nav_perf": { en: "Performance", zh: "績效" },
    "detail.nav_metrics": { en: "Risk & return", zh: "報酬與風險指標" },
    "detail.nav_chart_title": { en: "Portfolio NAV", zh: "組合 NAV" },
    "detail.history": { en: "History", zh: "歷史" },
    "detail.trade_log": { en: "Trade log", zh: "交易紀錄" },
    "portfolio.history_title": { en: "Trade ledger", zh: "成交紀錄" },
    "portfolio.tab.all": { en: "All", zh: "全部" },
    "portfolio.tab.buy": { en: "Buys", zh: "買入" },
    "portfolio.tab.sell": { en: "Sells", zh: "賣出" },
    "detail.buy_log": { en: "Buy log", zh: "買入紀錄" },
    "detail.sell_log": { en: "Sell log", zh: "賣出紀錄" },
    "detail.debt": { en: "Debt", zh: "負債" },
    "detail.loan_info": { en: "Loan", zh: "貸款資訊" },
    "detail.amort": { en: "Amortization", zh: "攤還" },
    "detail.amort_table": { en: "Amortization schedule", zh: "攤還表" },
    "detail.alloc_current": { en: "Current vs target", zh: "目前部位 vs 目標" },
    "detail.alloc_actions": { en: "Rebalance actions", zh: "再平衡建議" },
    "detail.alloc_rules": { en: "Phases & contributions", zh: "配置階段與再投入" },
    "detail.alloc_current_label": { en: "Current phase", zh: "目前配置" },
    "detail.fx_detail": { en: "FX · detail", zh: "換匯 · 明細" },
    "detail.fx_twd_usd": { en: "TWD to USD", zh: "台幣換美金" },
    "detail.fx_usd_twd": { en: "USD to TWD", zh: "美金換台幣" },
    "fx.count": { en: "Count", zh: "筆數" },
    "fx.avg_rate": { en: "Avg rate", zh: "平均匯率" },
    "fx.twd_total": { en: "TWD out (cum.)", zh: "累計付出台幣" },
    "fx.usd_in_total": { en: "USD in (cum.)", zh: "累計進帳美元" },
    "fx.usd_out_total": { en: "USD sold (cum.)", zh: "累計賣出美元" },
    "fx.twd_in_total": { en: "TWD in (cum.)", zh: "累計進帳台幣" },
    "perf.intervalReturnPct": { en: "Period return", zh: "區間報酬" },
    "perf.annReturnPct": { en: "Annualized return", zh: "年化報酬率" },
    "perf.excessReturnPct": { en: "Excess vs SPY", zh: "相對 SPY 超額報酬" },
    "perf.sharpe": { en: "Sharpe", zh: "夏普比率" },
    "perf.sortino": { en: "Sortino", zh: "索提諾比率" },
    "perf.calmar": { en: "Calmar", zh: "卡瑪比率" },
    "perf.recoveryFactor": { en: "Recovery factor", zh: "回撤修復倍數" },
    "perf.maxDrawdownPct": { en: "Max drawdown", zh: "最大回撤" },
    "perf.maxDdDurationDays": { en: "Longest drawdown (days)", zh: "最長回撤天數" },
    "perf.volPct": { en: "Ann. volatility", zh: "年化波動率" },
    "perf.downsideVolPct": { en: "Ann. downside vol", zh: "年化下行波動率" },
    "perf.var95DailyPct": { en: "Daily VaR 95%", zh: "日 VaR 95%" },
    "perf.cvar95DailyPct": { en: "Daily CVaR 95%", zh: "日 CVaR 95%" },
    "perf.winRatePct": { en: "Win rate", zh: "勝率" },
    "perf.profitFactor": { en: "Profit factor", zh: "獲利因子" },
    "perf.gainLossRatio": { en: "Avg win/loss", zh: "平均賺賠比" },
    "perf.upCapturePct": { en: "Up capture", zh: "上漲捕獲率" },
    "perf.downCapturePct": { en: "Down capture", zh: "下跌捕獲率" },
    "perf.beta": { en: "Beta (vs SPY)", zh: "Beta（對 SPY）" },
    "perf.corr": { en: "Corr. vs SPY", zh: "與 SPY 相關係數" },
    "perf.trackingErrorPct": { en: "Tracking error (ann.)", zh: "追蹤誤差（年化）" },
    "perf.bestDayPct": { en: "Best day", zh: "最佳單日報酬" },
    "perf.worstDayPct": { en: "Worst day", zh: "最差單日報酬" },
    "perf.avgDailyReturnPct": { en: "Avg daily return", zh: "日均報酬" },
    "perf.avgWinDayPct": { en: "Avg up day", zh: "平均上漲日報酬" },
    "perf.avgLossDayPct": { en: "Avg down day", zh: "平均下跌日報酬" },
    "perf.positiveDays": { en: "Up days", zh: "上漲日數" },
    "perf.negativeDays": { en: "Down days", zh: "下跌日數" },
    "perf.maxUpStreak": { en: "Max up streak", zh: "最長連漲天數" },
    "perf.maxDownStreak": { en: "Max down streak", zh: "最長連跌天數" },
    "perf.observationDays": { en: "Trading days", zh: "樣本交易日" },
    "perf.skewness": { en: "Skewness", zh: "偏度" },
    "perf.kurtosis": { en: "Excess kurtosis", zh: "峰度（超額）" },
    "portfolio.view.table": { en: "Table View", zh: "表格檢視" },
    "portfolio.view.timeline": { en: "Timeline View", zh: "時間軸檢視" },
    "trade.reason": { en: "Decision notes", zh: "決策原因" },
    "trade.details": { en: "Trade details", zh: "交易細節" },
    "strategy.official_link": { en: "Official Website", zh: "官方網站" },
    "meta.live_stream": { en: "Live Stream", zh: "實錄直播中" },
    "meta.live_days": { en: "Day {day} / 25 Years", zh: "第 {day} 天 / 25年" },
    "ticker.live_activity": { en: "Live Activity", zh: "最新動態" },
    "ticker.trade": { en: "Trade", zh: "交易" },
    "ticker.fx": { en: "FX", zh: "換匯" },
    "ticker.loan": { en: "Debt", zh: "貸款" },
    "ticker.status": { en: "Status", zh: "狀態" },
  };

  let memoryLang = "";

  function readStorage(key) {
    try {
      const v = localStorage.getItem(key);
      if (v != null) {
        return v;
      }
    } catch {
      /* file:// or privacy mode */
    }
    try {
      return sessionStorage.getItem(key);
    } catch {
      return null;
    }
  }

  function writeStorage(key, value) {
    memoryLang = value;
    let ok = false;
    try {
      localStorage.setItem(key, value);
      ok = true;
    } catch {
      /* ignore */
    }
    try {
      sessionStorage.setItem(key, value);
      ok = true;
    } catch {
      /* ignore */
    }
    return ok;
  }

  function getLang() {
    const fromUrl = readLangFromUrl();
    if (fromUrl) {
      return fromUrl;
    }
    const raw = readStorage(STORAGE_KEY) || memoryLang;
    return raw === LANG_EN || raw === LANG_ZH ? raw : "";
  }

  function isEn() {
    return getLang() === LANG_EN;
  }

  function isZh() {
    return getLang() === LANG_ZH;
  }

  function numberLocale() {
    return isEn() ? "en-US" : "zh-TW";
  }

  function lookupString(key) {
    const row = STRINGS[key];
    if (row) {
      return row;
    }
    const guide = global.GUIDE_STRINGS && global.GUIDE_STRINGS[key];
    return guide || null;
  }

  function t(key, vars) {
    const row = lookupString(key);
    if (!row) {
      return key;
    }
    let text = isEn() ? row.en : row.zh;
    if (vars) {
      for (const [name, value] of Object.entries(vars)) {
        text = text.replace(new RegExp(`\\{${name}\\}`, "g"), String(value));
      }
    }
    return text;
  }

  function applyDocumentLang() {
    const lang = getLang() || LANG_ZH;
    document.documentElement.lang = lang === LANG_EN ? "en" : "zh-Hant";
    document.documentElement.dataset.locale = lang === LANG_EN ? "en" : "zh";
    document.body?.classList.toggle("locale-en", lang === LANG_EN);
  }

  function applyStaticLabels() {
    document.querySelectorAll("[data-i18n-aria]").forEach((node) => {
      const key = node.getAttribute("data-i18n-aria");
      if (key) {
        node.setAttribute("aria-label", t(key));
      }
    });
    document.querySelectorAll("[data-i18n]").forEach((node) => {
      const key = node.getAttribute("data-i18n");
      if (!key) {
        return;
      }
      const text = t(key);
      if (/<\/?(?:strong|em|br)\b/i.test(text)) {
        node.innerHTML = text;
      } else {
        node.textContent = text;
      }
    });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
      const key = node.getAttribute("data-i18n-placeholder");
      if (key) {
        node.setAttribute("placeholder", t(key));
      }
    });
    document.title =
      document.querySelector("[data-title-i18n]")
        ? t(document.documentElement.getAttribute("data-title-i18n") || "")
        : document.documentElement.dataset.page === "details"
          ? isEn()
            ? "Details — Stack Experiment"
            : "資產堆疊實驗 · 明細"
          : isEn()
            ? "Stack Experiment | 25y Debt Investing Ledger"
            : "資產堆疊實驗 | 25歲貸款投資實錄";
    syncLangSwitcherUi();
  }

  function syncLangSwitcherUi() {
    document.querySelectorAll("[data-set-lang]").forEach((btn) => {
      const active = btn.getAttribute("data-set-lang") === getLang();
      btn.classList.toggle("is-active", active);
      btn.setAttribute("aria-pressed", active ? "true" : "false");
    });
  }

  function setLang(lang, onApplied) {
    if (lang !== LANG_EN && lang !== LANG_ZH) {
      return;
    }
    writeStorage(STORAGE_KEY, lang);
    syncLangToUrl(lang);
    applyDocumentLang();
    applyStaticLabels();
    hideLangGate();
    if (typeof onApplied === "function") {
      onApplied();
    }
  }

  function hideLangGate() {
    const gate = document.getElementById("lang-gate");
    if (!gate) {
      return;
    }
    gate.hidden = true;
    gate.setAttribute("aria-hidden", "true");
  }

  function showLangGate() {
    const gate = document.getElementById("lang-gate");
    if (!gate) {
      return;
    }
    gate.hidden = false;
    gate.setAttribute("aria-hidden", "false");
  }

  function bindGatePickers(onReady) {
    document.querySelectorAll("[data-pick-lang]").forEach((btn) => {
      if (btn.dataset.gateBound === "1") {
        return;
      }
      btn.dataset.gateBound = "1";
      btn.addEventListener("click", () => {
        const lang = btn.getAttribute("data-pick-lang");
        setLang(lang, onReady);
      });
    });
  }

  function initGate(onReady) {
    const urlLang = readLangFromUrl();
    if (urlLang) {
      writeStorage(STORAGE_KEY, urlLang);
    }
    const saved = getLang();
    const lang = saved || LANG_ZH;
    if (!saved) {
      writeStorage(STORAGE_KEY, lang);
    }
    applyDocumentLang();
    applyStaticLabels();
    bindGatePickers(onReady);
    bindSwitcher(onReady);
    // 永遠不顯示語言選擇 Gate，直接用中文開始
    hideLangGate();
    if (typeof onReady === "function") {
      onReady();
    }
    return true;
  }

  function bindSwitcher(onSwitch) {
    document.querySelectorAll("[data-set-lang]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const lang = btn.getAttribute("data-set-lang");
        if (lang && lang !== getLang()) {
          setLang(lang, onSwitch);
        }
      });
    });
    syncLangSwitcherUi();
  }

  function hideSubline(elementId) {
    const node = document.getElementById(elementId);
    if (!node) {
      return;
    }
    node.textContent = "";
    node.hidden = true;
  }

  function setUnitForMetric(primaryId, unitText) {
    const primary = document.getElementById(primaryId);
    const unit = primary?.closest(".focus-metric")?.querySelector(".focus-metric-unit");
    if (unit) {
      unit.textContent = unitText;
    }
  }

  global.PLLocale = {
    STORAGE_KEY,
    LANG_EN,
    LANG_ZH,
    getLang,
    isEn,
    isZh,
    numberLocale,
    t,
    applyStaticLabels,
    initGate,
    bindSwitcher,
    setLang,
    hideSubline,
    setUnitForMetric,
  };
})(typeof window !== "undefined" ? window : globalThis);
