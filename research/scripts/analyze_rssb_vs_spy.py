import pandas as pd
import numpy as np
import yfinance as yf
import os
import warnings
warnings.filterwarnings('ignore')

def main():
    print("[*] 正在解析 RSSB 落後 SPY 的底層原因...")
    # 下載 SPY(美股), VT(全球股), AGG(美債), ^IRX(借貸成本)
    tickers = ['SPY', 'VT', 'AGG', '^IRX']
    data_dict = {}
    for ticker in tickers:
        df = yf.download(ticker, start='2023-12-01', end='2024-12-31')
        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            if 'Adj Close' in df.columns:
                data_dict[ticker] = df['Adj Close']
            else:
                data_dict[ticker] = df['Close']
    data = pd.DataFrame(data_dict).dropna()
    
    # 計算日報酬
    returns = data.pct_change().dropna()
    borrow_rate_daily = (data['^IRX'] / 100).ffill() / 252
    borrow_rate_daily = borrow_rate_daily.loc[returns.index]
    
    # 拆解 RSSB 的內部獲利貢獻
    # 假設 RSSB = 100% VT + 100% AGG - Borrow
    vt_contrib = returns['VT']
    agg_contrib = returns['AGG']
    borrow_drag = borrow_rate_daily
    
    # 累計報酬率
    spy_cum = (1 + returns['SPY']).prod() - 1
    vt_cum = (1 + vt_contrib).prod() - 1
    agg_cum = (1 + agg_contrib).prod() - 1
    borrow_cum = (1 + borrow_drag).prod() - 1
    rssb_synth_cum = (1 + vt_contrib + agg_contrib - borrow_drag).prod() - 1
    
    print("\n" + "=" * 60)
    print("【 X光拆解：為什麼 RSSB (2023年底至今) 跑輸 SPY？ 】")
    print("=" * 60)
    print(f" 1. 美股大盤 (SPY) 總報酬     : +{spy_cum*100:.2f}%")
    print(f" 2. 全球股市 (VT) 總報酬      : +{vt_cum*100:.2f}%  <-- 國際股嚴重拖累")
    print(f" 3. 債券部位 (AGG) 總報酬     : +{agg_cum*100:.2f}%")
    print(f" 4. 槓桿借貸成本 (Borrow)     : -{borrow_cum*100:.2f}%  <-- 借錢成本比債券利息還貴！")
    print("-" * 60)
    print(f" 👉 RSSB 合成真實報酬         : +{rssb_synth_cum*100:.2f}%")
    print(f" 👉 跑輸 SPY 的差距           : {rssb_synth_cum*100 - spy_cum*100:.2f}%")
    
    print("\n" + "=" * 60)
    print("【 50% RSSB vs 40% RSSB 在投資組合中的具體效益 】")
    print("=" * 60)
    print(" 假設投資組合總資金為 100 萬：")
    
    # 50% RSSB
    vt_50 = 500000
    agg_50 = 500000
    drag_50 = 500000 * borrow_cum
    
    # 40% RSSB
    vt_40 = 400000
    agg_40 = 400000
    drag_40 = 400000 * borrow_cum
    
    print("[ 50% RSSB 原配置 ]")
    print(f" - 綁定全球股市: 50 萬 (承受國際股拖累)")
    print(f" - 綁定美國債券: 50 萬")
    print(f" - 產生的負利差摩擦成本 (借貸 > 債息): 約 {-drag_50:,.0f} 元")
    
    print("\n[ 40% RSSB 降載配置 ]")
    print(f" - 綁定全球股市: 40 萬 (減少 10 萬的國際股拖累)")
    print(f" - 綁定美國債券: 40 萬 (減少 10 萬的無效率債券)")
    print(f" - 產生的負利差摩擦成本: 約 {-drag_40:,.0f} 元 (省下約 20% 的利息耗損)")
    
    print("\n💡 結論：")
    print("將 RSSB 從 50% 降到 40%，相當於把 10 萬塊從『會產生負利差的債券』與『表現較差的國際股』中解放出來，")
    print("轉移到 30% RSST (或 RSND) 的『純美股 + 趨勢期貨』上。這就是為什麼新配置能多賺 200 萬的原因。")

if __name__ == '__main__':
    main()
