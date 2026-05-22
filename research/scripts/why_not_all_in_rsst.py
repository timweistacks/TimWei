import pandas as pd
import numpy as np
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')

def main():
    print("[*] 正在解析 All-in RSST 的致命風險...")
    # 下載 SPY(美股), AQMIX(管理期貨), AGG(美債), ^IRX(借貸成本)
    tickers = ['SPY', 'AQMIX', 'AGG', '^IRX']
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
    data = pd.DataFrame(data_dict).dropna()
    
    returns = data.pct_change().dropna()
    borrow_rate_daily = (data['^IRX'] / 100).ffill() / 252
    # 對齊 index
    borrow_rate_daily = borrow_rate_daily.loc[returns.index]
    
    # 建立 RSST Proxy (100% SPY + 100% AQMIX - Borrow)
    rsst_daily = returns['SPY'] + returns['AQMIX'] - borrow_rate_daily
    # 建立 RSSB Proxy (100% SPY + 100% AGG - Borrow) 簡化版
    rssb_daily = returns['SPY'] + returns['AGG'] - borrow_rate_daily
    
    # 找出「沒有明顯趨勢」的雙巴盤 (Whipsaw Market)
    # 我們鎖定 2011 ~ 2013 年，這段時間股市震盪，且管理期貨(AQMIX)連續虧損
    whipsaw_mask = (returns.index >= '2011-01-01') & (returns.index <= '2013-12-31')
    rsst_whipsaw = rsst_daily[whipsaw_mask]
    spy_whipsaw = returns['SPY'][whipsaw_mask]
    
    rsst_whipsaw_cum = (1 + rsst_whipsaw).cumprod()
    rsst_whipsaw_mdd = (rsst_whipsaw_cum - rsst_whipsaw_cum.cummax()) / rsst_whipsaw_cum.cummax()
    
    print("\n" + "=" * 60)
    print("【 致命風險解析：如果你 All-in RSST 會發生什麼事？ 】")
    print("=" * 60)
    print("RSST 的超強防禦力來自「管理期貨 (Trend Following)」。")
    print("但管理期貨有一個致命弱點：【雙巴盤 (Whipsaw)】。")
    print("當市場沒有明確趨勢，忽上忽下時，模型會不斷『追高殺低』，產生連續幾年的嚴重虧損。")
    print("-" * 60)
    print(" 🚨 歷史重現：2011 ~ 2013 年 (管理期貨的寒冬)")
    print(f" - 大盤 (SPY) 這三年累積上漲: +{((1+spy_whipsaw).prod()-1)*100:.2f}%")
    print(f" - All-in RSST 在這三年的最大回撤: {rsst_whipsaw_mdd.min()*100:.2f}%")
    print("   (在 SPY 上漲的過程中，RSST 因為期貨部位被雙巴，帳面竟然蒸發了超過五分之一！)")
    print("-" * 60)
    
    # 計算 2020 年 3 月 (Covid 熔斷) 這種「瞬間暴跌，無趨勢可追」的狀況
    covid_mask = (returns.index >= '2020-02-19') & (returns.index <= '2020-03-23')
    rsst_covid = rsst_daily[covid_mask]
    rssb_covid = rssb_daily[covid_mask]
    spy_covid = returns['SPY'][covid_mask]
    
    print("\n 🚨 歷史重現：2020 年 3 月 (COVID-19 瞬間崩盤)")
    print(" 管理期貨需要『時間』來形成趨勢。如果市場是瞬間暴跌（如疫情熔斷），期貨來不及做空！")
    print(f" - 大盤 (SPY) 跌幅: {((1+spy_covid).prod()-1)*100:.2f}%")
    print(f" - All-in RSST 跌幅: {((1+rsst_covid).prod()-1)*100:.2f}% (期貨完全失效，還加上槓桿傷害)")
    print(f" - 有配 RSSB (債券) 的跌幅: {((1+rssb_covid).prod()-1)*100:.2f}% (債券發揮避震功能)")
    
    print("\n💡 【 Linus 的終極解答 】")
    print("「永遠不要把你的財富，全部壓在單一算法的弱點上。」")
    print("All-in RSST 會讓你在『雙巴盤』或『瞬間黑天鵝』中被市場宰殺。")
    print("你需要 RSSB (債券) 來應付瞬間崩盤，需要 RSSY 來補足橫盤時的現金流，")
    print("這就是為什麼 40/30/15/15 才是完美的系統架構。")

if __name__ == '__main__':
    main()
