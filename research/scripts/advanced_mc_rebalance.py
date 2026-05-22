import pandas as pd
import numpy as np
import os
import glob

def load_data(data_dir):
    csv_files = glob.glob(os.path.join(data_dir, "*_history.csv"))
    df_list = []
    for file in csv_files:
        ticker = os.path.basename(file).replace("_history.csv", "")
        if ticker in ['SPY', 'SSO', 'RSIT', 'GLDM']: 
            continue
        try:
            df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
            s = df['Adj Close'] if 'Adj Close' in df.columns else df['Close']
            s.name = ticker
            df_list.append(s)
        except Exception as e:
            pass
    if df_list:
        return pd.concat(df_list, axis=1).dropna()
    return pd.DataFrame()

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    df = load_data(data_dir)
    
    # 取得日報酬
    returns_daily = df.pct_change().dropna()
    
    # RSIT 無足夠歷史資料，我們使用邏輯最接近的 RSST 作為 Proxy 確保共變異數矩陣完整
    returns_daily['RSIT'] = returns_daily['RSST']
    
    tickers = ['RSSB', 'RSST', 'RSSY', 'RSIT']
    returns_daily = returns_daily[tickers]
    
    # 將日資料轉換為月度期望值與共變異數矩陣 (假設每月 21 個交易日)
    mean_monthly = returns_daily.mean().values * 21
    cov_monthly = returns_daily.cov().values * 21
    
    # 策略參數
    targets = np.array([0.50, 0.20, 0.15, 0.15])
    # 容忍區間 (相對目標 +- 20%)
    bounds_lower = targets * 0.8
    bounds_upper = targets * 1.2
    
    n_sims = 5000
    n_months = 240 # 20 年
    initial_cap = 1300000
    
    # 追蹤指標
    final_values = np.zeros(n_sims)
    max_drawdowns = np.zeros(n_sims)
    annual_vols = np.zeros(n_sims)
    rebalance_counts = np.zeros(n_sims)
    
    np.random.seed(42) # 固定隨機種子
    
    for i in range(n_sims):
        # 利用歷史共變異數矩陣，產生 240 個月的連動隨機報酬率 (240 x 4)
        sim_returns = np.random.multivariate_normal(mean_monthly, cov_monthly, n_months)
        
        portfolio_values = np.zeros(n_months + 1)
        portfolio_values[0] = initial_cap
        
        # 初始資產分配
        asset_values = initial_cap * targets
        rebalances = 0
        
        for m in range(n_months):
            # 1. 資產依當月隨機報酬增長
            asset_values = asset_values * (1 + sim_returns[m])
            
            # 2. 決定現金流
            cf = 10000 if m < 60 else 30000
            
            # 3. 現金流路由 (買入最落後的資產)
            current_total = np.sum(asset_values)
            current_weights = asset_values / current_total
            weight_diff = current_weights - targets
            lowest_idx = np.argmin(weight_diff)
            asset_values[lowest_idx] += cf
            
            # 4. 閾值再平衡檢查 (Threshold Rebalancing)
            current_total = np.sum(asset_values)
            current_weights = asset_values / current_total
            
            if np.any(current_weights < bounds_lower) or np.any(current_weights > bounds_upper):
                # 觸發強制再平衡，重置回目標比例
                asset_values = current_total * targets
                rebalances += 1
            
            portfolio_values[m+1] = np.sum(asset_values)
            
        final_values[i] = portfolio_values[-1]
        
        # 結算該次模擬的路徑依賴數據
        roll_max = np.maximum.accumulate(portfolio_values)
        drawdowns = (portfolio_values - roll_max) / roll_max
        max_drawdowns[i] = np.min(drawdowns)
        
        monthly_pct = np.diff(portfolio_values) / portfolio_values[:-1]
        annual_vols[i] = np.std(monthly_pct) * np.sqrt(12)
        rebalance_counts[i] = rebalances
        
    print("-" * 60)
    print("【 基於歷史共變異矩陣與動態再平衡之蒙地卡羅 (5000次) 】")
    print("-" * 60)
    print(f"[ 20年後總資產預估 ]")
    print(f"中位數 (P50)       : {np.median(final_values):,.0f} 元")
    print(f"極差運氣 (P10)     : {np.percentile(final_values, 10):,.0f} 元")
    print(f"極佳運氣 (P90)     : {np.percentile(final_values, 90):,.0f} 元")
    print("")
    print(f"[ 路徑風險指標 ]")
    print(f"中位數 最大回撤(MDD): {np.median(max_drawdowns)*100:.2f}%")
    print(f"最慘狀況 90% MDD   : {np.percentile(max_drawdowns, 10)*100:.2f}% (十次裡有一次會跌這麼深)")
    print(f"平均年化波動率     : {np.mean(annual_vols)*100:.2f}%")
    print(f"20年平均再平衡次數 : {np.mean(rebalance_counts):.1f} 次")
    print("-" * 60)

if __name__ == '__main__':
    main()
