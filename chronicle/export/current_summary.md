# Current Summary

- Generated on: 2026-05-22
- Snapshot date: 2026-05-22
- Purpose: portable summary for future AI review and handoff.

## Current State

- Net worth: TWD 566
- Market value: TWD 1,336,472 / USD 42,456.00
- Remaining liability: TWD 1,336,228
- NAV index: 105.46
- Unrealized PnL: USD —
- Unrealized PnL in TWD view: TWD 20,985
- Market vs debt: 100.02% market coverage
- Next loan payment: 2026-06-13 / TWD 18,765

## Capital Structure

- External capital events: 1 (active months: 1)
- Debt-funded capital: TWD 1,350,000 / USD 0.00
- Self-funded capital: TWD 0 / USD 0.00
- Total external capital logged: TWD 1,350,000 / USD 0.00
- Average external contribution per active month: TWD 1,350,000 / USD 0.00
- Deployed capital into positions: USD 41,510.10
- TWD invested cost basis: TWD 1,315,487 (historical_fx_log)

## Holdings

- RSSB: 605.0000 units, last USD 30.28
- RSIT: 277.0000 units, last USD 20.84
- RSST: 379.0000 units, last USD 33.48
- RSSY: 227.0000 units, last USD 25.00
- BOXX: 0.0000 units, last USD 116.78

## Rules And Risk

- Rebalance band: ±20% of target weight
- Drawdown add trigger: 20% below peak NAV
- Peak NAV reference set: no
- Rule events logged: 0 / Rebalance logs: 1
- Income events logged: 0

## Data Coverage

- Trades logged: 21
- FX events logged: 12
- NAV history days: 28
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
- 2026-05-04T22:16:19: Trade: buy RSSY / 149.0000 units / USD 3,725.00
- 2026-04-30T22:16:50: Trade: sell BOXX / 289.0000 units / USD 33,677.17
- 2026-04-27: FX: TWD 30,000 -> USD 954.50 @ 31.4300
- 2026-04-21T23:38:48: Trade: buy BOXX / 30.0000 units / USD 3,493.05
- 2026-04-20T21:51:39: Trade: buy BOXX / 259.0000 units / USD 30,151.77
- 2026-04-20: FX: TWD 100,000 -> USD 3,167.56 @ 31.5700
- 2026-04-20: FX: TWD 50,000 -> USD 1,586.29 @ 31.5200

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
