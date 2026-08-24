# Current Summary

- Generated on: 2026-08-24
- Snapshot date: 2026-08-24
- Purpose: portable summary for future AI review and handoff.

## Current State

- Net worth: TWD 45,692
- Market value: TWD 1,340,428 / USD 42,122.69
- Remaining liability: TWD 1,294,934
- NAV index: 106.92
- Unrealized PnL: USD —
- Unrealized PnL in TWD view: TWD 47,207
- Market vs debt: 103.51% market coverage
- Next loan payment: 2026-09-13 / TWD 18,765

## Capital Structure

- External capital events: 2 (active months: 2)
- Debt-funded capital: TWD 1,350,000 / USD 0.00
- Self-funded capital: TWD 0 / USD 0.00
- Total external capital logged: TWD 1,350,000 / USD -900.00
- Average external contribution per active month: TWD 675,000 / USD -450.00
- Deployed capital into positions: USD 40,806.58
- TWD invested cost basis: TWD 1,293,221 (historical_fx_log)

## Holdings

- RSSB: 488.0000 units, last USD 31.01
- RSIT: 299.0000 units, last USD 21.21
- RSST: 303.0000 units, last USD 33.39
- RSSY: 248.0000 units, last USD 25.55
- WQTM: 130.0000 units, last USD 32.26
- BOXX: 0.0000 units, last USD 117.93

## Rules And Risk

- Rebalance band: ±20% of target weight
- Drawdown add trigger: 20% below peak NAV
- Peak NAV reference set: no
- Rule events logged: 0 / Rebalance logs: 2
- Income events logged: 0

## Data Coverage

- Trades logged: 27
- FX events logged: 12
- NAV history days: 93
- Cash snapshots logged: 0 (missing)

## Missing Information

- 自有資金投入待補：首次自有資金投入日期、金額、幣別，以及未來每月定期定額規則。
- 貸款實際扣款待補：首期扣款後請補 paid_at、payment_twd、principal_twd、interest_twd、remaining_balance_twd。
- 配息與分配待補：之後若有配息，請補 gross、tax、net、destination、是否再投入。
- 規則執行待補：若發生跌破高點 20% 加碼、再平衡或手動覆寫，請補建議與實際執行內容。

## Intake Checklist For Next AI

- New trade: need executed_at, symbol, side, units, average price, total amount, fee.
- Capital addition: need date, source kind, amount, currency, and whether it counts as strategy capital.
- Cash snapshot: need as_of, bucket, currency, amount, and location.
- Loan payment: need paid_at, total payment, principal, interest, and remaining balance if available.
- Dividend: need symbol, ex_date or pay_date, gross, tax, net, and destination.
- Rebalance action: need trigger reason, recommended action, executed action, and why they differ.

## Timeline

- 2026-08-24T23:51:08: Trade: buy WQTM / 130.0000 units / USD 4,230.20
- 2026-08-24T23:49:28: Trade: buy RSSY / 21.0000 units / USD 536.34
- 2026-08-24T23:48:39: Trade: buy RSIT / 22.0000 units / USD 465.52
- 2026-08-24T23:47:13: Trade: sell RSST / 76.0000 units / USD 2,544.10
- 2026-08-24T23:46:46: Trade: sell RSSB / 87.0000 units / USD 2,700.48
- 2026-08-04T12:51:00+08:00: Capital: withdrawal_from_strategy / TWD — / USD -900.00
- 2026-07-30T22:15:22: Trade: sell RSSB / 30.0000 units / USD 901.50
- 2026-05-21T22:15:05: Trade: buy RSST / 95.0000 units / USD 3,166.35
- 2026-05-21: FX: TWD 100,000 -> USD 3,164.56 @ 31.6000
- 2026-05-19T22:07:16: Trade: buy RSST / 37.0000 units / USD 1,222.85
- 2026-05-19: FX: TWD 38,000 -> USD 1,200.25 @ 31.6601
- 2026-05-07T22:27:59: Trade: buy RSSB / 72.0000 units / USD 2,200.32
- 2026-05-07T22:14:40: Trade: buy RSIT / 277.0000 units / USD 5,678.50
- 2026-05-07T22:12:48: Trade: sell RSST / 100.0000 units / USD 3,251.00
- 2026-05-07T22:09:58: Trade: buy RSSY / 37.0000 units / USD 927.59
- 2026-05-07: FX: TWD 72,305 -> USD 2,304.17 @ 31.3800
- 2026-05-06: FX: TWD 157,450 -> USD -5,000.00 @ 31.4900
- 2026-05-05: FX: TWD 31,577 -> USD -998.00 @ 31.6398
- 2026-05-04T22:18:15: Trade: buy RSSB / 433.0000 units / USD 12,873.05
- 2026-05-04T22:17:01: Trade: buy RSST / 274.0000 units / USD 8,762.52

## Files Of Truth

- `chronicle/data/portfolio.json`: current holdings and valuation config.
- `chronicle/data/trades.json`: executed trade log.
- `chronicle/data/investment_flows.json`: deployed capital into positions.
- `chronicle/data/capital_events.json`: full strategy funding ledger.
- `chronicle/data/cash_buckets.json`: strategy cash snapshots.
- `chronicle/data/rule_events.json`: trigger history.
- `chronicle/data/rebalance_log.json`: recommended vs executed rebalance actions.
- `chronicle/data/income_events.json`: dividends and income routing.
- `chronicle/data/ledger_intent.json`: human-approved intent and pending follow-ups.
