import pandas as pd
import numpy as np
import os
from pathlib import Path

def calculate_volatility(file_path, window=21):
    """計算年化實現波動率 (Realized Volatility)。
    
    Args:
        file_path: CSV 檔案路徑
        window: 滾動視窗大小（預設 21 天，約一個月交易日）
    """
    if not os.path.exists(file_path):
        print(f"錯誤: 找不到檔案 {file_path}")
        return

    # 讀取數據，將第一欄設為索引並解析日期
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    
    # 確保資料依時間排序
    df = df.sort_index()

    # 使用 Adj Close 或 Close
    col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    
    # 計算每日對數收益率 (Log Returns) - 數學上更精確
    df['Log_Returns'] = np.log(df[col] / df[col].shift(1))
    
    # 計算滾動標準差並年化 (假設一年 252 個交易日)
    df['Vol_Ann'] = df['Log_Returns'].rolling(window=window).std() * np.sqrt(252)
    
    latest_vol = df['Vol_Ann'].iloc[-1]
    avg_vol = df['Vol_Ann'].mean()
    
    print(f"\n===== {Path(file_path).stem} 波動率分析 =====")
    print(f"數據區間: {df.index[0].date()} 至 {df.index[-1].date()}")
    print(f"計算視窗: {window} 個交易日")
    print(f"最新年化波動率: {latest_vol:.2%}")
    print(f"全期平均波動率: {avg_vol:.2%}")
    print(f"歷史最高波動率: {df['Vol_Ann'].max():.2%}")
    print(f"歷史最低波動率: {df['Vol_Ann'].min():.2%}")
    print("=" * 35)

if __name__ == "__main__":
    # 自動分析 data 資料夾下的所有 CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    
    if not os.path.exists(data_dir):
        print("請先執行 fetch_history.py 抓取數據。")
    else:
        files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]
        if not files:
            print("data 資料夾中沒有 CSV 檔案。")
        for f in files:
            calculate_volatility(os.path.join(data_dir, f))
