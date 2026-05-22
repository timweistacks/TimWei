import pandas as pd
import numpy as np
import os
import glob

def load_data(data_dir):
    csv_files = glob.glob(os.path.join(data_dir, "*_history.csv"))
    df_list = []
    for file in csv_files:
        ticker = os.path.basename(file).replace("_history.csv", "")
        # 過濾掉 RSIT
        if ticker == "RSIT":
            continue
            
        try:
            df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
            series = df['Adj Close'] if 'Adj Close' in df.columns else df['Close']
            series.name = ticker
            df_list.append(series)
        except Exception as e:
            print(f"Error loading {ticker}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    combined_df = pd.concat(df_list, axis=1)
    combined_df.sort_index(inplace=True)
    return combined_df

def calculate_metrics(series, risk_free_rate=0.04):
    s = series.dropna()
    if len(s) < 2:
        return None
        
    # 計算日報酬率
    returns = s.pct_change().dropna()
    daily_rf = risk_free_rate / 252
    
    # CAGR
    start_price = s.iloc[0]
    end_price = s.iloc[-1]
    years = len(s) / 252
    cagr = (end_price / start_price) ** (1 / years) - 1 if years > 0 else np.nan
    
    # 波動率
    volatility = returns.std() * np.sqrt(252)
    
    # 夏普值 (Sharpe Ratio)
    excess_returns = returns - daily_rf
    sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else np.nan
    
    # 索提諾比率 (Sortino Ratio)
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = downside_returns.std()
    sortino = (excess_returns.mean() / downside_std) * np.sqrt(252) if not pd.isna(downside_std) and downside_std != 0 else np.nan
    
    # 最大回撤 (MDD)
    roll_max = s.cummax()
    drawdown = (s - roll_max) / roll_max
    mdd = drawdown.min()
    
    return {
        '資料天數': len(s),
        '起算日期': s.index[0].strftime('%Y-%m-%d'),
        'CAGR': f"{cagr*100:.2f}%",
        '年化波動率': f"{volatility*100:.2f}%",
        '最大回撤(MDD)': f"{mdd*100:.2f}%",
        '夏普值(Sharpe)': f"{sharpe:.2f}",
        '索提諾(Sortino)': f"{sortino:.2f}"
    }

def print_report(df, title):
    stats = []
    for col in df.columns:
        metrics = calculate_metrics(df[col])
        if metrics:
            metrics['標的'] = col
            stats.append(metrics)
            
    stats_df = pd.DataFrame(stats)
    # 重新排序欄位
    cols = ['標的', '起算日期', '資料天數', 'CAGR', '年化波動率', '最大回撤(MDD)', '夏普值(Sharpe)', '索提諾(Sortino)']
    stats_df = stats_df[cols]
    
    print("=" * 80)
    print(f"【 {title} 】(假設無風險利率 = 4%)")
    print("=" * 80)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats_df.to_string(index=False))
    print("=" * 80 + "\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    
    df = load_data(data_dir)
    if not df.empty:
        # 1. 各自獨立計算 (上市至今)
        print_report(df, "獨立生命週期計算 (各自上市至今)")
        
        # 2. 同期對齊計算 (找出最晚的起始日，切齊所有數據)
        # 去除全空的行，然後找出所有欄位都不為 NaN 的時間段
        aligned_df = df.dropna()
        print_report(aligned_df, "嚴格同期計算 (切齊至最晚發行的標的)")
    else:
        print("無法載入資料。")
