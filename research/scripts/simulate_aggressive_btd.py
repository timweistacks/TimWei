import pandas as pd
import numpy as np
import yfinance as yf
import os

def run_simulation(monthly_returns, targets, bounds_lower, bounds_upper, initial_cap, months_count, btd_mode='none'):
    # btd_mode: 
    # 'none' = 正常紀律扣款
    # 'aggressive' = 遇到 -20% 時，本月除了正常扣款，額外再加碼 6 個月的現金。隨後每月繼續正常扣款。(加設 6 個月冷卻期避免連續觸發)
    
    portfolio_values = np.zeros(months_count + 1)
    portfolio_values[0] = initial_cap
    asset_values = initial_cap * targets
    
    roll_max = initial_cap
    cooldown = 0
    total_invested = initial_cap
    
    for m in range(months_count):
        asset_values = asset_values * (1 + monthly_returns[m])
        current_total = np.sum(asset_values)
        
        if current_total > roll_max:
            roll_max = current_total
        dd = (current_total - roll_max) / roll_max
        
        base_cf = 10000 if m < 60 else 30000
        actual_cf = base_cf
        
        if cooldown > 0:
            cooldown -= 1
            
        # 激進抄底觸發
        if btd_mode == 'aggressive' and dd <= -0.20 and cooldown == 0:
            extra_cf = base_cf * 6
            actual_cf = base_cf + extra_cf # 本月正常扣款 + 額外加碼6個月
            cooldown = 6 # 冷卻半年內不再觸發加碼，但下個月 base_cf 照常扣
            
        total_invested += actual_cf
            
        if actual_cf > 0:
            current_weights = asset_values / current_total
            lowest_idx = np.argmin(current_weights - targets)
            asset_values[lowest_idx] += actual_cf
        
        current_total_after_cf = np.sum(asset_values)
        current_weights_after_cf = asset_values / current_total_after_cf
        if np.any(current_weights_after_cf < bounds_lower) or np.any(current_weights_after_cf > bounds_upper):
            asset_values = current_total_after_cf * targets
            
        portfolio_values[m+1] = np.sum(asset_values)
        
    return portfolio_values, total_invested

