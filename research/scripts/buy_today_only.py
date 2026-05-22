import json
import os
import yfinance as yf
import pandas as pd

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    portfolio_path = os.path.join(current_dir, "..", "..", "data", "personal_ledger", "portfolio.json")

    with open(portfolio_path, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    cash_usd_today = portfolio.get('cash_usd', 0)
    tickers = ['RSSB', 'RSST', 'RSSY', 'RSIT']
    positions = {p['symbol']: p['units'] for p in portfolio['positions'] if p['symbol'] in tickers}

    prices = {}
    try:
        data = yf.download(tickers, period="1d")
        for ticker in tickers:
            if isinstance(data.columns, pd.MultiIndex):
                prices[ticker] = float(data['Close'][ticker].iloc[-1])
            else:
                prices[ticker] = float(data['Close'].iloc[-1])
    except Exception as e:
        print(f"抓取最新股價失敗: {e}")
        return

    mv_initial = {t: positions.get(t, 0) * prices.get(t, 0) for t in tickers}
    total_invested = sum(mv_initial.values())

    print("=" * 60)
    print("【 資金現況盤點 】")
    print("=" * 60)
    print(f"[*] 階段一資金 (今天帳上餘額): ${cash_usd_today:,.2f}")
    print(f"[*] 階段二資金 (兩天後): $0.00")
    print("\n[ 目前真實持倉狀態 ]")
    for t in tickers:
        pct = mv_initial[t] / total_invested * 100 if total_invested > 0 else 0
        print(f"  {t}: ${mv_initial[t]:,.2f} ({pct:.1f}%) | 股數: {positions.get(t, 0)} | 最新單價: ${prices[t]:.2f}")

    # 目標 40/30/15/15
    targets = {'RSSB': 0.40, 'RSST': 0.30, 'RSSY': 0.15, 'RSIT': 0.15}
    total_future = total_invested + cash_usd_today

    shortfalls = {t: (total_future * targets[t]) - mv_initial[t] for t in tickers}

    print("\n" + "=" * 60)
    print("【 理想目標缺口 (往 40/30/15/15 靠攏) 】")
    print("=" * 60)
    for t in tickers:
        status = "落後" if shortfalls[t] > 0 else "超標"
        print(f"  {t}: 目標 ${total_future * targets[t]:,.0f} | 差距: {status} ${abs(shortfalls[t]):,.0f}")

    # 找最大缺口 All-in
    best_target = max(shortfalls, key=shortfalls.get)

    print("\n" + "=" * 60)
    print("【 實戰買進建議 (考量 $3 手續費，絕對不碎步進場) 】")
    print("=" * 60)
    if shortfalls[best_target] > 0 and cash_usd_today > 100:
        shares = int((cash_usd_today - 3) / prices[best_target])
        cost = shares * prices[best_target]
        rem_cash = cash_usd_today - cost - 3
        print(f"  ✅ All-in 買進 {best_target}: {shares} 股 (約花費 ${cost:,.2f})")
        print(f"  💸 預估手續費: $3")
        print(f"  💰 買完後帳上剩餘現金: ${rem_cash:,.2f}")

        # 買完後的比例
        mv_final = mv_initial.copy()
        mv_final[best_target] += cost
        total_final = sum(mv_final.values())

        print("\n[ 執行這筆交易後的【最終持倉比例】 ]")
        for t in tickers:
            pct = mv_final[t] / total_final * 100 if total_final > 0 else 0
            diff = pct - (targets[t] * 100)
            print(f"  {t}: ${mv_final[t]:,.2f} ({pct:.1f}%) | 目標: {targets[t]*100:.0f}% | 偏差: {diff:+.1f}%")
    else:
        print("  資金過小，不建議進場。")

if __name__ == '__main__':
    main()
