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
    print("[*] 正在下載底層真實資料 (包含國際股市 EFA)...")
    # EFA: iShares MSCI EAFE ETF (代表除北美外的國際已開發市場股票)
    tickers = ['SPY', 'EFA', 'AGG', 'AQMIX', 'HYG', '^IRX']
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
    
    # 修正 Proxy：精準區分美股(SPY)與國際股(EFA)
    # 假設全球股票 (VT) 大約是 60% 美股 + 40% 國際股
    synth_returns['RSSB_Proxy'] = (0.6 * returns['SPY'] + 0.4 * returns['EFA']) + returns['AGG'] - borrow_rate_daily
    synth_returns['RSST_Proxy'] = returns['SPY'] + returns['AQMIX'] - borrow_rate_daily 
    synth_returns['RSSY_Proxy'] = returns['SPY'] + returns['HYG'] - borrow_rate_daily
    # 【重大修正】RSIT 是國際股 (EFA) + 管理期貨 (AQMIX)
    synth_returns['RSIT_Proxy'] = returns['EFA'] + returns['AQMIX'] - borrow_rate_daily 
    
    synth_monthly = synth_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    
    # 原配置
    t_orig = np.array([0.50, 0.20, 0.15, 0.15])
    # 全新黃金比例配置
    t_new = np.array([0.40, 0.25, 0.15, 0.20])
    
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
        
        v_o = run_sim(sim_returns, t_orig, initial_cap, n_months)
        final_orig[i] = v_o[-1]
        mdd_orig[i] = np.min((v_o - np.maximum.accumulate(v_o)) / np.maximum.accumulate(v_o))
        
        v_n = run_sim(sim_returns, t_new, initial_cap, n_months)
        final_new[i] = v_n[-1]
        mdd_new[i] = np.min((v_n - np.maximum.accumulate(v_n)) / np.maximum.accumulate(v_n))

    print("\n" + "=" * 70)
    print("【 組合 X 光透視：底層資產真實曝險比例 】")
    print("=" * 70)
    print("        [ 原配置: 50/20/15/15 ]  |  [ 黃金配置: 40/25/15/20 ]")
    print("股票總計:         100%           |           100%")
    print(" ├ 美股 (SPY) :    65%           |            64%")
    print(" └ 國際股(EFA):    35%           |            36%  <-- 完美貼合全球市值(VT)比例！")
    print("----------------------------------------------------------------------")
    print("債券總計:          50%           |            40%  <-- 成功降低債券曝險")
    print("趨勢期貨:          35%           |            45%  <-- 大幅提升抗震避險能力")
    print("信貸收益:          15%           |            15%")
    print("總曝險  :         200%           |           200%")
    
    print("\n" + "=" * 70)
    print("【 蒙地卡羅壓力測試對比 (2000次重抽樣) 】")
    print("=" * 70)
    print(f"                       [ 原配置 ]          |  [ 黃金配置 ]")
    print(f"中位數總資產 (P50)   : {np.median(final_orig):18,.0f} | {np.median(final_new):18,.0f}")
    print(f"悲觀總資產 (P10)     : {np.percentile(final_orig, 10):18,.0f} | {np.percentile(final_new, 10):18,.0f}")
    print(f"中位數最大回撤 (MDD) : {np.median(mdd_orig)*100:17.2f}% | {np.median(mdd_new)*100:17.2f}%")
    print(f"極端股災90% MDD      : {np.percentile(mdd_orig, 10)*100:17.2f}% | {np.percentile(mdd_new, 10)*100:17.2f}%")
    print("-" * 70)

if __name__ == '__main__':
    main()
