import pandas as pd
import numpy as np
import argparse
import os

def calculate_realized_vol(file_path, window=21):
    """計算年化實現波動率 (Realized Volatility)。"""
    if not os.path.exists(file_path):
        print(f"[!] 錯誤: 找不到檔案 {file_path}")
        return

    # 讀取數據
    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    
    # 判斷使用的價格欄位
    col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    
    # 計算對數收益率 (Log Returns)
    df['Log_Ret'] = np.log(df[col] / df[col].shift(1))
    
    # 計算滾動波動率並年化 (252 個交易日)
    df['Vol'] = df['Log_Ret'].rolling(window=window).std() * np.sqrt(252)
    
    latest_vol = df['Vol'].iloc[-1]
    avg_vol = df['Vol'].mean()
    
    print(f"\n--- 波動率分析結果: {os.path.basename(file_path)} ---")
    print(f"滾動視窗: {window} 個交易日")
    print(f"最新年化波動率: {latest_vol:.2%}")
    print(f"期間平均波動率: {avg_vol:.2%}")
    print(f"期間最高波動率: {df['Vol'].max():.2%}")
    print(f"期間最低波動率: {df['Vol'].min():.2%}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="波動率計算工具")
    parser.add_argument("--file", required=True, help="CSV 歷史數據路徑")
    parser.add_argument("--window", type=int, default=21, help="滾動視窗大小 (預設 21 天)")
    args = parser.parse_args()
    
    calculate_realized_vol(args.file, args.window)
