import json
import os
import yfinance as yf
import pandas as pd

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    portfolio_path = os.path.join(current_dir, "..", "..", "data", "personal_ledger", "portfolio.json")
    
    with open(portfolio_path, 'r', encoding='utf-8') as f:
        portfolio = json.load(f)
        
    cash_usd = portfolio.get('cash_usd', 0)
    usd_twd_rate = portfolio['valuation'].get('usd_twd_rate', 32.0)
    
    # 從 Yahoo抓最新匯率
    try:
        usdtwd_data = yf.download("USDTWD=X", period="1d")
        if not usdtwd_data.empty:
            if isinstance(usdtwd_data.columns, pd.MultiIndex):
                usd_twd_rate = usdtwd_data['Close'].iloc[-1].values[0]
            else:
                usd_twd_rate = usdtwd_data['Close'].iloc[-1]
    except:
        pass

    print(f"[*] 目前匯率設定: {usd_twd_rate:.2f} TWD/USD")
    print(f"[*] 目前帳戶美元現金: ${cash_usd:.2f} (約 {cash_usd * usd_twd_rate:,.0f} TWD)")
    
    tickers = ['RSSB', 'RSST', 'RSSY', 'RSIT']
    positions = {p['symbol']: p['units'] for p in portfolio['positions'] if p['symbol'] in tickers}
    
    # 抓最新股價
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

    # 計算現值
    mv = {t: positions.get(t, 0) * prices.get(t, 0) for t in tickers}
    total_invested_usd = sum(mv.values())
    total_assets_usd = total_invested_usd + cash_usd
    
    print("\n【 目前真實持倉比例 (不含現金) 】")
    for t in tickers:
        pct = mv[t] / total_invested_usd if total_invested_usd > 0 else 0
        print(f"{t}: ${mv[t]:,.2f} ({pct*100:.1f}%) | 股數: {positions.get(t, 0)} | 單價: ${prices[t]:.2f}")
        
    # 計算準備投入的錢
    future_twd = 100000
    future_usd = future_twd / usd_twd_rate
    total_deployable_usd = cash_usd + future_usd
    
    new_total_invested_usd = total_invested_usd + total_deployable_usd
    print(f"\n[*] 準備動用資金: 帳上餘額 ${cash_usd:.2f} + 預計存入 ${future_usd:,.2f} (10萬台幣)")
    print(f"[*] 本次總可動用資金: ${total_deployable_usd:,.2f} (約 {total_deployable_usd * usd_twd_rate:,.0f} TWD)")
    print(f"[*] 預計打滿後總資產: ${new_total_invested_usd:,.2f}")
    
    # 目標比例
    target_orig = {'RSSB': 0.50, 'RSST': 0.20, 'RSSY': 0.15, 'RSIT': 0.15}
    target_new = {'RSSB': 0.40, 'RSST': 0.30, 'RSSY': 0.15, 'RSIT': 0.15}
    
    def calculate_buy(targets, title):
        print(f"\n==================================================")
        print(f" 方案：往 {title} 目標靠攏")
        print(f"==================================================")
        target_mvs = {t: new_total_invested_usd * pct for t, pct in targets.items()}
        shortfalls = {t: target_mvs[t] - mv[t] for t in tickers}
        
        # 過濾出需要買的 (只買不賣)
        to_buy = {t: amt for t, amt in shortfalls.items() if amt > 0}
        
        # 考慮單次 3 美元手續費，資金太小切碎不划算。
        # 總共約 $4300 USD 可買，如果某標的缺口小於 $500，直接無視，集中買最缺的。
        sorted_buy = sorted(to_buy.items(), key=lambda item: item[1], reverse=True)
        
        # 簡單邏輯：把錢按缺口比例分配給前一或前兩大缺口的資產
        remaining_cash = total_deployable_usd
        buy_plan = {}
        
        for t, amt in sorted_buy:
            if remaining_cash <= 0: break
            
            # 分配金額，考慮如果金額太小就不浪費 3 塊手續費了 (最低門檻設 1000 美元)
            if amt > remaining_cash:
                allocate = remaining_cash
            else:
                allocate = amt
                
            # 如果剩下的錢太少，不如全部倒給當前這個標的，免得多付一次手續費
            if remaining_cash - allocate < 1000:
                allocate = remaining_cash
                
            shares = int(allocate / prices[t])
            if shares > 0:
                buy_plan[t] = shares
                remaining_cash -= (shares * prices[t])
                
        # 印出建議
        fee_count = len(buy_plan)
        total_fee = fee_count * 3
        
        print("【 理想目標缺口 】")
        for t in tickers:
            print(f"{t}: 目標 ${target_mvs[t]:,.0f} | 差距: {'落後' if shortfalls[t]>0 else '超標'} ${abs(shortfalls[t]):,.0f}")
            
        print("\n【 實戰買進建議 (含手續費考量) 】")
        if not buy_plan:
            print("目前配置不需要買進，或資金過小。")
        else:
            for t, shares in buy_plan.items():
                cost = shares * prices[t]
                print(f"✅ 買進 {t}: {shares} 股 (約花費 ${cost:,.2f})")
            print(f"💸 預估手續費: ${total_fee} (進場 {fee_count} 次)")
            print(f"💰 買完後剩餘零錢: ${remaining_cash:,.2f}")
            
    calculate_buy(target_orig, "[ 50/20/15/15 原配置 ]")
    calculate_buy(target_new, "[ 40/30/15/15 趨勢強化新配置 ]")

if __name__ == '__main__':
    main()
