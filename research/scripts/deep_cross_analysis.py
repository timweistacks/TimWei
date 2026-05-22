import pandas as pd
import numpy as np
import os
import glob
import warnings
warnings.filterwarnings('ignore')

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
            pass
    if df_list:
        return pd.concat(df_list, axis=1).dropna()
    return pd.DataFrame()

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    
    tickers = ['SPY', 'SSO', 'RSSB', 'RSST']
    df = load_data(data_dir, tickers)
    
    if df.empty:
        print("資料載入失敗")
        return
        
    # 日報酬與月報酬
    daily_returns = df.pct_change().dropna()
    monthly_returns = df.resample('ME').apply(lambda x: (1+x).prod() - 1).dropna()
    
    spy_daily = daily_returns['SPY']
    spy_monthly = monthly_returns['SPY']
    
    rf_daily = 0.04 / 252
    rf_monthly = 0.04 / 12
    
    print("\n" + "=" * 80)
    print("【 深度量化解剖：Beta, Alpha, 捕獲率與動態相關性 】")
    print(f" 基準指數: SPY | 比較期間: {df.index[0].strftime('%Y-%m-%d')} ~ {df.index[-1].strftime('%Y-%m-%d')}")
    print("=" * 80)
    
    stats = []
    
    for ticker in ['SSO', 'RSSB', 'RSST']:
        asset_daily = daily_returns[ticker]
        asset_monthly = monthly_returns[ticker]
        
        # 1. 計算 Beta (對 SPY 的市場敏感度)
        cov_matrix = np.cov(asset_daily, spy_daily)
        beta = cov_matrix[0, 1] / cov_matrix[1, 1]
        
        # 2. 計算年化 Alpha (Jensen's Alpha)
        # Alpha = R_i - [R_f + Beta * (R_m - R_f)]
        ann_return = (1 + asset_daily.mean()) ** 252 - 1
        spy_ann_return = (1 + spy_daily.mean()) ** 252 - 1
        alpha = ann_return - (0.04 + beta * (spy_ann_return - 0.04))
        
        # 3. 上檔/下檔捕獲率 (Up/Down Capture Ratio) - 使用月報酬
        # SPY 上漲的月份
        up_months = spy_monthly > 0
        up_capture = (asset_monthly[up_months].mean() / spy_monthly[up_months].mean()) * 100
        
        # SPY 下跌的月份
        down_months = spy_monthly < 0
        if sum(down_months) > 0:
            down_capture = (asset_monthly[down_months].mean() / spy_monthly[down_months].mean()) * 100
        else:
            down_capture = np.nan
            
        capture_spread = up_capture - down_capture
        
        # 4. 月度勝率與盈虧比
        win_rate = (asset_monthly > 0).mean() * 100
        avg_win = asset_monthly[asset_monthly > 0].mean() * 100
        avg_loss = asset_monthly[asset_monthly < 0].mean() * 100
        
        # 5. 滾動 60 天相關性 (極值分析)
        roll_corr = asset_daily.rolling(window=60).corr(spy_daily).dropna()
        corr_max = roll_corr.max()
        corr_min = roll_corr.min()
        corr_mean = roll_corr.mean()
        
        stats.append({
            '標的': ticker,
            'Beta\n(市場連動)': f"{beta:.2f}",
            'Alpha\n(超額年化)': f"{alpha*100:+.1f}%",
            '上漲捕獲率\n(大盤漲它漲多少)': f"{up_capture:.0f}%",
            '下跌捕獲率\n(大盤跌它跌多少)': f"{down_capture:.0f}%",
            '捕獲利差\n(越高越好)': f"{capture_spread:+.0f}%",
            '勝率': f"{win_rate:.0f}%",
            '平均月賺/賠': f"+{avg_win:.1f}% / {avg_loss:.1f}%",
            '60天滾動相關性\n(最高 / 最低)': f"{corr_max:.2f} / {corr_min:.2f}"
        })
        
    stats_df = pd.DataFrame(stats)
    # Print formatted output
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    print(stats_df.to_string(index=False))
    print("-" * 80 + "\n")
    
    # 計算並印出前三大回撤分析
    print("【 深度回撤特性分析 (Drawdown Dynamics) 】")
    print(" 觀察這段真實歷史中，這三個策略在最痛苦時期的跌幅與復原狀況：")
    for ticker in ['SPY', 'SSO', 'RSSB', 'RSST']:
        s = df[ticker]
        roll_max = s.cummax()
        drawdown = (s - roll_max) / roll_max
        mdd = drawdown.min()
        print(f" > {ticker:4s} 最大回撤: {mdd*100:6.2f}%")
        
if __name__ == '__main__':
    main()
