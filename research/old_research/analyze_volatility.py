import pandas as pd
import numpy as np
import argparse
import os

def analyze(file_path, window=21):
    if not os.path.exists(file_path):
        print(f"[!] 檔案不存在: {file_path}")
        return

    df = pd.read_csv(file_path, index_col=0, parse_dates=True)
    ticker = os.path.basename(file_path).replace(".csv", "")

    # 1. 簡單實現波動率 (Standard Realized Volatility)
    # 使用 Adj Close 計算每日對數報酬率
    close_col = 'Adj Close' if 'Adj Close' in df.columns else 'Close'
    df['log_return'] = np.log(df[close_col] / df[close_col].shift(1))
    df['realized_vol'] = df['log_return'].rolling(window=window).std() * np.sqrt(252)

    # 2. Parkinson 波動率 (使用 High-Low，對日內波動更敏感)
    # Formula: sqrt(252 / (4 * window * ln(2)) * SUM(ln(High/Low)^2))
    df['parkinson_sum'] = np.log(df['High'] / df['Low'])**2
    df['parkinson_vol'] = np.sqrt(252 / (4 * np.log(2))) * np.sqrt(df['parkinson_sum'].rolling(window=window).mean())

    latest_rv = df['realized_vol'].iloc[-1]
    latest_pv = df['parkinson_vol'].iloc[-1]
    
    print(f"\n===== {ticker} 波動率分析 (Window: {window}d) =====")
    print(f"今日實現波動率 (Realized Vol): {latest_rv:.2%}")
    print(f"今日日內波動率 (Parkinson Vol): {latest_pv:.2%}")
    print(f"--------------------------------------------------")
    print(f"歷史平均實現波動率: {df['realized_vol'].mean():.2%}")
    print(f"區間最高實現波動率: {df['realized_vol'].max():.2%}")
    print(f"區間最低實現波動率: {df['realized_vol'].min():.2%}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="分析波動率")
    parser.add_argument("file", help="CSV 檔案路徑")
    parser.add_argument("--window", type=int, default=21, help="滾動視窗大小 (預設 21 天)")
    args = parser.parse_args()
    
    analyze(args.file, args.window)
