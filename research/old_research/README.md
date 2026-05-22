# Research & Analysis Sandbox

這是一個完全獨立的研究專區。這裡的程式碼與數據不會影響到主專案的 `chronicle/data`。

## 功能
- `fetch_history.py`: 抓取歷史數據並存成 CSV。
- `calc_volatility.py`: 讀取 CSV 並計算實現波動率 (Realized Volatility)。

## 使用方式
1. 抓取數據: `python research/fetch_history.py --ticker RSSB`
2. 計算波動率: `python research/calc_volatility.py --file research/data/RSSB_history.csv`
