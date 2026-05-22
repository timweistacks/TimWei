import pandas as pd
import numpy as np
import yfinance as yf

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
    
    borrow_rate_daily = (data['^IRX'] / 100).ffill().fillna(0.04) / 252
    returns = data.pct_change().dropna()
    
    synth_returns = pd.DataFrame(index=returns.index)
    synth_returns['RSSB_Proxy'] = returns['SPY'] + returns['AGG'] - borrow_rate_daily
    synth_returns['RSST_Proxy'] = returns['SPY'] + returns['AQMIX'] - borrow_rate_daily 
    synth_returns['RSSY_Proxy'] = returns['SPY'] + returns['HYG'] - borrow_rate_daily
    synth_returns['RSIT_Proxy'] = returns['QQQ'] + returns['AGG'] - borrow_rate_daily 
    
    synth_monthly = synth_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    
    # 原始配置
    targets_orig = np.array([0.50, 0.20, 0.15, 0.15])
    # 提案配置：降低債券，提升趨勢
    targets_new = np.array([0.40, 0.30, 0.15, 0.15])
    
    initial_cap = 1300000
    n_sims = 2000
    n_months = 240
    
    final_orig, mdd_orig = np.zeros(n_sims), np.zeros(n_sims)
    final_new, mdd_new = np.zeros(n_sims), np.zeros(n_sims)
    
    np.random.seed(42)
    monthly_pool = synth_monthly.values 
    
    for i in range(n_sims):
        random_indices = np.random.randint(0, len(monthly_pool), size=n_months)
        sim_returns = monthly_pool[random_indices]
        
        v_o = run_sim(sim_returns, targets_orig, initial_cap, n_months)
        final_orig[i] = v_o[-1]
        mdd_orig[i] = np.min((v_o - np.maximum.accumulate(v_o)) / np.maximum.accumulate(v_o))
        
        v_n = run_sim(sim_returns, targets_new, initial_cap, n_months)
        final_new[i] = v_n[-1]
        mdd_new[i] = np.min((v_n - np.maximum.accumulate(v_n)) / np.maximum.accumulate(v_n))

    print("=" * 60)
    print("【 概念驗證：降低債券曝險，提升趨勢避險 】")
    print("=" * 60)
    print(f"                       [ 原配置: 50/20/15/15 ] | [ 新配置: 40/30/15/15 ]")
    print(f"中位數總資產 (P50)   : {np.median(final_orig):21,.0f} | {np.median(final_new):21,.0f}")
    print(f"悲觀總資產 (P10)     : {np.percentile(final_orig, 10):21,.0f} | {np.percentile(final_new, 10):21,.0f}")
    print(f"中位數最大回撤 (MDD) : {np.median(mdd_orig)*100:20.2f}% | {np.median(mdd_new)*100:20.2f}%")
    print(f"極端股災90% MDD      : {np.percentile(mdd_orig, 10)*100:20.2f}% | {np.percentile(mdd_new, 10)*100:20.2f}%")
    print("-" * 60)

if __name__ == '__main__':
    main()
