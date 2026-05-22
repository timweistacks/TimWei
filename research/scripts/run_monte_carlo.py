import pandas as pd
import numpy as np
import os
import glob

def load_data(data_dir):
    csv_files = glob.glob(os.path.join(data_dir, "*_history.csv"))
    df_list = []
    for file in csv_files:
        ticker = os.path.basename(file).replace("_history.csv", "")
        # 只取我們需要的 RS 系列來算共變異數
        if ticker in ['SPY', 'SSO', 'RSIT', 'GLDM']: 
            continue
        try:
            df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
            s = df['Adj Close'] if 'Adj Close' in df.columns else df['Close']
            s.name = ticker
            df_list.append(s)
        except Exception as e:
            pass
    return pd.concat(df_list, axis=1).dropna()

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    df = load_data(data_dir)
    
    # 計算日報酬
    returns = df.pct_change().dropna()
    
    # 【資料處理宣告】由於 RSIT 上市僅 8 天無統計意義，我們以相同底層邏輯（股+期貨）的 RSST 作為相關性與波動率的 Proxy
    returns['RSIT'] = returns['RSST']
    
    # 資產配置權重
    tickers = ['RSSB', 'RSST', 'RSSY', 'RSIT']
    weights = np.array([0.50, 0.20, 0.15, 0.15])
    returns = returns[tickers]
    
    # 投資組合預期參數 (基於近期數據)
    mean_daily = returns.mean()
    cov_matrix = returns.cov()
    
    port_mean_daily = np.dot(weights, mean_daily)
    port_var_daily = np.dot(weights.T, np.dot(cov_matrix, weights))
    
    port_mean_annual = port_mean_daily * 252
    port_vol_annual = np.sqrt(port_var_daily) * np.sqrt(252)
    
    print("-" * 50)
    print("【 投資組合基礎參數 (依 2024至今 數據推算) 】")
    print(f"預期年化報酬率: {port_mean_annual*100:.2f}%")
    print(f"預期年化波動率: {port_vol_annual*100:.2f}%")
    print("-" * 50)
    
    # 蒙地卡羅設定
    n_sims = 10000
    n_months = 240 # 20年
    dt = 1/12
    initial_cap = 1300000
    
    def run_simulation(mu, sigma, title):
        np.random.seed(42) # 固定隨機種子以利重現
        Z = np.random.standard_normal((n_sims, n_months))
        drift = (mu - 0.5 * sigma**2) * dt
        diffusion = sigma * np.sqrt(dt)
        
        paths = np.zeros((n_sims, n_months + 1))
        paths[:, 0] = initial_cap
        
        for t in range(1, n_months + 1):
            # 前5年(60個月)每月投入1萬，之後每月投入3萬
            cf = 10000 if t <= 60 else 30000
            # 幾何布朗運動 (Geometric Brownian Motion)
            paths[:, t] = paths[:, t-1] * np.exp(drift + diffusion * Z[:, t-1]) + cf
            
        final_values = paths[:, -1]
        p10 = np.percentile(final_values, 10)
        p50 = np.percentile(final_values, 50)
        p90 = np.percentile(final_values, 90)
        
        print(f"【 {title} 】(mu={mu*100:.1f}%, sigma={sigma*100:.1f}%)")
        print(f"第 10 百分位 (悲觀，運氣極差): {p10:,.0f} 元")
        print(f"第 50 百分位 (中位數，最可能): {p50:,.0f} 元")
        print(f"第 90 百分位 (樂觀，運氣極佳): {p90:,.0f} 元")
        print("-" * 50)

    # 情境一：維持近期狂暴大多頭的參數 (高報酬假設)
    run_simulation(port_mean_annual, port_vol_annual, "情境一：近期歷史延伸 (大多頭偏誤)")
    
    # 情境二：長期合理參數 (保守假設：美國大盤百年歷史 CAGR 約 10%，我們這裡給 12% 反映策略 Alpha)
    conservative_mu = 0.12
    run_simulation(conservative_mu, port_vol_annual, "情境二：長期合理推演 (回歸均值)")

if __name__ == '__main__':
    main()