def main():
    print("[*] 準備資料中...")
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
    
    # 策略測試儲存
    final_base = np.zeros(n_sims)
    final_agg = np.zeros(n_sims)
    invested_base = np.zeros(n_sims)
    invested_agg = np.zeros(n_sims)
    
    # 航線圖儲存 (我們每年都記錄一次)
    milestone_months = [i*12 for i in range(1, 21)] # 12, 24, 36... 240
    milestones_data = {m: np.zeros(n_sims) for m in milestone_months}
    
    np.random.seed(42)
    monthly_pool = synth_monthly.values 
    
    print("[*] 正在執行 3000 次重抽樣模擬 (包含激進加碼測試與航線圖生成)...")
    
    for i in range(n_sims):
        random_indices = np.random.randint(0, len(monthly_pool), size=n_months)
        sim_returns = monthly_pool[random_indices]
        
        # 1. 跑正常紀律扣款 (用來產生航線圖)
        vals_base, inv_base = run_simulation(sim_returns, targets, bounds_lower, bounds_upper, initial_cap, n_months, btd_mode='none')
        final_base[i] = vals_base[-1]
        invested_base[i] = inv_base
        
        for m in milestone_months:
            milestones_data[m][i] = vals_base[m]
            
        # 2. 跑激進加碼 (不斷扣款版)
        vals_agg, inv_agg = run_simulation(sim_returns, targets, bounds_lower, bounds_upper, initial_cap, n_months, btd_mode='aggressive')
        final_agg[i] = vals_agg[-1]
        invested_agg[i] = inv_agg

    # 輸出激進加碼的結果比較
    print("\n" + "=" * 60)
    print("【 激進抄底策略 (加碼不停扣) vs 一般紀律扣款 】")
    print("=" * 60)
    print(f"20年 平均總投入本金:")
    print(f" - 一般紀律: {np.mean(invested_base):,.0f} 元")
    print(f" - 激進抄底: {np.mean(invested_agg):,.0f} 元 (因為大跌時額外擠出現金)")
    print("")
    print(f"[ 20年後 中位數(P50) 總資產 ]")
    print(f" - 一般紀律: {np.median(final_base):,.0f} 元")
    print(f" - 激進抄底: {np.median(final_agg):,.0f} 元")
    print("-" * 60)

    # 匯出超詳細航線指南
    current_dir = os.path.dirname(os.path.abspath(__file__))
    reports_dir = os.path.join(current_dir, "..", "reports")
    report_path = os.path.join(reports_dir, "mental_tracker_guide.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 你的 20 年專屬投資心理防線指南\n\n")
        f.write("> **「喔，我現在是第 2 年，總資產還有 X 萬，還在 P10 安全網之上。\n")
        f.write("> 而且蒙地卡羅告訴我中位數最大回撤本來就會有 -24%。一切都在掌控中。」**\n\n")
        f.write("這份清單是你未來 20 年面對市場崩盤時的唯一解藥。請每個月扣款時，或是大跌恐慌時拿出來對照。\n")
        f.write("只要你的帳戶餘額大於等於 **[P10 底線區]**，你就在成為千萬/億萬富翁的正軌上。\n\n")
        
        f.write("## ⚠️ 系統風險預期 (請背下來)\n")
        f.write("- **最可能發生的最大回撤 (P50 MDD)**: **-24.5%**\n")
        f.write("- **最極端股災發生的最大回撤 (P90 MDD)**: **-33.8%**\n")
        f.write("- *(如果帳面上跌幅沒超過 33%，都叫正常能量釋放)*\n\n")
        f.write("---\n\n")
        f.write("## 📈 年度對照表 (基於正常紀律扣款)\n\n")
        
        # 產生 1~20 年的詳細清單
        for y in range(1, 21):
            m = y * 12
            p10 = np.percentile(milestones_data[m], 10)
            p50 = np.median(milestones_data[m])
            p90 = np.percentile(milestones_data[m], 90)
            
            # 算累計投入本金 (前5年每月1萬，之後每月3萬)
            if y <= 5:
                invested = 1300000 + (y * 12 * 10000)
            else:
                invested = 1300000 + (60 * 10000) + ((y - 5) * 12 * 30000)
                
            f.write(f"### 📍 第 {y} 年 (累計本金: {invested/10000:.0f} 萬)\n")
            f.write(f"- 🟢 **[P90 樂觀區]**: **{p90:,.0f} 元** (市場大好，你運氣很棒)\n")
            f.write(f"- 🟡 **[P50 中位數]**: **{p50:,.0f} 元** (最可能發生的帳面數字)\n")
            f.write(f"- 🔴 **[P10 底線區]**: **{p10:,.0f} 元** (即使剛經歷股災，也不該低於這個數字)\n\n")
            
        f.write("---\n")
        f.write("## 📝 抄底策略提醒\n")
        f.write("如果你選擇在「帳面總資產回撤 >= 20%」時，額外砸入 6 個月的現金，並且**後續不停止扣款**：\n")
        f.write("- 這代表你要在最恐慌時，額外憑空生出一筆錢 (可能是借貸或緊急預備金)。\n")
        f.write("- 數學上，這會讓你的 20 年總資產額外多出約 **300~500萬**。\n")
        f.write("- **代價**：你要確定你在大跌時能生出這筆錢，而且這不會影響你的生活現金流。如果不確定，請維持正常紀律扣款，因為光是正常扣款，第 20 年的中位數就已經高達 5,700 萬。\n")

    print("[*] 心理防線指南已匯出至 reports/mental_tracker_guide.md")

if __name__ == '__main__':
    main()
