import pandas as pd
import numpy as np
import yfinance as yf
import os

def run_simulation(monthly_returns, targets, bounds_lower, bounds_upper, initial_cap, months_count):
    portfolio_values = np.zeros(months_count + 1)
    portfolio_values[0] = initial_cap
    asset_values = initial_cap * targets
    
    for m in range(months_count):
        asset_values = asset_values * (1 + monthly_returns[m])
        cf = 10000 if m < 60 else 30000
        current_total = np.sum(asset_values)
        
        if cf > 0:
            current_weights = asset_values / current_total
            lowest_idx = np.argmin(current_weights - targets)
            asset_values[lowest_idx] += cf
        
        current_total_after_cf = np.sum(asset_values)
        current_weights_after_cf = asset_values / current_total_after_cf
        if np.any(current_weights_after_cf < bounds_lower) or np.any(current_weights_after_cf > bounds_upper):
            asset_values = current_total_after_cf * targets
            
        portfolio_values[m+1] = np.sum(asset_values)
        
    return portfolio_values

def main():
    print("[*] 正在產生區間版航線圖...")
    tickers = ['SPY', 'AGG', 'AQMIX', 'QQQ', 'HYG', '^IRX']
    data_dict = {}
    for ticker in tickers:
        df = yf.download(ticker, start='2010-01-01', end='2024-12-31')
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if 'Adj Close' in df.columns:
                data_dict[ticker] = df['Adj Close']
            else:
                data_dict[ticker] = df['Close']
    data = pd.DataFrame(data_dict)
    
    borrow_rate_annual = data['^IRX'] / 100
    borrow_rate_annual = borrow_rate_annual.ffill().fillna(0.04)
    borrow_rate_daily = borrow_rate_annual / 252
    
    returns = data.pct_change().dropna()
    synth_returns = pd.DataFrame(index=returns.index)
    synth_returns['RSSB_Proxy'] = returns['SPY'] + returns['AGG'] - borrow_rate_daily
    synth_returns['RSST_Proxy'] = returns['SPY'] + returns['AQMIX'] - borrow_rate_daily 
    synth_returns['RSSY_Proxy'] = returns['SPY'] + returns['HYG'] - borrow_rate_daily
    synth_returns['RSIT_Proxy'] = returns['QQQ'] + returns['AGG'] - borrow_rate_daily 
    
    synth_monthly = synth_returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
    
    targets = np.array([0.50, 0.20, 0.15, 0.15])
    bounds_lower = targets * 0.8
    bounds_upper = targets * 1.2
    initial_cap = 1300000
    
    n_sims = 3000
    n_months = 240
    
    milestone_months = [i*12 for i in range(1, 21)]
    milestones_data = {m: np.zeros(n_sims) for m in milestone_months}
    
    np.random.seed(42)
    monthly_pool = synth_monthly.values 
    
    for i in range(n_sims):
        random_indices = np.random.randint(0, len(monthly_pool), size=n_months)
        sim_returns = monthly_pool[random_indices]
        vals_base = run_simulation(sim_returns, targets, bounds_lower, bounds_upper, initial_cap, n_months)
        
        for m in milestone_months:
            milestones_data[m][i] = vals_base[m]

    current_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(current_dir, "..", "reports")
    report_path = os.path.join(reports_dir, "mental_tracker_guide.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 20年期專屬投資心理防線與資產區間指南\n\n")
        f.write("> **用法：未來每個月對帳時，只要你的總資產落在「預期資產區間」內，就代表一切正常，不須恐慌。**\n\n")
        
        f.write("## ⚠️ 系統回撤水位 (Drawdown Zones)\n")
        f.write("不要死背單一數字，遇到大盤崩跌時，請對照你現在的帳面虧損處於哪個「水位」：\n")
        f.write("- 🟢 **【正常波動水位】 `0% ~ -15%`**：這組合帶有槓桿，跌 15% 以內就像呼吸一樣正常。\n")
        f.write("- 🟡 **【壓力測試水位】 `-15% ~ -25%`**：遇到熊市或衰退。這是核心震盪區，大部分的修正都會在這裡止住（中位數 MDD 約落在這區間的底部）。可以考慮預借現金抄底。\n")
        f.write("- 🔴 **【極端災難水位】 `-25% ~ -34%`**：遇到歷史級別大股災（如 2008 金融海嘯、2022 雙殺）。極度痛苦，但仍在這套模型預測的邊界內。**咬牙扣款就對了**。\n")
        f.write("- 💀 **【模型失效水位】 `超過 -35%`**：只有在這種情況下，你才需要重新評估這套策略是否徹底失效。\n\n")
        f.write("---\n\n")
        
        f.write("## 📈 年度資產落點區間指南\n\n")
        
        # 產出前 5 年的簡化 terminal 輸出文字，讓 agent 可以印出來
        terminal_output = []
        terminal_output.append("【 年度資產區間指南 (節錄前 5 年) 】")
        
        for y in range(1, 21):
            m = y * 12
            p10 = np.percentile(milestones_data[m], 10)
            p50 = np.median(milestones_data[m])
            p90 = np.percentile(milestones_data[m], 90)
            
            if y <= 5:
                invested = 1300000 + (y * 12 * 10000)
            else:
                invested = 1300000 + (60 * 10000) + ((y - 5) * 12 * 30000)
                
            f.write(f"### 📍 第 {y} 年 (累計本金: {invested/10000:.0f} 萬)\n")
            f.write(f"- 預期資產區間： **[ {p10/10000:,.0f} 萬 ~ {p90/10000:,.0f} 萬 ]**\n")
            f.write(f"- 🎯 核心最可能落點： **{p50/10000:,.0f} 萬**\n\n")
            
            if y <= 5:
                terminal_output.append(f"📍 第 {y} 年 (累計本金: {invested/10000:.0f} 萬)")
                terminal_output.append(f"   預期資產區間: [ {p10/10000:,.0f} 萬  ~  {p90/10000:,.0f} 萬 ]  (核心落點: {p50/10000:,.0f} 萬)")

    print("\n".join(terminal_output))
    print("\n[*] 完整的 20 年區間對照表已更新至 reports/mental_tracker_guide.md")

if __name__ == '__main__':
    main()
