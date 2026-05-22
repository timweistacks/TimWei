import pandas as pd
import numpy as np
import yfinance as yf
import os

def run_simulation(monthly_returns, targets, threshold, initial_cap, months_count):
    portfolio_values = np.zeros(months_count + 1)
    portfolio_values[0] = initial_cap
    asset_values = initial_cap * targets
    
    bounds_lower = targets * (1 - threshold)
    bounds_upper = targets * (1 + threshold)
    
    rebalances = 0
    
    for m in range(months_count):
        asset_values = asset_values * (1 + monthly_returns[m])
        cf = 10000 if m < 60 else 30000
        
        if cf > 0:
            current_total = np.sum(asset_values)
            current_weights = asset_values / current_total
            lowest_idx = np.argmin(current_weights - targets)
            asset_values[lowest_idx] += cf
        
        current_total_after_cf = np.sum(asset_values)
        current_weights_after_cf = asset_values / current_total_after_cf
        if np.any(current_weights_after_cf < bounds_lower) or np.any(current_weights_after_cf > bounds_upper):
            asset_values = current_total_after_cf * targets
            rebalances += 1
            
        portfolio_values[m+1] = np.sum(asset_values)
        
    return portfolio_values, rebalances

def main():
    print("[*] 正在獲取 2010-2024 真實歷史資料...")
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
    synth_returns = pd.DataFrame(index=returns.index)
    synth_returns['RSSB_Proxy'] = returns['SPY'] + returns['AGG'] - borrow_rate_daily
    synth_returns['RSST_Proxy'] = returns['SPY'] + returns['AQMIX'] - borrow_rate_daily 
    synth_returns['RSSY_Proxy'] = returns['SPY'] + returns['HYG'] - borrow_rate_daily
    synth_returns['RSIT_Proxy'] = returns['QQQ'] + returns['AGG'] - borrow_rate_daily 
    
    synth_monthly = synth_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    
    targets = np.array([0.50, 0.20, 0.15, 0.15])
    initial_cap = 1300000
    n_sims = 3000
    n_months = 240
    
    final_20 = np.zeros(n_sims)
    rebal_20 = np.zeros(n_sims)
    mdd_20 = np.zeros(n_sims)
    
    final_10 = np.zeros(n_sims)
    rebal_10 = np.zeros(n_sims)
    mdd_10 = np.zeros(n_sims)
    
    np.random.seed(42)
    monthly_pool = synth_monthly.values 
    
    print("[*] 正在執行 3000 次蒙地卡羅，對比 10% 與 20% 再平衡閾值...")
    
    for i in range(n_sims):
        random_indices = np.random.randint(0, len(monthly_pool), size=n_months)
        sim_returns = monthly_pool[random_indices]
        
        # 測試 20% 容忍度
        vals20, reb20 = run_simulation(sim_returns, targets, 0.20, initial_cap, n_months)
        final_20[i] = vals20[-1]
        rebal_20[i] = reb20
        mdd_20[i] = np.min((vals20 - np.maximum.accumulate(vals20)) / np.maximum.accumulate(vals20))
        
        # 測試 10% 容忍度
        vals10, reb10 = run_simulation(sim_returns, targets, 0.10, initial_cap, n_months)
        final_10[i] = vals10[-1]
        rebal_10[i] = reb10
        mdd_10[i] = np.min((vals10 - np.maximum.accumulate(vals10)) / np.maximum.accumulate(vals10))

    print("=" * 60)
    print("【 再平衡閾值對比： $\pm$ 20% vs $\pm$ 10% 】")
    print("=" * 60)
    print(f"                       [ $\pm$ 20% 寬鬆區間 ] | [ $\pm$ 10% 嚴格區間 ]")
    print(f"中位數總資產 (P50)   : {np.median(final_20):18,.0f} | {np.median(final_10):18,.0f}")
    print(f"悲觀總資產 (P10)     : {np.percentile(final_20, 10):18,.0f} | {np.percentile(final_10, 10):18,.0f}")
    print(f"樂觀總資產 (P90)     : {np.percentile(final_20, 90):18,.0f} | {np.percentile(final_10, 90):18,.0f}")
    print(f"中位數最大回撤 (MDD) : {np.median(mdd_20)*100:17.2f}% | {np.median(mdd_10)*100:17.2f}%")
    print(f"20 年平均強制買賣次數: {np.mean(rebal_20):18.1f} | {np.mean(rebal_10):18.1f}")
    print("-" * 60)

if __name__ == '__main__':
    main()
