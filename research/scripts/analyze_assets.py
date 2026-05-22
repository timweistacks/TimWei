import pandas as pd
import numpy as np
import os
import glob
from pathlib import Path

def load_data(data_dir):
    """載入所有 CSV 資料並合併成一個以 Date 為 index 的 DataFrame，取 Adj Close 或 Close。"""
    csv_files = glob.glob(os.path.join(data_dir, "*_history.csv"))
    df_list = []
    
    for file in csv_files:
        ticker = os.path.basename(file).replace("_history.csv", "")
        try:
            df = pd.read_csv(file, parse_dates=['Date'], index_col='Date')
            
            # 使用 Adj Close，如果沒有則使用 Close
            if 'Adj Close' in df.columns:
                series = df['Adj Close']
            elif 'Close' in df.columns:
                series = df['Close']
            else:
                continue
                
            series.name = ticker
            df_list.append(series)
        except Exception as e:
            print(f"Error loading {ticker}: {e}")
            
    if not df_list:
        return pd.DataFrame()
        
    combined_df = pd.concat(df_list, axis=1)
    combined_df.sort_index(inplace=True)
    return combined_df

def analyze_assets(df):
    """計算收益、波動率與蒙地卡羅所需參數"""
    # 計算每日報酬率
    daily_returns = df.pct_change().dropna(how='all')
    
    stats = []
    for col in daily_returns.columns:
        s = daily_returns[col].dropna()
        if len(s) == 0:
            continue
            
        # 每日平均報酬率與每日標準差 (蒙地卡羅模擬用參數)
        daily_mean = s.mean()
        daily_std = s.std()
        
        # 年化參數 (假設一年 252 個交易日)
        annual_return = daily_mean * 252
        annual_volatility = daily_std * np.sqrt(252)
        
        # 複合年均成長率 (CAGR)
        start_price = df[col].dropna().iloc[0]
        end_price = df[col].dropna().iloc[-1]
        years = len(s) / 252
        if years > 0:
            cagr = (end_price / start_price) ** (1 / years) - 1
        else:
            cagr = np.nan
            
        stats.append({
            '標的': col,
            '資料天數': len(s),
            '每日平均收益 (蒙地卡羅用_Mu)': f"{daily_mean:.6f}",
            '每日標準差 (蒙地卡羅用_Sigma)': f"{daily_std:.6f}",
            '年化波動率': f"{annual_volatility * 100:.2f}%",
            '年化收益率 (算術)': f"{annual_return * 100:.2f}%",
            '年化複合收益 (CAGR)': f"{cagr * 100:.2f}%" if pd.notnull(cagr) else "N/A"
        })
        
    stats_df = pd.DataFrame(stats)
    
    # 計算相關性矩陣 (以每日報酬率計算)
    correlation_matrix = daily_returns.corr()
    
    print("=" * 60)
    print("【各標的收益與波動率統計 (可用於蒙地卡羅模擬)】")
    print("=" * 60)
    # 使用 pandas 的 display 選項以完整顯示 DataFrame
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats_df.to_string(index=False))
    
    print("\n" + "=" * 60)
    print("【資產相關性矩陣 (Correlation Matrix)】")
    print("=" * 60)
    print(correlation_matrix.round(4).to_string())
    print("=" * 60)
    
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    
    combined_prices = load_data(data_dir)
    if combined_prices.empty:
        print("沒有找到有效的股價資料。")
    else:
        analyze_assets(combined_prices)
