import pandas as pd
import numpy as np
import yfinance as yf
import os

def run_sim(monthly_returns, targets, initial_cap, months_count):
    portfolio_values = np.zeros(months_count + 1)
    portfolio_values[0] = initial_cap
    asset_values = initial_cap * targets
    bounds_lower = targets * 0.8
    bounds_upper = targets * 1.2
    
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
        portfolio_values[m+1] = np.sum(asset_values)
    return portfolio_values

def main():
    print("[*] 拋棄拖後腿的國際股市，重新下載 QQQ 與底層真實資料...")
    tickers = ['SPY', 'EFA', 'AGG', 'AQMIX', 'QQQ', 'HYG', '^IRX']
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
    
    borrow_rate_daily = (data['^IRX'] / 100).ffill().fillna(0.04) / 252
    returns = data.pct_change().dropna()
    
    synth_returns = pd.DataFrame(index=returns.index)
    
    # 建立比較基準
    synth_returns['RSSB_Proxy_Int'] = (0.6 * returns['SPY'] + 0.4 * returns['EFA']) + returns['AGG'] - borrow_rate_daily
    synth_returns['RSSB_Proxy_US'] = returns['SPY'] + returns['AGG'] - borrow_rate_daily
    
    synth_returns['RSST_Proxy'] = returns['SPY'] + returns['AQMIX'] - borrow_rate_daily 
    synth_returns['RSSY_Proxy'] = returns['SPY'] + returns['HYG'] - borrow_rate_daily
    
    # 拖後腿的 RSIT (國際股 + 期貨)
    synth_returns['RSIT_Proxy'] = returns['EFA'] + returns['AQMIX'] - borrow_rate_daily 
    # 正確的暴力科技疊加 RSND (QQQ + 期貨)
    synth_returns['RSND_Proxy'] = returns['QQQ'] + returns['AQMIX'] - borrow_rate_daily 
    
    synth_monthly = synth_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    
    # 【配置一：被國際股市拖累的平衡版】 (上一版的 3500萬)
    # [40% RSSB(含國際), 25% RSST, 15% RSSY, 20% RSIT]
    targets_int = np.array([0.40, 0.25, 0.15, 0.20])
    
    # 【配置二：Linus 式火力全開科技版】 (使用者真正要的)
    # [40% RSSB(純美股), 30% RSST, 15% RSSY, 15% RSND]
    targets_tech = np.array([0.40, 0.30, 0.15, 0.15])
    
    initial_cap = 1300000
    n_sims = 3000
    n_months = 240
    
    final_int, mdd_int = np.zeros(n_sims), np.zeros(n_sims)
    final_tech, mdd_tech = np.zeros(n_sims), np.zeros(n_sims)
    
    np.random.seed(42)
    monthly_pool = synth_monthly.values 
    
    for i in range(n_sims):
        random_indices = np.random.randint(0, len(monthly_pool), size=n_months)
        
        # 準備資料 A: 包含 EFA 和 RSIT
        sim_returns_int = monthly_pool[random_indices][:, [0, 2, 3, 4]]
        # 準備資料 B: 拋棄 EFA，採用純美股 RSSB 與 RSND (科技+期貨)
        sim_returns_tech = monthly_pool[random_indices][:, [1, 2, 3, 5]]
        
        v_int = run_sim(sim_returns_int, targets_int, initial_cap, n_months)
        final_int[i] = v_int[-1]
        mdd_int[i] = np.min((v_int - np.maximum.accumulate(v_int)) / np.maximum.accumulate(v_int))
        
        v_tech = run_sim(sim_returns_tech, targets_tech, initial_cap, n_months)
        final_tech[i] = v_tech[-1]
        mdd_tech[i] = np.min((v_tech - np.maximum.accumulate(v_tech)) / np.maximum.accumulate(v_tech))

    print("\n" + "=" * 70)
    print("【 歷史重算：國際平衡的代價 vs 火力全開科技版 (RSND) 】")
    print("=" * 70)
    print(f"                       [ 國際拖累版 (RSIT) ] | [ 科技火力版 (RSND) ]")
    print(f"中位數總資產 (P50)   : {np.median(final_int):21,.0f} | {np.median(final_tech):21,.0f}")
    print(f"悲觀總資產 (P10)     : {np.percentile(final_int, 10):21,.0f} | {np.percentile(final_tech, 10):21,.0f}")
    print(f"中位數最大回撤 (MDD) : {np.median(mdd_int)*100:20.2f}% | {np.median(mdd_tech)*100:20.2f}%")
    print(f"極端股災90% MDD      : {np.percentile(mdd_int, 10)*100:20.2f}% | {np.percentile(mdd_tech, 10)*100:20.2f}%")
    print("-" * 70)

if __name__ == '__main__':
    main()
