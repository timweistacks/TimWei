import yfinance as yf
import pandas as pd
import argparse
import os
from pathlib import Path

def fetch_data(ticker, period="1y"):
    """抓取歷史數據並存成 CSV。"""
    print(f"[*] 正在抓取 {ticker} 的歷史數據 (期間: {period})...")
    try:
        data = yf.download(ticker, period=period)
        if data.empty:
            print(f"[!] 找不到 {ticker} 的數據。")
            return
        
        output_dir = Path("research/data")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_path = output_dir / f"{ticker}_history.csv"
        data.to_csv(output_path)
        print(f"[+] 數據已儲存至: {output_path}")
    except Exception as e:
        print(f"[!] 抓取失敗: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="抓取歷史數據工具")
    parser.add_argument("--ticker", required=True, help="標的代號 (例如: RSSB)")
    parser.add_argument("--period", default="1y", help="時間範圍 (1y, 2y, max 等)")
    args = parser.parse_args()
    
    fetch_data(args.ticker, args.period)
