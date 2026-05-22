import yfinance as yf
import pandas as pd
import os

def fetch_and_save(tickers):
    """抓取歷史數據並儲存為 CSV。"""
    # 取得當前腳本所在的目錄，並定位到 data 資料夾
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    for ticker in tickers:
        print(f"正在抓取 {ticker}...")
        try:
            df = yf.download(ticker, period="max")
            if not df.empty:
                # 處理多層索引 (yfinance 0.2.x 之後的行為)
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                
                path = os.path.join(data_dir, f"{ticker}_history.csv")
                df.to_csv(path)
                print(f"已儲存至: {path}")
            else:
                print(f"警告: {ticker} 找不到數據。")
        except Exception as e:
            print(f"抓取 {ticker} 時發生錯誤: {e}")

if __name__ == "__main__":
    # 使用者指定的標的：RS系列, SPY, SPY正二(SSO)
    target_tickers = ["RSSB", "RSST", "RSIT", "RSSY", "SPY", "SSO"]
    fetch_and_save(target_tickers)
