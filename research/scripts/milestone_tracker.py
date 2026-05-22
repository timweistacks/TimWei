import pandas as pd
import numpy as np
import yfinance as yf
import os

def run_portfolio_simulation(monthly_returns, targets, bounds_lower, bounds_upper, initial_cap, months_count):
    portfolio_values = np.zeros(months_count + 1)
    portfolio_values[0] = initial_cap
    asset_values = initial_cap * targets
    
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
    bounds_lower = targets * 0.8
    bounds_upper = targets * 1.2
    initial_cap = 1300000
    
    n_sims = 5000
    n_months = 240
    
    # 建立矩陣來儲存所有模擬在特定時間點的價值
    # milestones: 0(起始), 60(5年), 120(10年), 180(15年), 240(20年)
    milestone_months = [60, 120, 180, 240]
    milestones_data = {m: np.zeros(n_sims) for m in milestone_months}
    
    np.random.seed(42)
    monthly_pool = synth_monthly.values 
    
    for i in range(n_sims):
        random_indices = np.random.randint(0, len(monthly_pool), size=n_months)
        sim_returns = monthly_pool[random_indices]
        
        vals = run_portfolio_simulation(sim_returns, targets, bounds_lower, bounds_upper, initial_cap, n_months)
        
        for m in milestone_months:
            milestones_data[m][i] = vals[m]

    print("=" * 60)
    print("【 未來 20 年財富航線圖 (Milestone Tracker) 】")
    print("=" * 60)
    
    years = [5, 10, 15, 20]
    for idx, m in enumerate(milestone_months):
        p10 = np.percentile(milestones_data[m], 10)
        p50 = np.median(milestones_data[m])
        p90 = np.percentile(milestones_data[m], 90)
        
        print(f"📍 第 {years[idx]} 年 (第 {m} 個月):")
        print(f"   [P10 底線區]: {p10:,.0f} 元")
        print(f"   [P50 中位數]: {p50:,.0f} 元")
        print(f"   [P90 樂觀區]: {p90:,.0f} 元")
        print("-" * 40)
        
if __name__ == '__main__':
    main()
