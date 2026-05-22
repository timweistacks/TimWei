import pandas as pd
import numpy as np
import os
import glob

def load_aligned_data(data_dir):
    csv_files = glob.glob(os.path.join(data_dir, "*_history.csv"))
    df_list = []
    for file in csv_files:
        ticker = os.path.basename(file).replace("_history.csv", "")
        if ticker == "RSIT": # 過濾掉 RSIT
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
    
    # 嚴格切齊：找出所有標的都有資料的最晚起始日 (以 RSSY 為準，即 2024-05-29)
    aligned_df = combined_df.dropna()
    return aligned_df

def calculate_period_metrics(s_period, risk_free_rate=0.04):
    if len(s_period) < 5:
        return None
        
    returns = s_period.pct_change().dropna()
    daily_rf = risk_free_rate / 252
    
    # 區間累積報酬 (取代 CAGR，因為不滿一年的期間看 CAGR 會嚴重失真)
    period_return = (s_period.iloc[-1] / s_period.iloc[0]) - 1
    
    # 波動率
    volatility = returns.std() * np.sqrt(252)
    
    # 夏普值 (Sharpe Ratio)
    excess_returns = returns - daily_rf
    sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else np.nan
    
    # 最大回撤 (MDD)
    roll_max = s_period.cummax()
    drawdown = (s_period - roll_max) / roll_max
    mdd = drawdown.min()
    
    return {
        '區間報酬': f"{period_return*100:.2f}%",
        '年化波動率': f"{volatility*100:.2f}%",
        '最大回撤(MDD)': f"{mdd*100:.2f}%",
        '夏普值(Sharpe)': f"{sharpe:.2f}"
    }

def analyze_periods(df):
    periods = {
        "2024 (2024-05-29 ~ 2024-12-31)": ('2024-05-29', '2024-12-31'),
        "2025 (2025-01-01 ~ 2025-12-31)": ('2025-01-01', '2025-12-31'),
        "2026 (2026-01-01 ~ 2026-05-19)": ('2026-01-01', '2026-12-31') # 使用大於等於今天的日期涵蓋至今
    }
    
    report_lines = []
    
    for period_name, (start_date, end_date) in periods.items():
        # 切取該時間段的資料
        mask = (df.index >= start_date) & (df.index <= end_date)
        df_period = df.loc[mask]
        
        if df_period.empty or len(df_period) < 10:
            continue
            
        stats = []
        for col in df_period.columns:
            metrics = calculate_period_metrics(df_period[col])
            if metrics:
                metrics['標的'] = col
                stats.append(metrics)
                
        stats_df = pd.DataFrame(stats)
        cols = ['標的', '區間報酬', '年化波動率', '最大回撤(MDD)', '夏普值(Sharpe)']
        stats_df = stats_df[cols]
        
        # 計算該期間的相關性矩陣
        corr_matrix = df_period.pct_change().dropna().corr().round(4)
        
        # 準備文字報表
        report_lines.append("=" * 80)
        report_lines.append(f"【 期間：{period_name} 】")
        report_lines.append("=" * 80)
        report_lines.append(stats_df.to_string(index=False))
        report_lines.append("\n[ 資產相關性矩陣 ]")
        report_lines.append(corr_matrix.to_string())
        report_lines.append("=" * 80 + "\n")
        
    report_text = "\n".join(report_lines)
    print(report_text)
    
    # 將結果輸出到 markdown 檔案中
    current_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(current_dir, "..", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    md_path = os.path.join(reports_dir, "period_analysis_report.md")
    
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("# 歷史分段分析報告 (2024~2026切片)\n\n")
        f.write("此報告將資料依年份分段，觀察在不同時間區間與市場氛圍下，各策略資產的輪動表現與相關性變化。\n\n")
        f.write("```text\n")
        f.write(report_text)
        f.write("\n```\n")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data")
    
    aligned_df = load_aligned_data(data_dir)
    if not aligned_df.empty:
        analyze_periods(aligned_df)
    else:
        print("無法載入資料或無重疊日期。")
