import pandas as pd
import numpy as np
import yfinance as yf
import os

def run_portfolio_simulation(monthly_returns, targets, bounds_lower, bounds_upper, initial_cap, months_count):
    """給定一段月報酬序列，執行現金流與再平衡模擬"""
    portfolio_values = np.zeros(months_count + 1)
    portfolio_values[0] = initial_cap
    asset_values = initial_cap * targets
    rebalances = 0
    
    for m in range(months_count):
        # 1. 增長
        asset_values = asset_values * (1 + monthly_returns[m])
        # 2. 現金流
        cf = 10000 if m < 60 else 30000
        # 3. 路由到最落後的資產
        current_total = np.sum(asset_values)
        current_weights = asset_values / current_total
        lowest_idx = np.argmin(current_weights - targets)
        asset_values[lowest_idx] += cf
        # 4. 檢查再平衡
        current_total = np.sum(asset_values)
        current_weights = asset_values / current_total
        if np.any(current_weights < bounds_lower) or np.any(current_weights > bounds_upper):
            asset_values = current_total * targets
            rebalances += 1
            
        portfolio_values[m+1] = np.sum(asset_values)
        
    return portfolio_values, rebalances

def main():
    print("[*] 正在從 Yahoo Finance 下載 20 年底層歷史資料 (2005-2024)...")
    tickers = ['SPY', 'AGG', 'GLD', 'QQQ', 'LQD', '^IRX']
    
    data_dict = {}
    for ticker in tickers:
        df = yf.download(ticker, start='2005-01-01', end='2024-12-31')
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if 'Adj Close' in df.columns:
                data_dict[ticker] = df['Adj Close']
            else:
                data_dict[ticker] = df['Close']
    data = pd.DataFrame(data_dict)
    
    # 處理借貸成本 (美國 13 週國庫券殖利率，轉換為每日)
    borrow_rate_annual = data['^IRX'] / 100
    borrow_rate_annual = borrow_rate_annual.ffill().fillna(0.04)
    borrow_rate_daily = borrow_rate_annual / 252
    
    returns = data.pct_change().dropna()
    
    # 建立合成 Proxy 標的
    print("[*] 正在建立 Return Stacked 策略合成 Proxy...")
    synth_returns = pd.DataFrame(index=returns.index)
    synth_returns['RSSB_Proxy'] = returns['SPY'] + returns['AGG'] - borrow_rate_daily
    synth_returns['RSST_Proxy'] = returns['SPY'] + returns['GLD'] - borrow_rate_daily # 以 GLD 取代 Managed Futures 作為零相關替代品
    synth_returns['RSSY_Proxy'] = returns['SPY'] + returns['LQD'] - borrow_rate_daily # LQD (投資級企債) 取代 Yield
    synth_returns['RSIT_Proxy'] = returns['QQQ'] + returns['AGG'] - borrow_rate_daily # QQQ (科技) + AGG
    
    # 將日報酬轉換為月報酬
    synth_monthly = synth_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    
    targets = np.array([0.50, 0.20, 0.15, 0.15])
    bounds_lower = targets * 0.8
    bounds_upper = targets * 1.2
    initial_cap = 1300000
    
    print("-" * 60)
    print("【 測試一：真實歷史重播 (2005-2024，包含2008海嘯與2022雙殺) 】")
    # 將實際的歷史月報酬丟進去跑
    hist_months = len(synth_monthly)
    hist_vals, hist_rebal = run_portfolio_simulation(
        synth_monthly.values, targets, bounds_lower, bounds_upper, initial_cap, hist_months
    )
    
    hist_max = np.maximum.accumulate(hist_vals)
    hist_drawdowns = (hist_vals - hist_max) / hist_max
    
    # 找出最大回撤發生的時間點
    mdd_val = np.min(hist_drawdowns)
    
    print(f"2005年 初始本金: {initial_cap:,.0f} 元")
    print(f"2024年底 總資產: {hist_vals[-1]:,.0f} 元")
    print(f"歷史最大回撤 (MDD): {mdd_val*100:.2f}% (這是在真實歷史的股災中會遭遇的帳面蒸發)")
    print(f"期間強制再平衡次數: {hist_rebal} 次")
    print("-" * 60)
    
    print("【 測試二：歷史重抽樣 蒙地卡羅 (Bootstrapping, 5000次) 】")
    print("邏輯：從這 20 年的歷史月報酬中，隨機『抽出』240 個月來組成未來。")
    print("這能完美保留了股災時『多種資產一起崩盤』的肥尾風險，不依賴常態分佈公式。")
    
    n_sims = 5000
    n_months = 240
    final_values = np.zeros(n_sims)
    max_drawdowns = np.zeros(n_sims)
    
    np.random.seed(42)
    # 將 dataframe 轉換為 numpy array 加速抽樣
    monthly_pool = synth_monthly.values 
    
    for i in range(n_sims):
        # 隨機抽取 240 個月 (可重複抽出)
        random_indices = np.random.randint(0, len(monthly_pool), size=n_months)
        sim_returns = monthly_pool[random_indices]
        
        vals, _ = run_portfolio_simulation(
            sim_returns, targets, bounds_lower, bounds_upper, initial_cap, n_months
        )
        
        final_values[i] = vals[-1]
        roll_max = np.maximum.accumulate(vals)
        dd = (vals - roll_max) / roll_max
        max_drawdowns[i] = np.min(dd)

    p10_val = np.percentile(final_values, 10)
    p50_val = np.median(final_values)
    p90_val = np.percentile(final_values, 90)
    
    p90_mdd = np.percentile(max_drawdowns, 10) # MDD is negative, so 10th percentile is the worst 10%
    p50_mdd = np.median(max_drawdowns)
    
    print(f"[ 20年後總資產 (抽樣推演) ]")
    print(f"中位數 (P50): {p50_val:,.0f} 元")
    print(f"極差運氣 (P10): {p10_val:,.0f} 元")
    print(f"極佳運氣 (P90): {p90_val:,.0f} 元")
    print(f"[ 回撤風險 ]")
    print(f"中位數 MDD: {p50_mdd*100:.2f}%")
    print(f"極端崩盤 (最慘10%的路徑) MDD: {p90_mdd*100:.2f}%")
    
    # 將報告匯出
    current_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(current_dir, "..", "reports", "stress_tests")
    os.makedirs(reports_dir, exist_ok=True)
    report_path = os.path.join(reports_dir, "historical_proxy_stress_test.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 底層資產合成與歷史壓力測試報告 (Proxy Bootstrapping)\n\n")
        f.write("此報告解決了「RS系列 ETF 歷史太短，充滿牛市偏誤」的問題。\n")
        f.write("我們使用 20 年 (2005~2024) 的歷史底層資產，合成出等效的策略，並進行兩種維度的壓力測試。\n\n")
        
        f.write("## 1. 代理資產 (Proxy) 邏輯\n")
        f.write("- **借貸成本**: `^IRX` (美國 13 週國庫券殖利率)\n")
        f.write("- **RSSB Proxy**: `SPY + AGG - 借貸成本`\n")
        f.write("- **RSST Proxy**: `SPY + GLD - 借貸成本` (以黃金取代未上市的趨勢基金)\n")
        f.write("- **RSSY Proxy**: `SPY + LQD - 借貸成本` (投資級企債取代收益)\n")
        f.write("- **RSIT Proxy**: `QQQ + AGG - 借貸成本`\n\n")
        
        f.write("## 2. 真實歷史重播 (2005-2024)\n")
        f.write("完全套用這 20 年的真實月報酬，包含 2008 年金融海嘯與 2022 年股債雙殺。\n")
        f.write(f"- 歷史最大回撤 (MDD): **{mdd_val*100:.2f}%**\n")
        f.write(f"- 2024 年底總資產: **{hist_vals[-1]:,.0f} 元**\n")
        f.write(f"- 期間強制再平衡次數: **{hist_rebal} 次**\n\n")
        
        f.write("## 3. 歷史重抽樣蒙地卡羅 (Bootstrapping, 5000 次)\n")
        f.write("不依賴常態分佈公式，直接從這 240 個月的歷史中隨機抽取組合，保留了「股債齊跌」的真實肥尾風險。\n")
        f.write("### 預估資產 (20年後)\n")
        f.write(f"- 中位數 (P50): **{p50_val:,.0f} 元**\n")
        f.write(f"- 極差運氣 (P10): **{p10_val:,.0f} 元**\n")
        f.write(f"- 極佳運氣 (P90): **{p90_val:,.0f} 元**\n\n")
        f.write("### 預期最大回撤\n")
        f.write(f"- 中位數 MDD: **{p50_mdd*100:.2f}%**\n")
        f.write(f"- 極端崩盤 90% MDD: **{p90_mdd*100:.2f}%**\n")

if __name__ == '__main__':
    main()
