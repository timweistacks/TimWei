import json
import os
import yfinance as yf
import pandas as pd

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    portfolio_path = os.path.join(current_dir, "..", "..", "data", "personal_ledger", "portfolio.json")

    with open(portfolio_path, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)

    # 取得最新匯率與股價
    usd_twd_rate = portfolio['valuation'].get('usd_twd_rate', 32.0)
    try:
        usdtwd_data = yf.download("USDTWD=X", period="1d")
        if not usdtwd_data.empty:
            if isinstance(usdtwd_data.columns, pd.MultiIndex):
                usd_twd_rate = usdtwd_data['Close'].iloc[-1].values[0]
            else:
                usd_twd_rate = usdtwd_data['Close'].iloc[-1]
    except:
        pass

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

    # ==========================================
    # 模擬階段一：今天買完 36 股 RSST 後的狀態
    # ==========================================
    positions['RSST'] += 36
    mv_after_step1 = {t: positions.get(t, 0) * prices.get(t, 0) for t in tickers}
    total_invested_after_step1 = sum(mv_after_step1.values())
    
    # 今天買完後剩下的零錢 (從前一次計算得知為 $32.56)
    rem_cash_step1 = 32.56

    print("=" * 60)
    print("【 兩天後 (階段二) 的資金現況模擬 】")
    print("=" * 60)
    print("假設今天已經買完 36 股 RSST...")
    
    # 兩天後 10 萬台幣入帳
    cash_usd_future = 100000 / usd_twd_rate
    total_deployable_usd = rem_cash_step1 + cash_usd_future
    
    print(f"[*] 階段一剩餘零錢: ${rem_cash_step1:,.2f}")
    print(f"[*] 兩天後新入金 (10萬台幣): 約 ${cash_usd_future:,.2f}")
    print(f"[*] 總可用資金: ${total_deployable_usd:,.2f}")

    print("\n[ 買完第一階段後的持倉比例 ]")
    for t in tickers:
        pct = mv_after_step1[t] / total_invested_after_step1 * 100 if total_invested_after_step1 > 0 else 0
        print(f"  {t}: ${mv_after_step1[t]:,.2f} ({pct:.1f}%) | 股數: {positions.get(t, 0)}")

    # 目標 40/30/15/15
    targets = {'RSSB': 0.40, 'RSST': 0.30, 'RSSY': 0.15, 'RSIT': 0.15}
    total_future_step2 = total_invested_after_step1 + total_deployable_usd

    shortfalls_2 = {t: (total_future_step2 * targets[t]) - mv_after_step1[t] for t in tickers}

    print("\n" + "=" * 60)
    print("【 兩天後的目標缺口 (往 40/30/15/15 靠攏) 】")
    print("=" * 60)
    for t in tickers:
        status = "落後" if shortfalls_2[t] > 0 else "超標"
        print(f"  {t}: 差距: {status} ${abs(shortfalls_2[t]):,.0f}")

    # 找最大缺口 All-in
    best_target_2 = max(shortfalls_2, key=shortfalls_2.get)

    print("\n" + "=" * 60)
    print("【 實戰買進建議 (考量 $3 手續費，絕對不碎步進場) 】")
    print("=" * 60)
    if shortfalls_2[best_target_2] > 0 and total_deployable_usd > 100:
        shares = int((total_deployable_usd - 3) / prices[best_target_2])
        cost = shares * prices[best_target_2]
        rem_cash_final = total_deployable_usd - cost - 3
        
        print(f"  ✅ All-in 買進 {best_target_2}: {shares} 股 (約花費 ${cost:,.2f})")
        print(f"  💸 預估手續費: $3")
        print(f"  💰 兩次都買完後，帳上最終剩餘現金: ${rem_cash_final:,.2f}")

        # 兩次都買完後的比例
        mv_final = mv_after_step1.copy()
        mv_final[best_target_2] += cost
        total_final = sum(mv_final.values())

        print("\n[ 兩天後買完的【最終持倉比例】 ]")
        for t in tickers:
            pct = mv_final[t] / total_final * 100 if total_final > 0 else 0
            diff = pct - (targets[t] * 100)
            print(f"  {t}: ${mv_final[t]:,.2f} ({pct:.1f}%) | 目標: {targets[t]*100:.0f}% | 偏差: {diff:+.1f}%")
    else:
        print("  資金過小，不建議進場。")

if __name__ == '__main__':
    main()
