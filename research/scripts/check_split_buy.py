import json
import os
import yfinance as yf
import pandas as pd

def print_portfolio_status(mv, total_usd):
    for t, m in mv.items():
        pct = m / total_usd * 100 if total_usd > 0 else 0
        print(f"  {t}: ${m:,.2f} ({pct:.1f}%)")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    portfolio_path = os.path.join(current_dir, "..", "..", "data", "personal_ledger", "portfolio.json")
    
    with open(portfolio_path, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)
        
    cash_usd_today = portfolio.get('cash_usd', 0)
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

    cash_usd_future = 100000 / usd_twd_rate
    
    tickers = ['RSSB', 'RSST', 'RSSY', 'RSIT']
    positions = {p['symbol']: p['units'] for p in portfolio['positions'] if p['symbol'] in tickers}
    
    prices = {}
    try:
        data = yf.download(tickers, period="1d")
        for ticker in tickers:
            if isinstance(data.columns, pd.MultiIndex):
                prices[ticker] = data['Close'][ticker].iloc[-1]
            else:
                prices[ticker] = data['Close'].iloc[-1]
    except Exception as e:
        print(f"抓取最新股價失敗: {e}")
        return

    mv_initial = {t: positions.get(t, 0) * prices.get(t, 0) for t in tickers}
    total_invested_initial = sum(mv_initial.values())
    
    print(f"[*] 目前匯率設定: {usd_twd_rate:.2f} TWD/USD")
    print(f"[*] 階段一資金 (今天): ${cash_usd_today:,.2f}")
    print(f"[*] 階段二資金 (兩天後): 10萬台幣 約 ${cash_usd_future:,.2f}")
    print("\n【 原始真實持倉比例 】")
    print_portfolio_status(mv_initial, total_invested_initial)
    
    def simulate_two_step_buy(targets, title):
        print(f"\n==================================================")
        print(f" 方案：往 {title} 目標靠攏")
        print(f"==================================================")
        
        # 複製目前狀態
        mv_current = mv_initial.copy()
        pos_current = positions.copy()
        total_inv_current = total_invested_initial
        
        # ------------------------------------------------
        # 階段一：今天投入 cash_usd_today
        # ------------------------------------------------
        print("\n▶ [ 階段一：今天進場 ]")
        print(f"  可用資金: ${cash_usd_today:,.2f}")
        
        # 計算理想目標與缺口
        target_mvs_1 = {t: (total_inv_current + cash_usd_today) * pct for t, pct in targets.items()}
        shortfalls_1 = {t: target_mvs_1[t] - mv_current[t] for t, pct in targets.items()}
        
        # 挑選缺口最大的標的 All-in
        best_target_1 = max(shortfalls_1, key=shortfalls_1.get)
        
        if shortfalls_1[best_target_1] > 0 and cash_usd_today > 100:
            shares_1 = int((cash_usd_today - 3) / prices[best_target_1]) # 扣除手續費
            cost_1 = shares_1 * prices[best_target_1]
            rem_cash_1 = cash_usd_today - cost_1 - 3
            
            # 更新狀態
            pos_current[best_target_1] += shares_1
            mv_current[best_target_1] += cost_1
            total_inv_current += cost_1
            
            print(f"  ✅ 買進 {best_target_1}: {shares_1} 股 (花費 ${cost_1:,.2f} + $3 手續費)")
            print(f"  今天買完後，剩餘現金: ${rem_cash_1:,.2f}")
        else:
            print("  資金過小或無需買進。")
            rem_cash_1 = cash_usd_today
            
        print("  [ 今天買完後的比例 ]")
        print_portfolio_status(mv_current, total_inv_current)
        
        # ------------------------------------------------
        # 階段二：兩天後投入 cash_usd_future
        # ------------------------------------------------
        print("\n▶ [ 階段二：兩天後進場 (10萬台幣入帳) ]")
        avail_cash_2 = rem_cash_1 + cash_usd_future
        print(f"  可用資金: ${avail_cash_2:,.2f}")
        
        # 再次計算理想目標與缺口 (基於買完第一波後的狀態)
        target_mvs_2 = {t: (total_inv_current + avail_cash_2) * pct for t, pct in targets.items()}
        shortfalls_2 = {t: target_mvs_2[t] - mv_current[t] for t, pct in targets.items()}
        
        best_target_2 = max(shortfalls_2, key=shortfalls_2.get)
        
        if shortfalls_2[best_target_2] > 0 and avail_cash_2 > 100:
            shares_2 = int((avail_cash_2 - 3) / prices[best_target_2])
            cost_2 = shares_2 * prices[best_target_2]
            rem_cash_2 = avail_cash_2 - cost_2 - 3
            
            # 更新狀態
            pos_current[best_target_2] += shares_2
            mv_current[best_target_2] += cost_2
            total_inv_current += cost_2
            
            print(f"  ✅ 買進 {best_target_2}: {shares_2} 股 (花費 ${cost_2:,.2f} + $3 手續費)")
            print(f"  最終剩餘現金: ${rem_cash_2:,.2f}")
        else:
            print("  資金過小或無需買進。")
            rem_cash_2 = avail_cash_2

        print("  [ 兩天後買完的【最終比例】 ]")
        for t in tickers:
            pct = mv_current[t] / total_inv_current * 100 if total_inv_current > 0 else 0
            target_pct = targets[t] * 100
            diff = pct - target_pct
            print(f"  {t}: ${mv_current[t]:,.2f} ({pct:.1f}%) | 目標: {target_pct}% | 偏差: {diff:+.1f}%")
            
    simulate_two_step_buy({'RSSB': 0.50, 'RSST': 0.20, 'RSSY': 0.15, 'RSIT': 0.15}, "50/20/15/15 原配置")
    simulate_two_step_buy({'RSSB': 0.40, 'RSST': 0.30, 'RSSY': 0.15, 'RSIT': 0.15}, "40/30/15/15 趨勢強化新配置")

if __name__ == '__main__':
    main()
