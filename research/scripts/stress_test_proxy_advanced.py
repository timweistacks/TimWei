import pandas as pd
import numpy as np
import yfinance as yf
import os

def run_portfolio_simulation(monthly_returns, targets, bounds_lower, bounds_upper, initial_cap, months_count):
    portfolio_values = np.zeros(months_count + 1)
    portfolio_values[0] = initial_cap
    asset_values = initial_cap * targets
    rebalances = 0
    
    for m in range(months_count):
        asset_values = asset_values * (1 + monthly_returns[m])
        cf = 10000 if m < 60 else 30000
        
        current_total = np.sum(asset_values)
        current_weights = asset_values / current_total
        lowest_idx = np.argmin(current_weights - targets)
        asset_values[lowest_idx] += cf
        
        current_total = np.sum(asset_values)
        current_weights = asset_values / current_total
        if np.any(current_weights < bounds_lower) or np.any(current_weights > bounds_upper):
            asset_values = current_total * targets
            rebalances += 1
            
        portfolio_values[m+1] = np.sum(asset_values)
        
    return portfolio_values, rebalances

def main():
    print("[*] 正在從 Yahoo Finance 下載更精確的 Proxy 底層歷史資料 (2010-2024)...")
    # AQMIX (AQR Managed Futures Strategy Fund) 成立於 2010 年，是量化界最標準的管理期貨 Proxy
    # HYG (High Yield Bond) 用來粗略替代 RSSY 的 Yield (因為純 Carry 基金的歷史資料極難免費取得)
    tickers = ['SPY', 'AGG', 'AQMIX', 'QQQ', 'HYG', '^IRX']
    
    data_dict = {}
    for ticker in tickers:
        df = yf.download(ticker, start='2010-01-01', end='2024-12-31')
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if 'Adj Close' in df.columns:
                data_dict[ticker] = df['Adj Close']
            else:
                data_dict[ticker] = df['Close']
    data = pd.DataFrame(data_dict)
    
    borrow_rate_annual = data['^IRX'] / 100
    borrow_rate_annual = borrow_rate_annual.ffill().fillna(0.04)
    borrow_rate_daily = borrow_rate_annual / 252
    
    returns = data.pct_change().dropna()
    
    print("[*] 正在建立 Return Stacked 策略合成 Proxy (導入真實管理期貨)...")
    synth_returns = pd.DataFrame(index=returns.index)
    # RSSB 債券部位：AGG 是綜合債券(含長短天期與企債)，平均存續期約 6-7 年，符合中長期債券混合
    synth_returns['RSSB_Proxy'] = returns['SPY'] + returns['AGG'] - borrow_rate_daily
    # RSST: 使用 AQR 真實的管理期貨基金 (AQMIX) 作為 Proxy
    synth_returns['RSST_Proxy'] = returns['SPY'] + returns['AQMIX'] - borrow_rate_daily 
    # RSSY: 使用高收益債 (HYG) 模擬收取高息(Yield)的特性
    synth_returns['RSSY_Proxy'] = returns['SPY'] + returns['HYG'] - borrow_rate_daily
    # RSIT: 科技股 + AGG
    synth_returns['RSIT_Proxy'] = returns['QQQ'] + returns['AGG'] - borrow_rate_daily 
    
    synth_monthly = synth_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    
    targets = np.array([0.50, 0.20, 0.15, 0.15])
    bounds_lower = targets * 0.8
    bounds_upper = targets * 1.2
    initial_cap = 1300000
    
    print("-" * 60)
    print("【 測試一：真實歷史重播 (2010-2024，包含2020疫情與2022雙殺) 】")
    hist_months = len(synth_monthly)
    hist_vals, hist_rebal = run_portfolio_simulation(
        synth_monthly.values, targets, bounds_lower, bounds_upper, initial_cap, hist_months
    )
    
    hist_max = np.maximum.accumulate(hist_vals)
    hist_drawdowns = (hist_vals - hist_max) / hist_max
    mdd_val = np.min(hist_drawdowns)
    
    print(f"2010年 初始本金: {initial_cap:,.0f} 元")
    print(f"2024年底 總資產: {hist_vals[-1]:,.0f} 元")
    print(f"歷史最大回撤 (MDD): {mdd_val*100:.2f}%")
    print("-" * 60)
    
    print("【 測試二：歷史重抽樣 蒙地卡羅 (Bootstrapping, 5000次) 】")
    n_sims = 5000
    n_months = 240
    final_values = np.zeros(n_sims)
    max_drawdowns = np.zeros(n_sims)
    
    np.random.seed(42)
    monthly_pool = synth_monthly.values 
    
    for i in range(n_sims):
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
    
    p90_mdd = np.percentile(max_drawdowns, 10)
    p50_mdd = np.median(max_drawdowns)
    
    print(f"[ 20年後總資產 (抽樣推演) ]")
    print(f"中位數 (P50): {p50_val:,.0f} 元")
    print(f"極差運氣 (P10): {p10_val:,.0f} 元")
    print(f"極佳運氣 (P90): {p90_val:,.0f} 元")
    print(f"[ 回撤風險 ]")
    print(f"中位數 MDD: {p50_mdd*100:.2f}%")
    print(f"極端崩盤 90% MDD: {p90_mdd*100:.2f}%")

if __name__ == '__main__':
    main()
