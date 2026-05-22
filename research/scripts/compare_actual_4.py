import pandas as pd
import numpy as np
import os
import glob

def load_data(data_dir, tickers):
    df_list = []
    for ticker in tickers:
        file = os.path.join(data_dir, f"{ticker}_history.csv")
        try:
            df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
            s = df['Adj Close'] if 'Adj Close' in df.columns else df['Close']
            s.name = ticker
            df_list.append(s)
        except Exception as e:
            print(f"Error loading {ticker}: {e}")
    if df_list:
        return pd.concat(df_list, axis=1).dropna()
    return pd.DataFrame()

def calculate_metrics(s_period, risk_free_rate=0.04):
    if len(s_period) < 5:
        return None
        
    returns = s_period.pct_change().dropna()
    daily_rf = risk_free_rate / 252
    
    period_return = (s_period.iloc[-1] / s_period.iloc[0]) - 1
    
    volatility = returns.std() * np.sqrt(252)
    
    excess_returns = returns - daily_rf
    sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else np.nan
    
    roll_max = s_period.cummax()
    drawdown = (s_period - roll_max) / roll_max
    mdd = drawdown.min()
    
    return {
        '區間報酬': f"{period_return*100:.2f}%",
        '年化波動率': f"{volatility*100:.2f}%",
        '最大回撤(MDD)': f"{mdd*100:.2f}%",
        '夏普值(Sharpe)': f"{sharpe:.2f}"
    }

def print_comparison(df, period_name, start_date, end_date):
    mask = (df.index >= start_date) & (df.index <= end_date)
    df_period = df.loc[mask]
    
    if df_period.empty or len(df_period) < 10:
        return
        
    print("=" * 70)
    print(f"【 {period_name} 】 ({df_period.index[0].strftime('%Y-%m-%d')} ~ {df_period.index[-1].strftime('%Y-%m-%d')})")
    print("=" * 70)
    
    stats = []
    for col in df_period.columns:
        metrics = calculate_metrics(df_period[col])
        if metrics:
            metrics['標的'] = col
            stats.append(metrics)
            
    stats_df = pd.DataFrame(stats)
    cols = ['標的', '區間報酬', '年化波動率', '最大回撤(MDD)', '夏普值(Sharpe)']
    stats_df = stats_df[cols]
    print(stats_df.to_string(index=False))
    
    print("\n[ 資產相關性矩陣 (連動性) ]")
    corr_matrix = df_period.pct_change().dropna().corr().round(4)
    print(corr_matrix.to_string())
    print("-" * 70 + "\n")

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    
    tickers = ['SPY', 'SSO', 'RSSB', 'RSST']
    df = load_data(data_dir, tickers)
    
    if df.empty:
        print("載入資料失敗。")
        return
        
    print("\n" + "#" * 70)
    print(" 深度交叉比較：RSSB / RSST vs 大盤(SPY) / 正二(SSO) (真實歷史數據)")
    print("#" * 70 + "\n")
    
    # 1. 完整真實重疊期 (從最晚上市的 RSSB 開始)
    print_comparison(df, "完整真實重疊期 (RSSB上市至今)", '2000-01-01', '2030-12-31')
    
    # 2. 2024 完整年度
    print_comparison(df, "2024年 完整表現", '2024-01-01', '2024-12-31')
    
    # 3. 2025 完整年度
    print_comparison(df, "2025年 完整表現", '2025-01-01', '2025-12-31')
    
    # 4. 2026 今年表現
    print_comparison(df, "2026年 至今表現 (YTD)", '2026-01-01', '2026-12-31')

if __name__ == '__main__':
    main()
