import yfinance as yf
import pandas as pd
import os
from datetime import datetime, timedelta

def fetch_historical_data(tickers, days=365):
    """
    抓取指定標的的歷史數據並存成 CSV。
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    os.makedirs("research/data", exist_ok=True)
    
    for ticker in tickers:
        print(f"正在抓取 {ticker}...")
        df = yf.download(ticker, start=start_date, end=end_date)
        if not df.empty:
            file_path = f"research/data/{ticker}.csv"
            df.to_csv(file_path)
            print(f"已儲存至 {file_path}")
        else:
            print(f"找不到 {ticker} 的數據")

if __name__ == "__main__":
    # 預設抓取你目前的組合標的
    my_tickers = ["RSSB", "RSST", "RSIT", "RSSY", "SPY", "GLDM"]
    fetch_historical_data(my_tickers)
