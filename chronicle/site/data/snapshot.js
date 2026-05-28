window.__PERSONAL_LEDGER_SNAPSHOT__ = {
  "allocations": {
    "monthly_contribution": {
      "mode": "add_to_worst_performer",
      "note": "Rule: add monthly contribution to the sleeve that fell the most vs prior (use manual preferred_ticker until automated).",
      "note_zh": "加在相對跌最深的那一檔",
      "preferred_ticker": null
    },
    "phases": [
      {
        "effective_from": "2026-04-13",
        "effective_to": "2026-05-06",
        "id": "phase-a",
        "note": "Until mid-May 2026 (approximate).",
        "targets": [
          {
            "symbol": "RSSB",
            "weight": 0.5
          },
          {
            "symbol": "RSST",
            "weight": 0.35
          },
          {
            "symbol": "RSSY",
            "weight": 0.15
          }
        ]
      },
      {
        "effective_from": "2026-05-07",
        "effective_to": "2026-05-18",
        "id": "phase-b",
        "note": "RSIT sleeve: trim RSST and fund RSIT to target weight. Revert target if easing cycle resumes (see phase-c note).",
        "transition_reason_zh": "2026-05-07 起納入 RSIT（當日掛牌）。為達成約 63% 美股、37% 國際股票曝險，在維持 RSSB 50% 的前提下，以 RSIT 補強國際部位（自 RSST 調出權重）。",
        "targets": [
          {
            "symbol": "RSSB",
            "weight": 0.5
          },
          {
            "symbol": "RSST",
            "weight": 0.2
          },
          {
            "symbol": "RSSY",
            "weight": 0.15
          },
          {
            "symbol": "RSIT",
            "weight": 0.15
          }
        ]
      },
      {
        "effective_from": "2026-05-19",
        "effective_to": null,
        "id": "phase-c",
        "note": "Hawkish macro: expect rate hikes or end of easing; overweight RSST vs phase-b. Revert to phase-b weights (50/20/15/15) if inflation eases and cuts resume.",
        "transition_reason_zh": "宏觀轉偏鷹：市場定價升息或至少非降息循環，故下調 RSSB、提高 RSST 曝險。若之後通膨回落、降息循環再起，可依設定回到 phase-b（RSSB 50% 等權重）。",
        "revert_to_phase_id": "phase-b",
        "targets": [
          {
            "symbol": "RSSB",
            "weight": 0.4
          },
          {
            "symbol": "RSST",
            "weight": 0.3
          },
          {
            "symbol": "RSSY",
            "weight": 0.15
          },
          {
            "symbol": "RSIT",
            "weight": 0.15
          }
        ]
      }
    ],
    "rebalance": {
      "band_relative_to_target": 0.2,
      "broker_fee_usd_per_trade": 3,
      "buy_fee_min_notional_multiplier_other": 1.15,
      "buy_fee_min_notional_multiplier_priority": 0.85,
      "buy_fee_note_zh": "每筆買入與賣出皆計 broker_fee_usd_per_trade。若該筆手續費÷名目大於 max_trade_fee_as_pct_of_notional（數值可比照 max_buy_fee_as_pct_of_notional），前台不列下單建議（僅見偏低／偏高）。買進名目過小則再等較大金額一筆調；buy_fee_priority_symbols 門檻較低；其餘用 other；清單可空改 default。",
      "buy_fee_priority_symbols": [
        "RSIT",
        "RSSB"
      ],
      "deploy_all_cash_usd": false,
      "exact_target_min_trade_usd": 5,
      "include_cash_usd_in_denominator": true,
      "max_buy_fee_as_pct_of_notional": 0.003,
      "max_trade_fee_as_pct_of_notional": 0.003,
      "note": "Trigger when sleeve weight is below target*(1-band) or above target*(1+band). Example: 50% -> 40%-60%; 15% -> 12%-18%.",
      "note_zh": "include_cash_usd_in_denominator=true：分母含券商 USD 現金。deploy_all_cash_usd=false：僅在權重偏離帶寬外才建議再平衡（例 15%±20% → 12%–18% 內不動）。exact_target_min_trade_usd：帶寬外若差額仍低於此 USD 仍可標示調整名目過小。"
    }
  },
  "benchmarks_note": "",
  "capital_summary": {
    "cash_twd": 0.0,
    "cash_usd": 10.2,
    "cash_usd_twd": 320.38,
    "contract_principal_twd": 1350000.0,
    "deployment_ratio_pct": 99.98,
    "investment_mv_twd": 1344575.42,
    "liquid_assets_twd": 320.38,
    "loan_outstanding_twd": 1336228.0,
    "net_to_account_twd": 1340970.0,
    "net_worth_twd": 8667.8,
    "project_assets_twd": 1344895.8,
    "setup_cost_twd": 9030.0
  },
  "capital_deployed_chart": {
    "caption_zh": "棕線＝累計淨換匯投入；綠線＝權益型持股市值。券商 USD 與 BOXX 為現金側，不進 NAV 單位淨值。",
    "labels": [
      "2026-04-14T22:07:04",
      "2026-04-14",
      "2026-04-15",
      "2026-04-16",
      "2026-04-17",
      "2026-04-20",
      "2026-04-21",
      "2026-04-22",
      "2026-04-23",
      "2026-04-24",
      "2026-04-27",
      "2026-04-28",
      "2026-04-29",
      "2026-04-30",
      "2026-05-01",
      "2026-05-04",
      "2026-05-05",
      "2026-05-06",
      "2026-05-07",
      "2026-05-08",
      "2026-05-11",
      "2026-05-12",
      "2026-05-13",
      "2026-05-14",
      "2026-05-15",
      "2026-05-18",
      "2026-05-19",
      "2026-05-20",
      "2026-05-21",
      "2026-05-22",
      "2026-05-26",
      "2026-05-27"
    ],
    "datasets": [
      {
        "id": "funding_usd",
        "label": "Cumulative capital (net FX, USD)",
        "borderColor": "#8c5f34",
        "data": [
          null,
          31541.76,
          31541.76,
          34709.32,
          34709.32,
          39463.17,
          39463.17,
          39463.17,
          39463.17,
          39463.17,
          40417.67,
          40417.67,
          40417.67,
          40417.67,
          40417.67,
          40417.67,
          39419.67,
          34419.67,
          36723.84,
          36723.84,
          36723.84,
          36723.84,
          36723.84,
          36723.84,
          36723.84,
          36723.84,
          37924.09,
          37924.09,
          41088.65,
          41088.65,
          41088.65,
          41088.65
        ]
      },
      {
        "id": "position_mv_usd",
        "label": "Equity sleeve MV (USD)",
        "borderColor": "#496c59",
        "data": [
          11031.53,
          31662.200197,
          31843.370079,
          12875.320108,
          6250.110018,
          6240.577078,
          6187.420162,
          6264.810022,
          6225.610029,
          6287.180021,
          6294.012968,
          6256.875,
          6245.259972,
          6317.000113,
          6330.799044,
          31564.490545,
          31875.88006,
          32367.179928,
          37659.10232,
          38149.653175,
          38213.560143,
          38058.485483,
          38315.022961,
          38466.679485,
          37673.239904,
          37768.681023,
          38630.210047,
          39118.49003,
          42456.000284,
          42587.240978,
          42921.84099,
          42807.24054
        ]
      }
    ],
    "ready": true
  },
  "capital_buckets": {
    "buckets": [],
    "ledger_scope_note_zh": ""
  },
  "cash_buckets": {
    "schema_version": 1,
    "summary_note_en": "Cash buckets are manual snapshots of money reserved for this strategy only. They are not general personal spending cash. Use snapshots when the user reports current balances.",
    "snapshot_template": {
      "as_of": "YYYY-MM-DD",
      "buckets": [
        {
          "bucket_id": "strategy-usd-deploy",
          "amount": 0,
          "currency": "USD",
          "location_name": "broker_or_sub_account_name",
          "note_en": "Only strategy-reserved cash belongs here."
        }
      ]
    },
    "bucket_definitions": [
      {
        "id": "strategy-twd-deploy",
        "label_zh": "TWD 待投入現金",
        "currency": "TWD",
        "location_type": "bank_sub_account",
        "purpose": "undeployed_capital"
      },
      {
        "id": "strategy-usd-deploy",
        "label_zh": "USD 待投入現金",
        "currency": "USD",
        "location_type": "broker_cash",
        "purpose": "undeployed_capital"
      },
      {
        "id": "loan-payment-reserve",
        "label_zh": "月付款預備金",
        "currency": "TWD",
        "location_type": "bank_sub_account",
        "purpose": "debt_service_reserve"
      },
      {
        "id": "rebalance-reserve",
        "label_zh": "再平衡預備金",
        "currency": "USD",
        "location_type": "broker_cash",
        "purpose": "rebalance_reserve"
      },
      {
        "id": "dividend-cash-pool",
        "label_zh": "配息待用現金",
        "currency": "USD",
        "location_type": "broker_cash",
        "purpose": "income_reserve"
      }
    ],
    "snapshots": []
  },
  "cash_usd": 10.2,
  "cash_twd": 0.0,
  "charts_ready": true,
  "capital_events": {
    "schema_version": 1,
    "summary_note_en": "Capital events track strategy-level funding in/out. Use this file to measure total contributed capital, debt-funded capital, self-funded capital, and withdrawals. Do not use it for market valuation.",
    "cost_method_for_realized_pnl": "average_cost",
    "entry_template": {
      "id": "cap-YYYYMMDD-unique",
      "date": "YYYY-MM-DD",
      "event_type": "manual_contribution",
      "direction": "in",
      "source_kind": "self_funded",
      "source_name": "bank_transfer_or_income_source",
      "amount_twd": null,
      "amount_usd": null,
      "target_bucket_id": "strategy-usd-deploy",
      "counts_as_external_capital": true,
      "counts_as_strategy_cash": true,
      "linked_file": null,
      "note_en": "Describe why this event matters."
    },
    "events": [
      {
        "id": "cap-20260413-loan-draw",
        "date": "2026-04-13",
        "event_type": "loan_draw",
        "direction": "in",
        "source_kind": "debt",
        "source_name": "Personal loan",
        "amount_twd": 1350000,
        "amount_usd": null,
        "target_bucket_id": "strategy-twd-deploy",
        "counts_as_external_capital": true,
        "counts_as_strategy_cash": true,
        "linked_file": "loan.json",
        "note_en": "Initial debt-funded capital allocated to the strategy."
      }
    ],
    "event_type_reference": {
      "loan_draw": "Debt-funded capital entering the strategy.",
      "manual_contribution": "Self-funded manual capital addition.",
      "monthly_contribution": "Scheduled recurring self-funded capital addition.",
      "irregular_topup": "One-off extra capital addition.",
      "withdrawal_from_strategy": "Capital withdrawn out of the strategy.",
      "dividend_to_cash": "Income received into strategy cash.",
      "sale_proceeds_to_cash": "Sale proceeds returned to strategy cash.",
      "tax_or_fee_outflow": "Non-trade cost paid from strategy capital."
    }
  },
  "drawdown_reinvest": {
    "peak_investment_value_twd": null,
    "trigger_drawdown_from_peak_pct": 0.2,
    "effective_peak_nav_index": 106.6407,
    "current_position_nav_index": 106.3278,
    "current_vs_peak_pct": 0.29,
    "trigger_nav_index": 85.3126
  },
  "errors": [],
  "fx_events": [
    {
      "date": "2026-04-13",
      "id": "fx-opening-usd-20260413",
      "note_en": "Opening USD cash in brokerage wallet before first TWD conversion.",
      "time_local": "12:00:00",
      "usd_amount": 5
    },
    {
      "date": "2026-04-14",
      "id": "fx-20260414-a",
      "rate_twd_per_usd": 31.708,
      "time_local": "11:16:00",
      "twd_amount": 499999,
      "usd_amount": 15768.86
    },
    {
      "date": "2026-04-14",
      "id": "fx-20260414-b",
      "rate_twd_per_usd": 31.71,
      "time_local": "11:31:00",
      "twd_amount": 500000,
      "usd_amount": 15767.9
    },
    {
      "date": "2026-04-16",
      "id": "fx-20260416-a",
      "rate_twd_per_usd": 31.57,
      "time_local": "09:57:00",
      "twd_amount": 100000,
      "usd_amount": 3167.56
    },
    {
      "date": "2026-04-20",
      "id": "fx-20260420-a",
      "rate_twd_per_usd": 31.57,
      "time_local": "09:26:00",
      "twd_amount": 100000,
      "usd_amount": 3167.56
    },
    {
      "date": "2026-04-20",
      "id": "fx-20260420-b",
      "rate_twd_per_usd": 31.52,
      "time_local": "09:58:06",
      "twd_amount": 50000,
      "usd_amount": 1586.29
    },
    {
      "date": "2026-04-27",
      "id": "fx-20260427-a",
      "rate_twd_per_usd": 31.43,
      "time_local": "14:33:09",
      "twd_amount": 30000,
      "usd_amount": 954.5
    },
    {
      "date": "2026-05-05",
      "direction": "usd_to_twd",
      "id": "fx-20260505-a",
      "rate_twd_per_usd": 31.63977955811623,
      "time_local": "09:31:00",
      "twd_amount": 31577,
      "usd_amount": -998
    },
    {
      "date": "2026-05-06",
      "direction": "usd_to_twd",
      "id": "fx-20260506-a",
      "rate_twd_per_usd": 31.49,
      "time_local": "10:55:00",
      "twd_amount": 157450,
      "usd_amount": -5000
    },
    {
      "date": "2026-05-07",
      "id": "fx-20260507-a",
      "rate_twd_per_usd": 31.38,
      "time_local": "12:49:03",
      "twd_amount": 72305,
      "usd_amount": 2304.17
    },
    {
      "date": "2026-05-19",
      "id": "fx-20260519-a",
      "rate_twd_per_usd": 31.6601,
      "time_local": "10:40:49",
      "twd_amount": 38000,
      "usd_amount": 1200.25
    },
    {
      "date": "2026-05-21",
      "id": "fx-20260521-a",
      "rate_twd_per_usd": 31.6,
      "time_local": "09:12:41",
      "twd_amount": 100000,
      "usd_amount": 3164.56
    }
  ],
  "generated_at": "2026-05-28",
  "income_events": {
    "schema_version": 1,
    "summary_note_en": "Income events record dividends, distributions, withholding taxes, and where the cash went next. Keep this separate from trade history.",
    "entry_template": {
      "id": "income-YYYYMMDD-unique",
      "symbol": "RSSB",
      "event_type": "dividend",
      "ex_date": "YYYY-MM-DD",
      "pay_date": "YYYY-MM-DD",
      "gross_usd": 0,
      "tax_usd": 0,
      "net_usd": 0,
      "destination": "keep_as_cash",
      "destination_bucket_id": "dividend-cash-pool",
      "reinvested_symbol": null,
      "note_en": "Describe where the income went."
    },
    "events": [],
    "event_type_reference": {
      "dividend": "Cash dividend from a holding.",
      "distribution": "Fund distribution or similar income event.",
      "interest_income": "Cash interest received in broker or bank.",
      "return_of_capital": "Non-dividend capital return event."
    },
    "destination_reference": {
      "keep_as_cash": "Income stays in a strategy cash bucket.",
      "reinvest_same_symbol": "Income reinvested into the same symbol.",
      "reinvest_other_symbol": "Income reinvested into a different symbol.",
      "use_for_loan_payment": "Income reserved to support debt service."
    }
  },
  "ledger_intent": {
    "meta": {
      "purpose_zh": "口述紀錄與約定；技術細節以 loan.json、loan_official_schedule.json、fx.json 為準。",
      "updated_at": "2026-05-21"
    },
    "pending_followups_zh": [
      "自有資金投入待補：首次自有資金投入日期、金額、幣別，以及未來每月定期定額規則。",
      "貸款實際扣款待補：首期扣款後請補 paid_at、payment_twd、principal_twd、interest_twd、remaining_balance_twd。",
      "配息與分配待補：之後若有配息，請補 gross、tax、net、destination、是否再投入。",
      "規則執行待補：若發生跌破高點 20% 加碼、再平衡或手動覆寫，請補建議與實際執行內容。"
    ],
    "sections": [
      {
        "bullets": [
          "本帳本定位：個人投資與負債的長期紀錄；行情以 yfinance 收盤為快照。",
          "開啟方式：優先使用 scripts/open-site.bat（先更新快照再開瀏覽器）。",
          "買入後由你彙報部位、時間點、手續費；再平衡與每月再投入見 allocations.json。"
        ],
        "heading": "總覽"
      },
      {
        "bullets": [
          "2026-04-13 申貸：合約本金 1,350,000 TWD；年利率 4.5%；手續費 9,000、跨行 30，實際入帳 1,340,970 TWD。",
          "銀行紙本／試算攤還表：見 loan_official_schedule.json（可補齊各期）；與 loan.json 並存。",
          "每月應繳 18,765 TWD；繳款日每月 13 日；綁約 2 年；期數 84。",
          "淨值模型用合約本金攤還；入帳淨額見 disbursement。"
        ],
        "heading": "信貸"
      },
      {
        "bullets": [
          "換匯紀錄在 fx.json：逐筆保存匯率與金額，方便日後查「當時用哪個匯率換的」。",
          "不強制把「各筆換得美元加總」當成唯一美金現金；你可能另有舊美金。若要讓淨值含美元現金，於 portfolio.json 手動填 cash_usd；可維持 null。"
        ],
        "heading": "換匯"
      },
      {
        "bullets": [
          "約至 2026-05-06 前：RSSB 50%、RSST 35%、RSSY 15%。",
          "2026-05-07 至 2026-05-18（phase-b）：RSSB 50%、RSST 20%、RSIT 15%、RSSY 15%。",
          "2026-05-19 起（phase-c）：RSSB 40%、RSST 30%、RSSY 15%、RSIT 15%。理由：預期升息或停止降息循環。",
          "若通膨回落或其他因素使降息循環再啟動，改回 phase-b 權重（50/20/15/15）；見 allocations.json phase-c.revert_to_phase_id。",
          "2026-05-19 22:07:16 買入 RSST 37 股 @33.05，成交 1222.85 USD，手續費 3（phase-c 加碼 RSST）。",
          "2026-05-21 22:15:05 買入 RSST 95 股 @33.33，成交 3166.35 USD，手續費 3（phase-c 加碼 RSST）。"
        ],
        "heading": "目標配置"
      },
      {
        "bullets": [
          "再平衡：目標權重 ±20% 帶寬。",
          "每月再投入：加在相對跌最深的那一檔（見 monthly_contribution）。",
          "策略帳本重點：追蹤總投入、自有資金 / 借入資金拆分、規則觸發、實際執行、配息與現金池。"
        ],
        "heading": "再平衡與再投入"
      },
      {
        "bullets": [
          "新增骨架檔：capital_events.json、cash_buckets.json、rule_events.json、rebalance_log.json、income_events.json。",
          "交接摘要輸出：chronicle/export/current_summary.md，由 scripts/export-summary.bat 或 scripts/open-site.bat 一併更新。",
          "capital_events.json 用於統計整套策略累計投入，不只看貸款，也包含未來自有資金與配息回流。",
          "cash_buckets.json 用於記錄策略專用現金池，不等於一般生活現金。",
          "rule_events.json 與 rebalance_log.json 分開保存規則觸發與實際執行。",
          "income_events.json 專門記配息與現金用途，避免和 trades.json 混在一起。"
        ],
        "heading": "策略帳本骨架"
      }
    ],
    "title": "個人投資紀錄與約定"
  },
  "loan_schedule_computed": {
    "caption_zh": "",
    "method": "daily_365",
    "rows": [
      {
        "balance_after_twd": 1336228.0,
        "days": 30,
        "interest_twd": 4993.0,
        "payment_date": "2026-05-13",
        "payment_twd": 18765.0,
        "period": 1,
        "period_start": "2026-04-13",
        "principal_twd": 13772.0
      },
      {
        "balance_after_twd": 1322570.0,
        "days": 31,
        "interest_twd": 5107.0,
        "payment_date": "2026-06-13",
        "payment_twd": 18765.0,
        "period": 2,
        "period_start": "2026-05-13",
        "principal_twd": 13658.0
      },
      {
        "balance_after_twd": 1308697.0,
        "days": 30,
        "interest_twd": 4892.0,
        "payment_date": "2026-07-13",
        "payment_twd": 18765.0,
        "period": 3,
        "period_start": "2026-06-13",
        "principal_twd": 13873.0
      },
      {
        "balance_after_twd": 1294934.0,
        "days": 31,
        "interest_twd": 5002.0,
        "payment_date": "2026-08-13",
        "payment_twd": 18765.0,
        "period": 4,
        "period_start": "2026-07-13",
        "principal_twd": 13763.0
      },
      {
        "balance_after_twd": 1281118.0,
        "days": 31,
        "interest_twd": 4949.0,
        "payment_date": "2026-09-13",
        "payment_twd": 18765.0,
        "period": 5,
        "period_start": "2026-08-13",
        "principal_twd": 13816.0
      },
      {
        "balance_after_twd": 1267091.0,
        "days": 30,
        "interest_twd": 4738.0,
        "payment_date": "2026-10-13",
        "payment_twd": 18765.0,
        "period": 6,
        "period_start": "2026-09-13",
        "principal_twd": 14027.0
      },
      {
        "balance_after_twd": 1253169.0,
        "days": 31,
        "interest_twd": 4843.0,
        "payment_date": "2026-11-13",
        "payment_twd": 18765.0,
        "period": 7,
        "period_start": "2026-10-13",
        "principal_twd": 13922.0
      },
      {
        "balance_after_twd": 1239039.0,
        "days": 30,
        "interest_twd": 4635.0,
        "payment_date": "2026-12-13",
        "payment_twd": 18765.0,
        "period": 8,
        "period_start": "2026-11-13",
        "principal_twd": 14130.0
      },
      {
        "balance_after_twd": 1225010.0,
        "days": 31,
        "interest_twd": 4736.0,
        "payment_date": "2027-01-13",
        "payment_twd": 18765.0,
        "period": 9,
        "period_start": "2026-12-13",
        "principal_twd": 14029.0
      },
      {
        "balance_after_twd": 1210927.0,
        "days": 31,
        "interest_twd": 4682.0,
        "payment_date": "2027-02-13",
        "payment_twd": 18765.0,
        "period": 10,
        "period_start": "2027-01-13",
        "principal_twd": 14083.0
      },
      {
        "balance_after_twd": 1196342.0,
        "days": 28,
        "interest_twd": 4180.0,
        "payment_date": "2027-03-13",
        "payment_twd": 18765.0,
        "period": 11,
        "period_start": "2027-02-13",
        "principal_twd": 14585.0
      },
      {
        "balance_after_twd": 1182149.0,
        "days": 31,
        "interest_twd": 4572.0,
        "payment_date": "2027-04-13",
        "payment_twd": 18765.0,
        "period": 12,
        "period_start": "2027-03-13",
        "principal_twd": 14193.0
      },
      {
        "balance_after_twd": 1167756.0,
        "days": 30,
        "interest_twd": 4372.0,
        "payment_date": "2027-05-13",
        "payment_twd": 18765.0,
        "period": 13,
        "period_start": "2027-04-13",
        "principal_twd": 14393.0
      },
      {
        "balance_after_twd": 1153454.0,
        "days": 31,
        "interest_twd": 4463.0,
        "payment_date": "2027-06-13",
        "payment_twd": 18765.0,
        "period": 14,
        "period_start": "2027-05-13",
        "principal_twd": 14302.0
      },
      {
        "balance_after_twd": 1138955.0,
        "days": 30,
        "interest_twd": 4266.0,
        "payment_date": "2027-07-13",
        "payment_twd": 18765.0,
        "period": 15,
        "period_start": "2027-06-13",
        "principal_twd": 14499.0
      },
      {
        "balance_after_twd": 1124543.0,
        "days": 31,
        "interest_twd": 4353.0,
        "payment_date": "2027-08-13",
        "payment_twd": 18765.0,
        "period": 16,
        "period_start": "2027-07-13",
        "principal_twd": 14412.0
      },
      {
        "balance_after_twd": 1110076.0,
        "days": 31,
        "interest_twd": 4298.0,
        "payment_date": "2027-09-13",
        "payment_twd": 18765.0,
        "period": 17,
        "period_start": "2027-08-13",
        "principal_twd": 14467.0
      },
      {
        "balance_after_twd": 1095417.0,
        "days": 30,
        "interest_twd": 4106.0,
        "payment_date": "2027-10-13",
        "payment_twd": 18765.0,
        "period": 18,
        "period_start": "2027-09-13",
        "principal_twd": 14659.0
      },
      {
        "balance_after_twd": 1080839.0,
        "days": 31,
        "interest_twd": 4187.0,
        "payment_date": "2027-11-13",
        "payment_twd": 18765.0,
        "period": 19,
        "period_start": "2027-10-13",
        "principal_twd": 14578.0
      },
      {
        "balance_after_twd": 1066072.0,
        "days": 30,
        "interest_twd": 3998.0,
        "payment_date": "2027-12-13",
        "payment_twd": 18765.0,
        "period": 20,
        "period_start": "2027-11-13",
        "principal_twd": 14767.0
      },
      {
        "balance_after_twd": 1051381.0,
        "days": 31,
        "interest_twd": 4074.0,
        "payment_date": "2028-01-13",
        "payment_twd": 18765.0,
        "period": 21,
        "period_start": "2027-12-13",
        "principal_twd": 14691.0
      },
      {
        "balance_after_twd": 1036634.0,
        "days": 31,
        "interest_twd": 4018.0,
        "payment_date": "2028-02-13",
        "payment_twd": 18765.0,
        "period": 22,
        "period_start": "2028-01-13",
        "principal_twd": 14747.0
      },
      {
        "balance_after_twd": 1021575.0,
        "days": 29,
        "interest_twd": 3706.0,
        "payment_date": "2028-03-13",
        "payment_twd": 18765.0,
        "period": 23,
        "period_start": "2028-02-13",
        "principal_twd": 15059.0
      },
      {
        "balance_after_twd": 1006714.0,
        "days": 31,
        "interest_twd": 3904.0,
        "payment_date": "2028-04-13",
        "payment_twd": 18765.0,
        "period": 24,
        "period_start": "2028-03-13",
        "principal_twd": 14861.0
      },
      {
        "balance_after_twd": 991672.0,
        "days": 30,
        "interest_twd": 3723.0,
        "payment_date": "2028-05-13",
        "payment_twd": 18765.0,
        "period": 25,
        "period_start": "2028-04-13",
        "principal_twd": 15042.0
      },
      {
        "balance_after_twd": 976697.0,
        "days": 31,
        "interest_twd": 3790.0,
        "payment_date": "2028-06-13",
        "payment_twd": 18765.0,
        "period": 26,
        "period_start": "2028-05-13",
        "principal_twd": 14975.0
      },
      {
        "balance_after_twd": 961544.0,
        "days": 30,
        "interest_twd": 3612.0,
        "payment_date": "2028-07-13",
        "payment_twd": 18765.0,
        "period": 27,
        "period_start": "2028-06-13",
        "principal_twd": 15153.0
      },
      {
        "balance_after_twd": 946454.0,
        "days": 31,
        "interest_twd": 3675.0,
        "payment_date": "2028-08-13",
        "payment_twd": 18765.0,
        "period": 28,
        "period_start": "2028-07-13",
        "principal_twd": 15090.0
      },
      {
        "balance_after_twd": 931306.0,
        "days": 31,
        "interest_twd": 3617.0,
        "payment_date": "2028-09-13",
        "payment_twd": 18765.0,
        "period": 29,
        "period_start": "2028-08-13",
        "principal_twd": 15148.0
      },
      {
        "balance_after_twd": 915986.0,
        "days": 30,
        "interest_twd": 3445.0,
        "payment_date": "2028-10-13",
        "payment_twd": 18765.0,
        "period": 30,
        "period_start": "2028-09-13",
        "principal_twd": 15320.0
      },
      {
        "balance_after_twd": 900722.0,
        "days": 31,
        "interest_twd": 3501.0,
        "payment_date": "2028-11-13",
        "payment_twd": 18765.0,
        "period": 31,
        "period_start": "2028-10-13",
        "principal_twd": 15264.0
      },
      {
        "balance_after_twd": 885288.0,
        "days": 30,
        "interest_twd": 3331.0,
        "payment_date": "2028-12-13",
        "payment_twd": 18765.0,
        "period": 32,
        "period_start": "2028-11-13",
        "principal_twd": 15434.0
      },
      {
        "balance_after_twd": 869906.0,
        "days": 31,
        "interest_twd": 3383.0,
        "payment_date": "2029-01-13",
        "payment_twd": 18765.0,
        "period": 33,
        "period_start": "2028-12-13",
        "principal_twd": 15382.0
      },
      {
        "balance_after_twd": 854466.0,
        "days": 31,
        "interest_twd": 3325.0,
        "payment_date": "2029-02-13",
        "payment_twd": 18765.0,
        "period": 34,
        "period_start": "2029-01-13",
        "principal_twd": 15440.0
      },
      {
        "balance_after_twd": 838651.0,
        "days": 28,
        "interest_twd": 2950.0,
        "payment_date": "2029-03-13",
        "payment_twd": 18765.0,
        "period": 35,
        "period_start": "2029-02-13",
        "principal_twd": 15815.0
      },
      {
        "balance_after_twd": 823091.0,
        "days": 31,
        "interest_twd": 3205.0,
        "payment_date": "2029-04-13",
        "payment_twd": 18765.0,
        "period": 36,
        "period_start": "2029-03-13",
        "principal_twd": 15560.0
      },
      {
        "balance_after_twd": 807370.0,
        "days": 30,
        "interest_twd": 3044.0,
        "payment_date": "2029-05-13",
        "payment_twd": 18765.0,
        "period": 37,
        "period_start": "2029-04-13",
        "principal_twd": 15721.0
      },
      {
        "balance_after_twd": 791691.0,
        "days": 31,
        "interest_twd": 3086.0,
        "payment_date": "2029-06-13",
        "payment_twd": 18765.0,
        "period": 38,
        "period_start": "2029-05-13",
        "principal_twd": 15679.0
      },
      {
        "balance_after_twd": 775854.0,
        "days": 30,
        "interest_twd": 2928.0,
        "payment_date": "2029-07-13",
        "payment_twd": 18765.0,
        "period": 39,
        "period_start": "2029-06-13",
        "principal_twd": 15837.0
      },
      {
        "balance_after_twd": 760054.0,
        "days": 31,
        "interest_twd": 2965.0,
        "payment_date": "2029-08-13",
        "payment_twd": 18765.0,
        "period": 40,
        "period_start": "2029-07-13",
        "principal_twd": 15800.0
      },
      {
        "balance_after_twd": 744194.0,
        "days": 31,
        "interest_twd": 2905.0,
        "payment_date": "2029-09-13",
        "payment_twd": 18765.0,
        "period": 41,
        "period_start": "2029-08-13",
        "principal_twd": 15860.0
      },
      {
        "balance_after_twd": 728181.0,
        "days": 30,
        "interest_twd": 2752.0,
        "payment_date": "2029-10-13",
        "payment_twd": 18765.0,
        "period": 42,
        "period_start": "2029-09-13",
        "principal_twd": 16013.0
      },
      {
        "balance_after_twd": 712199.0,
        "days": 31,
        "interest_twd": 2783.0,
        "payment_date": "2029-11-13",
        "payment_twd": 18765.0,
        "period": 43,
        "period_start": "2029-10-13",
        "principal_twd": 15982.0
      },
      {
        "balance_after_twd": 696068.0,
        "days": 30,
        "interest_twd": 2634.0,
        "payment_date": "2029-12-13",
        "payment_twd": 18765.0,
        "period": 44,
        "period_start": "2029-11-13",
        "principal_twd": 16131.0
      },
      {
        "balance_after_twd": 679963.0,
        "days": 31,
        "interest_twd": 2660.0,
        "payment_date": "2030-01-13",
        "payment_twd": 18765.0,
        "period": 45,
        "period_start": "2029-12-13",
        "principal_twd": 16105.0
      },
      {
        "balance_after_twd": 663797.0,
        "days": 31,
        "interest_twd": 2599.0,
        "payment_date": "2030-02-13",
        "payment_twd": 18765.0,
        "period": 46,
        "period_start": "2030-01-13",
        "principal_twd": 16166.0
      },
      {
        "balance_after_twd": 647323.0,
        "days": 28,
        "interest_twd": 2291.0,
        "payment_date": "2030-03-13",
        "payment_twd": 18765.0,
        "period": 47,
        "period_start": "2030-02-13",
        "principal_twd": 16474.0
      },
      {
        "balance_after_twd": 631032.0,
        "days": 31,
        "interest_twd": 2474.0,
        "payment_date": "2030-04-13",
        "payment_twd": 18765.0,
        "period": 48,
        "period_start": "2030-03-13",
        "principal_twd": 16291.0
      },
      {
        "balance_after_twd": 614601.0,
        "days": 30,
        "interest_twd": 2334.0,
        "payment_date": "2030-05-13",
        "payment_twd": 18765.0,
        "period": 49,
        "period_start": "2030-04-13",
        "principal_twd": 16431.0
      },
      {
        "balance_after_twd": 598185.0,
        "days": 31,
        "interest_twd": 2349.0,
        "payment_date": "2030-06-13",
        "payment_twd": 18765.0,
        "period": 50,
        "period_start": "2030-05-13",
        "principal_twd": 16416.0
      },
      {
        "balance_after_twd": 581632.0,
        "days": 30,
        "interest_twd": 2212.0,
        "payment_date": "2030-07-13",
        "payment_twd": 18765.0,
        "period": 51,
        "period_start": "2030-06-13",
        "principal_twd": 16553.0
      },
      {
        "balance_after_twd": 565090.0,
        "days": 31,
        "interest_twd": 2223.0,
        "payment_date": "2030-08-13",
        "payment_twd": 18765.0,
        "period": 52,
        "period_start": "2030-07-13",
        "principal_twd": 16542.0
      },
      {
        "balance_after_twd": 548485.0,
        "days": 31,
        "interest_twd": 2160.0,
        "payment_date": "2030-09-13",
        "payment_twd": 18765.0,
        "period": 53,
        "period_start": "2030-08-13",
        "principal_twd": 16605.0
      },
      {
        "balance_after_twd": 531749.0,
        "days": 30,
        "interest_twd": 2029.0,
        "payment_date": "2030-10-13",
        "payment_twd": 18765.0,
        "period": 54,
        "period_start": "2030-09-13",
        "principal_twd": 16736.0
      },
      {
        "balance_after_twd": 515016.0,
        "days": 31,
        "interest_twd": 2032.0,
        "payment_date": "2030-11-13",
        "payment_twd": 18765.0,
        "period": 55,
        "period_start": "2030-10-13",
        "principal_twd": 16733.0
      },
      {
        "balance_after_twd": 498156.0,
        "days": 30,
        "interest_twd": 1905.0,
        "payment_date": "2030-12-13",
        "payment_twd": 18765.0,
        "period": 56,
        "period_start": "2030-11-13",
        "principal_twd": 16860.0
      },
      {
        "balance_after_twd": 481295.0,
        "days": 31,
        "interest_twd": 1904.0,
        "payment_date": "2031-01-13",
        "payment_twd": 18765.0,
        "period": 57,
        "period_start": "2030-12-13",
        "principal_twd": 16861.0
      },
      {
        "balance_after_twd": 464369.0,
        "days": 31,
        "interest_twd": 1839.0,
        "payment_date": "2031-02-13",
        "payment_twd": 18765.0,
        "period": 58,
        "period_start": "2031-01-13",
        "principal_twd": 16926.0
      },
      {
        "balance_after_twd": 447207.0,
        "days": 28,
        "interest_twd": 1603.0,
        "payment_date": "2031-03-13",
        "payment_twd": 18765.0,
        "period": 59,
        "period_start": "2031-02-13",
        "principal_twd": 17162.0
      },
      {
        "balance_after_twd": 430151.0,
        "days": 31,
        "interest_twd": 1709.0,
        "payment_date": "2031-04-13",
        "payment_twd": 18765.0,
        "period": 60,
        "period_start": "2031-03-13",
        "principal_twd": 17056.0
      },
      {
        "balance_after_twd": 412977.0,
        "days": 30,
        "interest_twd": 1591.0,
        "payment_date": "2031-05-13",
        "payment_twd": 18765.0,
        "period": 61,
        "period_start": "2031-04-13",
        "principal_twd": 17174.0
      },
      {
        "balance_after_twd": 395790.0,
        "days": 31,
        "interest_twd": 1578.0,
        "payment_date": "2031-06-13",
        "payment_twd": 18765.0,
        "period": 62,
        "period_start": "2031-05-13",
        "principal_twd": 17187.0
      },
      {
        "balance_after_twd": 378489.0,
        "days": 30,
        "interest_twd": 1464.0,
        "payment_date": "2031-07-13",
        "payment_twd": 18765.0,
        "period": 63,
        "period_start": "2031-06-13",
        "principal_twd": 17301.0
      },
      {
        "balance_after_twd": 361171.0,
        "days": 31,
        "interest_twd": 1447.0,
        "payment_date": "2031-08-13",
        "payment_twd": 18765.0,
        "period": 64,
        "period_start": "2031-07-13",
        "principal_twd": 17318.0
      },
      {
        "balance_after_twd": 343786.0,
        "days": 31,
        "interest_twd": 1380.0,
        "payment_date": "2031-09-13",
        "payment_twd": 18765.0,
        "period": 65,
        "period_start": "2031-08-13",
        "principal_twd": 17385.0
      },
      {
        "balance_after_twd": 326293.0,
        "days": 30,
        "interest_twd": 1272.0,
        "payment_date": "2031-10-13",
        "payment_twd": 18765.0,
        "period": 66,
        "period_start": "2031-09-13",
        "principal_twd": 17493.0
      },
      {
        "balance_after_twd": 308775.0,
        "days": 31,
        "interest_twd": 1247.0,
        "payment_date": "2031-11-13",
        "payment_twd": 18765.0,
        "period": 67,
        "period_start": "2031-10-13",
        "principal_twd": 17518.0
      },
      {
        "balance_after_twd": 291152.0,
        "days": 30,
        "interest_twd": 1142.0,
        "payment_date": "2031-12-13",
        "payment_twd": 18765.0,
        "period": 68,
        "period_start": "2031-11-13",
        "principal_twd": 17623.0
      },
      {
        "balance_after_twd": 273500.0,
        "days": 31,
        "interest_twd": 1113.0,
        "payment_date": "2032-01-13",
        "payment_twd": 18765.0,
        "period": 69,
        "period_start": "2031-12-13",
        "principal_twd": 17652.0
      },
      {
        "balance_after_twd": 255780.0,
        "days": 31,
        "interest_twd": 1045.0,
        "payment_date": "2032-02-13",
        "payment_twd": 18765.0,
        "period": 70,
        "period_start": "2032-01-13",
        "principal_twd": 17720.0
      },
      {
        "balance_after_twd": 237930.0,
        "days": 29,
        "interest_twd": 915.0,
        "payment_date": "2032-03-13",
        "payment_twd": 18765.0,
        "period": 71,
        "period_start": "2032-02-13",
        "principal_twd": 17850.0
      },
      {
        "balance_after_twd": 220074.0,
        "days": 31,
        "interest_twd": 909.0,
        "payment_date": "2032-04-13",
        "payment_twd": 18765.0,
        "period": 72,
        "period_start": "2032-03-13",
        "principal_twd": 17856.0
      },
      {
        "balance_after_twd": 202123.0,
        "days": 30,
        "interest_twd": 814.0,
        "payment_date": "2032-05-13",
        "payment_twd": 18765.0,
        "period": 73,
        "period_start": "2032-04-13",
        "principal_twd": 17951.0
      },
      {
        "balance_after_twd": 184130.0,
        "days": 31,
        "interest_twd": 772.0,
        "payment_date": "2032-06-13",
        "payment_twd": 18765.0,
        "period": 74,
        "period_start": "2032-05-13",
        "principal_twd": 17993.0
      },
      {
        "balance_after_twd": 166046.0,
        "days": 30,
        "interest_twd": 681.0,
        "payment_date": "2032-07-13",
        "payment_twd": 18765.0,
        "period": 75,
        "period_start": "2032-06-13",
        "principal_twd": 18084.0
      },
      {
        "balance_after_twd": 147916.0,
        "days": 31,
        "interest_twd": 635.0,
        "payment_date": "2032-08-13",
        "payment_twd": 18765.0,
        "period": 76,
        "period_start": "2032-07-13",
        "principal_twd": 18130.0
      },
      {
        "balance_after_twd": 129716.0,
        "days": 31,
        "interest_twd": 565.0,
        "payment_date": "2032-09-13",
        "payment_twd": 18765.0,
        "period": 77,
        "period_start": "2032-08-13",
        "principal_twd": 18200.0
      },
      {
        "balance_after_twd": 111431.0,
        "days": 30,
        "interest_twd": 480.0,
        "payment_date": "2032-10-13",
        "payment_twd": 18765.0,
        "period": 78,
        "period_start": "2032-09-13",
        "principal_twd": 18285.0
      },
      {
        "balance_after_twd": 93092.0,
        "days": 31,
        "interest_twd": 426.0,
        "payment_date": "2032-11-13",
        "payment_twd": 18765.0,
        "period": 79,
        "period_start": "2032-10-13",
        "principal_twd": 18339.0
      },
      {
        "balance_after_twd": 74671.0,
        "days": 30,
        "interest_twd": 344.0,
        "payment_date": "2032-12-13",
        "payment_twd": 18765.0,
        "period": 80,
        "period_start": "2032-11-13",
        "principal_twd": 18421.0
      },
      {
        "balance_after_twd": 56191.0,
        "days": 31,
        "interest_twd": 285.0,
        "payment_date": "2033-01-13",
        "payment_twd": 18765.0,
        "period": 81,
        "period_start": "2032-12-13",
        "principal_twd": 18480.0
      },
      {
        "balance_after_twd": 37641.0,
        "days": 31,
        "interest_twd": 215.0,
        "payment_date": "2033-02-13",
        "payment_twd": 18765.0,
        "period": 82,
        "period_start": "2033-01-13",
        "principal_twd": 18550.0
      },
      {
        "balance_after_twd": 19006.0,
        "days": 28,
        "interest_twd": 130.0,
        "payment_date": "2033-03-13",
        "payment_twd": 18765.0,
        "period": 83,
        "period_start": "2033-02-13",
        "principal_twd": 18635.0
      },
      {
        "balance_after_twd": 314.0,
        "days": 31,
        "interest_twd": 73.0,
        "payment_date": "2033-04-13",
        "payment_twd": 18765.0,
        "period": 84,
        "period_start": "2033-03-13",
        "principal_twd": 18692.0
      }
    ]
  },
  "investment_cost": {
    "historical_cost_twd": 1315487.46,
    "current_fx_equivalent_twd": 1303832.23,
    "invested_usd": 41510.1,
    "matched_flow_count": 18,
    "unmatched_flow_count": 0,
    "historical_fx_rate_avg": 31.5844,
    "twd_cost_method": "historical_fx_log",
    "unrealized_pnl_twd": 29087.96
  },
  "investment_mv_twd": 1344575.42,
  "investment_mv_usd": 42807.2405,
  "liabilities": {
    "loan_next_due_amount_twd": 18765.0,
    "loan_next_due_date": "2026-06-13",
    "loan_outstanding_twd": 1336228.0,
    "net_worth_liabilities_twd": 1336228.0
  },
  "loan": {
    "annual_nominal_rate": 0.045,
    "contract_principal_twd": 1350000.0,
    "cross_bank_fee_twd": 30.0,
    "cumulative_interest_paid_twd": 4993.0,
    "cumulative_principal_paid_twd": 13772.0,
    "fees_total_twd": 9030.0,
    "first_due_date": "2026-05-13",
    "handling_fee_twd": 9000.0,
    "lock_in_months": 24,
    "monthly_payment_twd": 18765.0,
    "net_to_account_twd": 1340970.0,
    "next_due_amount_twd": 18765.0,
    "next_due_date": "2026-06-13",
    "origin_date": "2026-04-13",
    "outstanding_raw_twd": 1336228.0,
    "outstanding_twd": 1336228.0,
    "payments_assumed_count": 1,
    "term_months": 84,
    "next_due_interest_twd": 5107.0,
    "next_due_period": 2,
    "next_due_principal_twd": 13658.0,
    "outstanding_after_next_due_twd": 1322570.0,
    "reminder": {
      "calendar_day": 13,
      "note_zh": "每月 13 日清晨扣款；需提醒（可接行事曆或手機，此處僅紀錄）。"
    }
  },
  "nav_chart": {
    "caption_zh": "綠線 = 單位淨值 NAV（僅權益型 ETF 持股市值；閒置 USD 與 BOXX 不計入）；換匯（含美金換台幣）不動單位；僅權益型 ETF 買入增單位、賣出減單位。棕線 = 若改買 SPY（跟你的股票買賣名目；成交時點對 Yahoo 1m/5m）；紫線 = 同上改 SSO。BOXX 等同美金現金，不進 NAV、不動影子。",
    "labels": [
      "2026-04-14T22:07:04",
      "2026-04-14",
      "2026-04-15",
      "2026-04-16",
      "2026-04-17",
      "2026-04-20",
      "2026-04-21",
      "2026-04-22",
      "2026-04-23",
      "2026-04-24",
      "2026-04-27",
      "2026-04-28",
      "2026-04-29",
      "2026-04-30",
      "2026-05-01",
      "2026-05-04",
      "2026-05-05",
      "2026-05-06",
      "2026-05-07",
      "2026-05-08",
      "2026-05-11",
      "2026-05-12",
      "2026-05-13",
      "2026-05-14",
      "2026-05-15",
      "2026-05-18",
      "2026-05-19",
      "2026-05-20",
      "2026-05-21",
      "2026-05-22",
      "2026-05-26",
      "2026-05-27"
    ],
    "datasets": [
      {
        "id": "nav",
        "label": "我的組合 NAV（單位淨值，基期 100）",
        "borderColor": "#496c59",
        "data": [
          100.0,
          100.9978,
          101.5757,
          101.3333,
          102.1483,
          101.9925,
          101.1237,
          102.3885,
          101.7479,
          102.7541,
          102.8658,
          102.2588,
          102.069,
          103.2415,
          103.467,
          102.6588,
          103.6716,
          105.2694,
          104.4018,
          105.7618,
          105.939,
          105.509,
          106.2202,
          106.6407,
          104.441,
          104.7056,
          103.6956,
          105.0063,
          105.4554,
          105.7814,
          106.6125,
          106.3278
        ]
      },
      {
        "id": "spy_shadow",
        "label": "SPY 影子（跟你的買賣／現金）",
        "borderColor": "#8c5f34",
        "data": [
          100.0,
          100.591,
          101.3847,
          101.6339,
          102.8622,
          102.6565,
          101.9844,
          103.0172,
          102.6174,
          103.4126,
          103.5908,
          103.0867,
          103.0708,
          104.0963,
          104.3845,
          104.0021,
          104.8365,
          106.2936,
          105.9677,
          106.8426,
          107.086,
          106.9237,
          107.5219,
          108.3707,
          107.0671,
          106.9918,
          106.2791,
          107.3684,
          107.5813,
          108.0043,
          108.7213,
          108.7025
        ]
      },
      {
        "id": "sso_shadow",
        "label": "SSO 正二影子（跟你的買賣／現金）",
        "borderColor": "#6f5a9a",
        "data": [
          100.0,
          101.1749,
          102.7356,
          103.2158,
          105.6856,
          105.2568,
          103.9019,
          105.96,
          105.1539,
          106.6975,
          107.0577,
          105.9943,
          105.9772,
          107.9839,
          108.5842,
          107.8124,
          109.476,
          112.5289,
          111.7914,
          113.5752,
          114.0726,
          113.7638,
          115.0159,
          116.7996,
          113.9353,
          113.7295,
          112.2545,
          114.5528,
          114.9644,
          115.7877,
          117.297,
          117.2798
        ]
      }
    ]
  },
  "nav_history_days": 32,
  "nav_summary": {
    "cumulative_invested_usd": 41510.1,
    "invested_basis": "flows",
    "mv_usd": 42807.24054,
    "mv_as_of": "2026-05-27",
    "nav_index_100": 106.3278,
    "unrealized_pnl_usd": null,
    "position_mv_usd": 42807.2405,
    "ledger_cash_usd": 10.2,
    "nav_funding_usd": 41088.65,
    "nav_index_basis": "unit_fund_deployed_on_trade",
    "nav_anchor_first_trade": "2026-04-14T22:07:04",
    "shadow_ready": true,
    "shadow_tickers": [
      "SPY",
      "SSO"
    ],
    "shadow_index_basis": "chained_benchmark_return_with_mirrored_shares",
    "shadow_fill_price_basis": "intraday_bar_at_executed_at",
    "shadow_fill_timestamp_tz": "Asia/Taipei",
    "shadow_fill_market_tz": "America/New_York",
    "spy_nav_benchmark_stats": {
      "ready": true,
      "interval": {
        "from_date": "2026-04-14T22:07:04",
        "to_date": "2026-05-27",
        "nav_pct": 6.3278,
        "spy_pct": 8.7025,
        "excess_pct_points": -2.3747
      },
      "prior_row": {
        "prior_date": "2026-05-26",
        "last_date": "2026-05-27",
        "nav_1d_pct": -0.267,
        "spy_1d_pct": -0.0173,
        "excess_pct_points": -0.2497,
        "mv_usd_prior": 42932.04099,
        "mv_usd_last": 42817.44054,
        "mv_usd_delta": -114.6004,
        "mv_usd_pct": -0.2669
      }
    },
    "sso_nav_benchmark_stats": {
      "ready": true,
      "interval": {
        "from_date": "2026-04-14T22:07:04",
        "to_date": "2026-05-27",
        "nav_pct": 6.3278,
        "spy_pct": 17.2798,
        "excess_pct_points": -10.952
      },
      "prior_row": {
        "prior_date": "2026-05-26",
        "last_date": "2026-05-27",
        "nav_1d_pct": -0.267,
        "spy_1d_pct": -0.0147,
        "excess_pct_points": -0.2523,
        "mv_usd_prior": 42932.04099,
        "mv_usd_last": 42817.44054,
        "mv_usd_delta": -114.6004,
        "mv_usd_pct": -0.2669
      }
    },
    "first_trade_at": "2026-04-14T22:07:04",
    "spy_benchmark_anchor": "yahoo_open",
    "nav_model": "equity_cash_ledger",
    "ledger_cash_seed_usd": 0.0,
    "nav_cash_includes_fx": true,
    "equity_plus_cash_usd": 42817.44
  },
  "net_worth": {
    "assets_twd": 1344895.8,
    "cash_total_twd": 320.38,
    "cash_usd_omitted": false,
    "investment_positions_twd": 1344575.42,
    "liabilities_twd": 1336228.0,
    "net_worth_twd": 8667.8
  },
  "net_worth_note_zh": null,
  "overview": {
    "assets_twd": 1344895.8,
    "broker_cash_plus_boxx_mv_usd": 10.2,
    "broker_cash_plus_cash_like_mv_usd": 10.2,
    "boxx_market_value_usd": 0.0,
    "cash_like_market_value_usd": 0.0,
    "cash_like_symbols": [
      "BOXX"
    ],
    "cash_like_note_zh": "券商 USD 餘額 + BOXX 市值（等同美金現金，計入淨資產現金側）；NAV 綠線與 SPY 影子僅跟權益型 ETF 買賣，不含閒置現金與 BOXX。",
    "investment_mv_twd": 1344575.42,
    "liabilities_twd": 1336228.0,
    "loan_next_due_amount_twd": 18765.0,
    "loan_next_due_date": "2026-06-13",
    "net_worth_twd": 8667.8,
    "phase_id": "phase-c",
    "phase_range": {
      "from": "2026-05-19",
      "to": null
    },
    "project_buckets_note_zh": "",
    "project_buckets_total_twd": 0,
    "rebalance_needed": false,
    "usd_twd": 31.40999984741211,
    "usd_twd_source": "yahoo"
  },
  "platform_note_zh": "",
  "portfolio_view": {
    "as_of": "2026-05-28",
    "buy_fee_policy": {
      "active": true,
      "broker_fee_usd_per_trade": 3.0,
      "max_buy_fee_as_pct_of_notional": 0.003,
      "max_trade_fee_as_pct_of_notional": 0.003,
      "buy_fee_priority_symbols": [
        "RSIT",
        "RSSB"
      ],
      "buy_fee_min_notional_multiplier_priority": 0.85,
      "buy_fee_min_notional_multiplier_other": 1.15,
      "note_zh": "每筆買入與賣出皆計 broker_fee_usd_per_trade。若該筆手續費÷名目大於 max_trade_fee_as_pct_of_notional（數值可比照 max_buy_fee_as_pct_of_notional），前台不列下單建議（僅見偏低／偏高）。買進名目過小則再等較大金額一筆調；buy_fee_priority_symbols 門檻較低；其餘用 other；清單可空改 default。"
    },
    "cash_usd_in_rebalance_denominator": 10.2,
    "deferred_buy_actions": [],
    "deploy_all_cash_usd": false,
    "exact_target_min_trade_usd": 5.0,
    "phase": {
      "effective_from": "2026-05-19",
      "effective_to": null,
      "id": "phase-c",
      "note": "Hawkish macro: expect rate hikes or end of easing; overweight RSST vs phase-b. Revert to phase-b weights (50/20/15/15) if inflation eases and cuts resume.",
      "targets": [
        {
          "symbol": "RSSB",
          "weight": 0.4
        },
        {
          "symbol": "RSST",
          "weight": 0.3
        },
        {
          "symbol": "RSSY",
          "weight": 0.15
        },
        {
          "symbol": "RSIT",
          "weight": 0.15
        }
      ]
    },
    "positions_mv_usd_for_targets": 42807.2405,
    "rebalance_actions": [],
    "rebalance_denominator_twd": 1344895.8,
    "rebalance_denominator_usd": 42817.4405,
    "rebalance_needed": false,
    "sleeves": [
      {
        "band_high_pct": 48.0,
        "band_low_pct": 32.0,
        "buy_fee_min_notional_usd": null,
        "buy_fee_pct_if_traded": null,
        "current_pct": 43.46,
        "current_units": 605.0,
        "delta_mv_twd": -46518.49,
        "delta_mv_usd": -1481.0088,
        "last_twd": 966.08,
        "last_usd": 30.757,
        "listed": true,
        "mv_twd": 584476.81,
        "mv_usd": 18607.985,
        "recommendation_mode": "in_band",
        "target_mv_twd": 537958.32,
        "target_mv_usd": 17126.9762,
        "status": "ok",
        "symbol": "RSSB",
        "trade_side": "hold",
        "trade_units": null,
        "target_pct": 40.0,
        "yahoo_ticker": "RSSB"
      },
      {
        "band_high_pct": 36.0,
        "band_low_pct": 24.0,
        "buy_fee_min_notional_usd": null,
        "buy_fee_pct_if_traded": null,
        "current_pct": 29.67,
        "current_units": 379.0,
        "delta_mv_twd": 4433.58,
        "delta_mv_usd": 141.152,
        "last_twd": 1052.86,
        "last_usd": 33.52,
        "listed": true,
        "mv_twd": 399035.16,
        "mv_usd": 12704.0802,
        "recommendation_mode": "in_band",
        "target_mv_twd": 403468.74,
        "target_mv_usd": 12845.2322,
        "status": "ok",
        "symbol": "RSST",
        "trade_side": "hold",
        "trade_units": null,
        "target_pct": 30.0,
        "yahoo_ticker": "RSST"
      },
      {
        "band_high_pct": 18.0,
        "band_low_pct": 12.0,
        "buy_fee_min_notional_usd": null,
        "buy_fee_pct_if_traded": null,
        "current_pct": 13.29,
        "current_units": 227.0,
        "delta_mv_twd": 22947.86,
        "delta_mv_usd": 730.5909,
        "last_twd": 787.61,
        "last_usd": 25.075,
        "listed": true,
        "mv_twd": 178786.51,
        "mv_usd": 5692.0252,
        "recommendation_mode": "in_band",
        "target_mv_twd": 201734.37,
        "target_mv_usd": 6422.6161,
        "status": "ok",
        "symbol": "RSSY",
        "trade_side": "hold",
        "trade_units": null,
        "target_pct": 15.0,
        "yahoo_ticker": "RSSY"
      },
      {
        "band_high_pct": 18.0,
        "band_low_pct": 12.0,
        "buy_fee_min_notional_usd": null,
        "buy_fee_pct_if_traded": null,
        "current_pct": 13.55,
        "current_units": 277.0,
        "delta_mv_twd": 19457.42,
        "delta_mv_usd": 619.4659,
        "last_twd": 658.04,
        "last_usd": 20.95,
        "listed": true,
        "mv_twd": 182276.95,
        "mv_usd": 5803.1502,
        "recommendation_mode": "in_band",
        "target_mv_twd": 201734.37,
        "target_mv_usd": 6422.6161,
        "status": "ok",
        "symbol": "RSIT",
        "trade_side": "hold",
        "trade_units": null,
        "target_pct": 15.0,
        "yahoo_ticker": "RSIT"
      }
    ],
    "total_mv_twd": 1344575.42,
    "total_mv_usd": 42807.2405
  },
  "refresh_hint_zh": "",
  "rebalance_log": {
    "schema_version": 1,
    "summary_note_en": "Rebalance log stores recommended actions, executed actions, and the gap between them. Use this file to review whether the strategy was followed.",
    "cost_method_for_realized_pnl": "average_cost",
    "entry_template": {
      "id": "rebalance-YYYYMMDD-unique",
      "decision_date": "YYYY-MM-DD",
      "phase_id": "phase-a",
      "trigger_reason": "rebalance_band_breach",
      "before_weights": [],
      "recommended_actions": [],
      "executed_actions": [],
      "difference_reason": null,
      "fees_usd": null,
      "realized_pnl_usd": null,
      "linked_rule_event_id": null,
      "note_en": "Document recommendation versus execution."
    },
    "entries": [
      {
        "id": "rebalance-20260519-phase-c",
        "decision_date": "2026-05-19",
        "phase_id": "phase-c",
        "trigger_reason": "manual_macro_view",
        "before_weights": {
          "note": "Prior active phase: phase-b (50/20/15/15)."
        },
        "recommended_actions": [
          {
            "action": "shift_targets",
            "targets": "RSSB 40%, RSST 30%, RSSY 15%, RSIT 15%",
            "rationale_en": "Expect rate hikes or end of easing; overweight RSST vs phase-b."
          },
          {
            "action": "buy",
            "symbol": "RSST",
            "note": "Move toward 30% RSST sleeve; further trims/adds TBD by band."
          }
        ],
        "executed_actions": [
          {
            "executed_at": "2026-05-19T22:07:16",
            "symbol": "RSST",
            "side": "buy",
            "units": 37,
            "price_usd": 33.05,
            "total_usd": 1222.85,
            "fee_usd": 3
          },
          {
            "executed_at": "2026-05-21T22:15:05",
            "symbol": "RSST",
            "side": "buy",
            "units": 95,
            "price_usd": 33.33,
            "total_usd": 3166.35,
            "fee_usd": 3
          }
        ],
        "difference_reason": "Target change recorded; RSST adds in progress toward 30% sleeve.",
        "fees_usd": 6,
        "realized_pnl_usd": null,
        "linked_rule_event_id": null,
        "note_en": "Revert to phase-b (50/20/15/15) if easing resumes (e.g. inflation cools)."
      }
    ]
  },
  "record_health": {
    "capital_event_count": 1,
    "cash_snapshot_count": 0,
    "latest_cash_snapshot_as_of": null,
    "rule_event_count": 0,
    "rebalance_log_count": 1,
    "income_event_count": 0,
    "pending_followup_count": 4,
    "first_pending_followup_zh": "自有資金投入待補：首次自有資金投入日期、金額、幣別，以及未來每月定期定額規則。"
  },
  "quotes": [
    {
      "listed": true,
      "symbol": "RSSB",
      "yahoo_ticker": "RSSB",
      "last_usd": 30.756999969482422,
      "units": 605.0,
      "avg_entry_usd": 29.741008,
      "unrealized_pnl_usd": 614.67,
      "last_twd": 966.08
    },
    {
      "listed": true,
      "symbol": "RSIT",
      "yahoo_ticker": "RSIT",
      "last_usd": 20.950000762939453,
      "units": 277.0,
      "avg_entry_usd": 20.511011,
      "unrealized_pnl_usd": 121.6,
      "last_twd": 658.04
    },
    {
      "listed": true,
      "symbol": "RSST",
      "yahoo_ticker": "RSST",
      "last_usd": 33.52000045776367,
      "units": 379.0,
      "avg_entry_usd": 32.432665,
      "unrealized_pnl_usd": 412.1,
      "last_twd": 1052.86
    },
    {
      "listed": true,
      "symbol": "RSSY",
      "yahoo_ticker": "RSSY",
      "last_usd": 25.075000762939453,
      "units": 227.0,
      "avg_entry_usd": 24.761982,
      "unrealized_pnl_usd": 71.06,
      "last_twd": 787.61
    },
    {
      "listed": true,
      "symbol": "BOXX",
      "yahoo_ticker": "BOXX",
      "last_usd": 116.83999633789062,
      "units": 0.0,
      "avg_entry_usd": null,
      "unrealized_pnl_usd": null,
      "last_twd": 3669.94,
      "cash_like": true
    },
    {
      "symbol": "SPY",
      "yahoo_ticker": "SPY",
      "last_usd": 750.4600219726562,
      "benchmark": true
    },
    {
      "symbol": "SSO",
      "yahoo_ticker": "SSO",
      "last_usd": 68.37999725341797,
      "benchmark": true
    }
  ],
  "realized_pnl": {
    "cost_method": "average_cost",
    "total_realized_pnl_usd": 431.73,
    "sell_count": 8,
    "rows": [
      {
        "executed_at": "2026-04-16T21:55:46",
        "symbol": "RSSB",
        "side": "sell",
        "units": 321.0,
        "net_proceeds_usd": 9402.1,
        "cost_basis_usd": 9354.12,
        "realized_pnl_usd": 47.98
      },
      {
        "executed_at": "2026-04-16T21:56:12",
        "symbol": "RSST",
        "side": "sell",
        "units": 217.0,
        "net_proceeds_usd": 6689.14,
        "cost_basis_usd": 6596.4,
        "realized_pnl_usd": 92.74
      },
      {
        "executed_at": "2026-04-16T21:59:33",
        "symbol": "RSSY",
        "side": "sell",
        "units": 121.0,
        "net_proceeds_usd": 2881.58,
        "cost_basis_usd": 2840.45,
        "realized_pnl_usd": 41.13
      },
      {
        "executed_at": "2026-04-17T03:59:53",
        "symbol": "RSSY",
        "side": "sell",
        "units": 41.0,
        "net_proceeds_usd": 978.51,
        "cost_basis_usd": 962.47,
        "realized_pnl_usd": 16.04
      },
      {
        "executed_at": "2026-04-17T03:59:54",
        "symbol": "RSST",
        "side": "sell",
        "units": 73.0,
        "net_proceeds_usd": 2262.14,
        "cost_basis_usd": 2219.07,
        "realized_pnl_usd": 43.07
      },
      {
        "executed_at": "2026-04-17T23:20:53",
        "symbol": "RSSB",
        "side": "sell",
        "units": 117.0,
        "net_proceeds_usd": 3495.22,
        "cost_basis_usd": 3409.45,
        "realized_pnl_usd": 85.77
      },
      {
        "executed_at": "2026-04-30T22:16:50",
        "symbol": "BOXX",
        "side": "sell",
        "units": 289.0,
        "net_proceeds_usd": 33673.47,
        "cost_basis_usd": 33650.82,
        "realized_pnl_usd": 22.65
      },
      {
        "executed_at": "2026-05-07T22:12:48",
        "symbol": "RSST",
        "side": "sell",
        "units": 100.0,
        "net_proceeds_usd": 3247.93,
        "cost_basis_usd": 3165.59,
        "realized_pnl_usd": 82.34
      }
    ],
    "total_realized_pnl_twd": 13560.64
  },
  "rule_events": {
    "schema_version": 1,
    "summary_note_en": "Rule events log when a strategy rule was observed, triggered, ignored, or completed. This is the trigger history, not the execution ledger.",
    "entry_template": {
      "id": "rule-YYYYMMDD-unique",
      "event_date": "YYYY-MM-DD",
      "detected_at": "YYYY-MM-DDTHH:MM:SS",
      "rule_type": "drawdown_add",
      "status": "triggered",
      "phase_id": "phase-a",
      "metric_name": "nav_drawdown_pct",
      "metric_value": -20.0,
      "threshold_value": -20.0,
      "target_symbol": "RSSB",
      "suggested_actions": [],
      "linked_rebalance_id": null,
      "note_en": "Describe what rule fired and why."
    },
    "events": [],
    "rule_type_reference": {
      "drawdown_add": "NAV fell from peak enough to trigger extra capital deployment.",
      "rebalance_band_breach": "Allocation drift exceeded the configured band.",
      "monthly_contribution_target": "Rule selected a target sleeve for the next contribution.",
      "manual_override": "User intentionally overrode the default rule."
    },
    "status_reference": {
      "observed": "Condition detected but no action decided yet.",
      "triggered": "Condition confirmed and awaiting action.",
      "executed": "Action completed and linked to a log entry.",
      "dismissed": "Condition intentionally ignored or cancelled."
    }
  },
  "spy_compare_chart": {
    "caption_zh": "",
    "labels": [
      "2026-04-14T22:07:04",
      "2026-04-14",
      "2026-04-15",
      "2026-04-16",
      "2026-04-17",
      "2026-04-20",
      "2026-04-21",
      "2026-04-22",
      "2026-04-23",
      "2026-04-24",
      "2026-04-27",
      "2026-04-28",
      "2026-04-29",
      "2026-04-30",
      "2026-05-01",
      "2026-05-04",
      "2026-05-05",
      "2026-05-06",
      "2026-05-07",
      "2026-05-08",
      "2026-05-11",
      "2026-05-12",
      "2026-05-13",
      "2026-05-14",
      "2026-05-15",
      "2026-05-18",
      "2026-05-19",
      "2026-05-20",
      "2026-05-21",
      "2026-05-22",
      "2026-05-26",
      "2026-05-27"
    ],
    "datasets": [
      {
        "id": "spy_shadow",
        "label": "SPY 影子（跟你的買賣／現金）",
        "borderColor": "#8c5f34",
        "data": [
          100.0,
          100.591,
          101.3847,
          101.6339,
          102.8622,
          102.6565,
          101.9844,
          103.0172,
          102.6174,
          103.4126,
          103.5908,
          103.0867,
          103.0708,
          104.0963,
          104.3845,
          104.0021,
          104.8365,
          106.2936,
          105.9677,
          106.8426,
          107.086,
          106.9237,
          107.5219,
          108.3707,
          107.0671,
          106.9918,
          106.2791,
          107.3684,
          107.5813,
          108.0043,
          108.7213,
          108.7025
        ]
      },
      {
        "id": "sso_shadow",
        "label": "SSO 正二影子（跟你的買賣／現金）",
        "borderColor": "#6f5a9a",
        "data": [
          100.0,
          101.1749,
          102.7356,
          103.2158,
          105.6856,
          105.2568,
          103.9019,
          105.96,
          105.1539,
          106.6975,
          107.0577,
          105.9943,
          105.9772,
          107.9839,
          108.5842,
          107.8124,
          109.476,
          112.5289,
          111.7914,
          113.5752,
          114.0726,
          113.7638,
          115.0159,
          116.7996,
          113.9353,
          113.7295,
          112.2545,
          114.5528,
          114.9644,
          115.7877,
          117.297,
          117.2798
        ]
      }
    ]
  },
  "trade_ledger": {
    "count": 21,
    "trades": [
      {
        "executed_at": "2026-04-14T22:07:04",
        "symbol": "RSST",
        "side": "buy",
        "units": 363,
        "price_usd": 30.3899,
        "fee_usd": 3,
        "total_usd": 11031.53,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 35.241889,
        "nav_touch_equity_delta_usd": 11093.279806,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 690.38,
            "source": "intraday_5m",
            "bar_at": "2026-04-14T10:05:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 58.305,
            "source": "intraday_5m",
            "bar_at": "2026-04-14T10:05:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-14T22:08:50",
        "symbol": "RSSB",
        "side": "buy",
        "units": 538,
        "price_usd": 29.135,
        "fee_usd": 3,
        "total_usd": 15674.63,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 50.163705,
        "nav_touch_equity_delta_usd": 15790.300205,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 690.38,
            "source": "intraday_5m",
            "bar_at": "2026-04-14T10:05:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 58.305,
            "source": "intraday_5m",
            "bar_at": "2026-04-14T10:05:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-14T22:11:59",
        "symbol": "RSSY",
        "side": "buy",
        "units": 203,
        "price_usd": 23.46,
        "fee_usd": 3,
        "total_usd": 4762.38,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 15.181047,
        "nav_touch_equity_delta_usd": 4778.620186,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 690.8799,
            "source": "intraday_5m",
            "bar_at": "2026-04-14T10:10:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 58.3973,
            "source": "intraday_5m",
            "bar_at": "2026-04-14T10:10:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-16T21:55:46",
        "symbol": "RSSB",
        "side": "sell",
        "units": 321,
        "price_usd": 29.3,
        "fee_usd": 3,
        "other_fees_usd": 0.2,
        "total_usd": 9405.3,
        "broker": "manual_import",
        "note": "Expected US equity cascade drawdown; raise cash target ~85%, keep ~15% invested (avg-cost basis in flows).",
        "nav_touch_pts": -74.436396,
        "nav_touch_equity_delta_usd": -9443.820024,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 699.48,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T09:55:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 59.83,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T09:55:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-16T21:56:12",
        "symbol": "RSST",
        "side": "sell",
        "units": 217,
        "price_usd": 30.84,
        "fee_usd": 3,
        "other_fees_usd": 0.14,
        "total_usd": 6692.28,
        "broker": "manual_import",
        "note": "Expected US equity cascade drawdown; raise cash target ~85%, keep ~15% invested (avg-cost basis in flows).",
        "nav_touch_pts": -53.05657,
        "nav_touch_equity_delta_usd": -6731.340099,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 699.48,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T09:55:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 59.83,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T09:55:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-16T21:59:33",
        "symbol": "RSSY",
        "side": "sell",
        "units": 121,
        "price_usd": 23.84,
        "fee_usd": 3,
        "other_fees_usd": 0.06,
        "total_usd": 2884.64,
        "broker": "manual_import",
        "note": "Expected US equity cascade drawdown; raise cash target ~85%, keep ~15% invested (avg-cost basis in flows).",
        "nav_touch_pts": -22.822631,
        "nav_touch_equity_delta_usd": -2895.530037,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 699.48,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T09:55:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 59.83,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T09:55:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-17T03:59:53",
        "symbol": "RSSY",
        "side": "sell",
        "units": 41,
        "price_usd": 23.94,
        "fee_usd": 3,
        "other_fees_usd": 0.03,
        "total_usd": 981.54,
        "broker": "manual_import",
        "note": "Expected US equity cascade drawdown; raise cash target ~85%, keep ~15% invested (avg-cost basis in flows).",
        "nav_touch_pts": -16.075767,
        "nav_touch_equity_delta_usd": -979.899984,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 701.55,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T15:55:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 60.18,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T15:55:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-17T03:59:54",
        "symbol": "RSST",
        "side": "sell",
        "units": 73,
        "price_usd": 31.03,
        "fee_usd": 3,
        "other_fees_usd": 0.05,
        "total_usd": 2265.19,
        "broker": "manual_import",
        "note": "Expected US equity cascade drawdown; raise cash target ~85%, keep ~15% invested (avg-cost basis in flows).",
        "nav_touch_pts": -37.449041,
        "nav_touch_equity_delta_usd": -2282.710033,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 701.55,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T15:55:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 60.18,
            "source": "intraday_5m",
            "bar_at": "2026-04-16T15:55:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-17T23:20:53",
        "symbol": "RSSB",
        "side": "sell",
        "units": 117,
        "price_usd": 29.9,
        "fee_usd": 3,
        "other_fees_usd": 0.08,
        "total_usd": 3498.3,
        "broker": "manual_import",
        "note": "Expected US equity cascade drawdown; raise cash target ~85%, keep ~15% invested (avg-cost basis in flows).",
        "nav_touch_pts": -57.343438,
        "nav_touch_equity_delta_usd": -3495.375,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 710.48,
            "source": "intraday_5m",
            "bar_at": "2026-04-17T11:20:00-04:00",
            "interval": "5m"
          },
          "SSO": {
            "price_usd": 61.69,
            "source": "intraday_5m",
            "bar_at": "2026-04-17T11:20:00-04:00",
            "interval": "5m"
          }
        }
      },
      {
        "executed_at": "2026-04-20T21:51:39",
        "symbol": "BOXX",
        "side": "buy",
        "units": 259,
        "price_usd": 116.4161,
        "fee_usd": 3,
        "total_usd": 30151.77,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 0.0,
        "nav_touch_equity_delta_usd": 0.0
      },
      {
        "executed_at": "2026-04-21T23:38:48",
        "symbol": "BOXX",
        "side": "buy",
        "units": 30,
        "price_usd": 116.435,
        "fee_usd": 3,
        "total_usd": 3493.05,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 0.0,
        "nav_touch_equity_delta_usd": 0.0
      },
      {
        "executed_at": "2026-04-30T22:16:50",
        "symbol": "BOXX",
        "side": "sell",
        "units": 289,
        "price_usd": 116.53,
        "fee_usd": 3,
        "other_fees_usd": 0.7,
        "total_usd": 33677.17,
        "broker": "manual_import",
        "note": "Sell BOXX: total_usd gross credit; net in = total_usd - fee_usd - other_fees_usd.",
        "nav_touch_pts": 0.0,
        "nav_touch_equity_delta_usd": 0.0
      },
      {
        "executed_at": "2026-05-04T22:16:19",
        "symbol": "RSSY",
        "side": "buy",
        "units": 149,
        "price_usd": 25,
        "fee_usd": 3,
        "total_usd": 3725,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 11.831418,
        "nav_touch_equity_delta_usd": 3722.765091,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 721.2,
            "source": "intraday_1m",
            "bar_at": "2026-05-04T10:16:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 63.41,
            "source": "intraday_1m",
            "bar_at": "2026-05-04T10:16:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "executed_at": "2026-05-04T22:17:01",
        "symbol": "RSST",
        "side": "buy",
        "units": 274,
        "price_usd": 31.98,
        "fee_usd": 3,
        "total_usd": 8762.52,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 27.813564,
        "nav_touch_equity_delta_usd": 8751.560146,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 721.17,
            "source": "intraday_1m",
            "bar_at": "2026-05-04T10:17:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 63.4099,
            "source": "intraday_1m",
            "bar_at": "2026-05-04T10:17:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "executed_at": "2026-05-04T22:18:15",
        "symbol": "RSSB",
        "side": "buy",
        "units": 433,
        "price_usd": 29.7299,
        "fee_usd": 3,
        "total_usd": 12873.05,
        "broker": "manual_import",
        "note": "Buy: total_usd = fill principal; cash out = total_usd + fee_usd.",
        "nav_touch_pts": 40.62332,
        "nav_touch_equity_delta_usd": 12782.160198,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 721.345,
            "source": "intraday_1m",
            "bar_at": "2026-05-04T10:18:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 63.43,
            "source": "intraday_1m",
            "bar_at": "2026-05-04T10:18:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "broker": "manual_import",
        "executed_at": "2026-05-07T22:09:58",
        "fee_usd": 3,
        "note": "phase-b rebalance sleeve adds.",
        "price_usd": 25.07,
        "side": "buy",
        "symbol": "RSSY",
        "total_usd": 927.59,
        "units": 37,
        "nav_touch_pts": 2.504124,
        "nav_touch_equity_delta_usd": 929.402981,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 734.69,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:09:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 65.7399,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:09:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "broker": "manual_import",
        "executed_at": "2026-05-07T22:12:48",
        "fee_usd": 3,
        "note": "phase-b rebalance trim RSST.",
        "other_fees_usd": 0.07,
        "price_usd": 32.51,
        "side": "sell",
        "symbol": "RSST",
        "total_usd": 3251,
        "units": 100,
        "nav_touch_pts": -8.759285,
        "nav_touch_equity_delta_usd": -3250.999832,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 734.7,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:12:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 65.765,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:12:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "broker": "manual_import",
        "executed_at": "2026-05-07T22:14:40",
        "fee_usd": 3,
        "note": "phase-b open RSIT sleeve.",
        "price_usd": 20.5,
        "side": "buy",
        "symbol": "RSIT",
        "total_usd": 5678.5,
        "units": 277,
        "nav_touch_pts": 15.157982,
        "nav_touch_equity_delta_usd": 5625.869852,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 734.52,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:14:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 65.73,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:14:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "broker": "manual_import",
        "executed_at": "2026-05-07T22:27:59",
        "fee_usd": 3,
        "note": "phase-b add RSSB; no RSST trim.",
        "price_usd": 30.56,
        "side": "buy",
        "symbol": "RSSB",
        "total_usd": 2200.32,
        "units": 72,
        "nav_touch_pts": 5.868263,
        "nav_touch_equity_delta_usd": 2178.0,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 734.72,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:27:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 65.78,
            "source": "intraday_1m",
            "bar_at": "2026-05-07T10:26:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "broker": "manual_import",
        "executed_at": "2026-05-19T22:07:16",
        "fee_usd": 3,
        "note": "phase-c: add RSST toward 30% target (hawkish rates / end of easing).",
        "price_usd": 33.05,
        "side": "buy",
        "symbol": "RSST",
        "total_usd": 1222.85,
        "units": 37,
        "nav_touch_pts": 3.199077,
        "nav_touch_equity_delta_usd": 1226.550056,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 733.07,
            "source": "intraday_1m",
            "bar_at": "2026-05-19T10:07:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 65.33,
            "source": "intraday_1m",
            "bar_at": "2026-05-19T10:07:00-04:00",
            "interval": "1m"
          }
        }
      },
      {
        "broker": "manual_import",
        "executed_at": "2026-05-21T22:15:05",
        "fee_usd": 3,
        "note": "phase-c: add RSST toward 30% target.",
        "price_usd": 33.33,
        "side": "buy",
        "symbol": "RSST",
        "total_usd": 3166.35,
        "units": 95,
        "nav_touch_pts": 7.662231,
        "nav_touch_equity_delta_usd": 3180.599957,
        "shadow_benchmark_fills": {
          "SPY": {
            "price_usd": 738.58,
            "source": "intraday_1m",
            "bar_at": "2026-05-21T10:15:00-04:00",
            "interval": "1m"
          },
          "SSO": {
            "price_usd": 66.37,
            "source": "intraday_1m",
            "bar_at": "2026-05-21T10:15:00-04:00",
            "interval": "1m"
          }
        }
      }
    ]
  },
  "usd_twd": 31.40999984741211,
  "usd_twd_source": "yahoo"
};
