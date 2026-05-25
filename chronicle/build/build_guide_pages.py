"""Generate static guide pages (learn, etfs lineup, per-ETF detail) for chronicle/site."""

from __future__ import annotations

import html
import json
import re
from pathlib import Path

from guide_i18n_en import BASE_EN, LAYER2_EN, LAYER2_VIZ_EN, STACK_EN, UI, ZH_DEFAULTS

SITE = Path(__file__).resolve().parents[1] / "site"
ETF_DIR = SITE / "etfs"

CSS_VER = "30"
JS_VER = "11"
LOCALE_VER = "7"
STYLES_VER = "8"

I18N_REGISTRY: dict[str, dict[str, str]] = {}


def register_i18n(key: str, zh: str, en: str) -> None:
    I18N_REGISTRY[key] = {"zh": zh, "en": en}


def T(key: str, zh: str, en: str | None = None) -> str:
    register_i18n(key, zh, en if en is not None else zh)
    return f'<span data-i18n="{key}">{esc(zh)}</span>'


def Th(key: str, zh: str, en: str | None = None) -> str:
    register_i18n(key, zh, en if en is not None else zh)
    return f'<th data-i18n="{key}">{esc(zh)}</th>'


def bootstrap_i18n() -> None:
    for key, zh in ZH_DEFAULTS.items():
        en_val = UI.get(key, zh)
        if isinstance(en_val, tuple):
            en_val = en_val[1]
        register_i18n(key, zh, en_val)
    for key, val in UI.items():
        if key in ZH_DEFAULTS:
            continue
        if isinstance(val, tuple):
            register_i18n(key, val[0], val[1])
        else:
            register_i18n(key, val, val)


def layer2_en(key: str, field: str, zh: str) -> str:
    strategy = LAYER2_EN.get(key, {})
    if field.startswith("points."):
        idx = int(field.split(".", 1)[1])
        points = strategy.get("points", [])
        if idx < len(points):
            return points[idx]
    return strategy.get(field, zh)


def layer2_nav_label(key: str) -> str:
    strategy = LAYER2_STRATEGIES[key]
    nav_short = strategy.get("nav_short")
    if nav_short:
        return nav_short
    return re.sub(r"（[^）]*）", "", strategy["title"]).strip()


def write_guide_locale_js() -> None:
    lines = [
        "/** Auto-generated guide i18n strings. Do not edit by hand. */",
        "(function (global) {",
        "  global.GUIDE_STRINGS = {",
    ]
    for key in sorted(I18N_REGISTRY.keys()):
        row = I18N_REGISTRY[key]
        lines.append(
            f'    {json.dumps(key)}: {{ "zh": {json.dumps(row["zh"], ensure_ascii=False)}, '
            f'"en": {json.dumps(row["en"], ensure_ascii=False)} }},'
        )
    lines.append("  };")
    lines.append("})(typeof window !== \"undefined\" ? window : globalThis);")
    (SITE / "guide-locale.js").write_text("\n".join(lines) + "\n", encoding="utf-8")


def ui_en(key: str, fallback: str = "") -> str:
    val = UI.get(key, fallback)
    if isinstance(val, tuple):
        return val[1]
    return str(val)

LAYER2_STRATEGIES: dict[str, dict] = {
    "us-bonds": {
        "title": "美國公債",
        "etfs": ["RSSB"],
        "summary": "用美債期貨建立債券利率曝險，賺債息與債價變動。",
        "pitch": "若第二層選美國公債，代表用多出來的資金建立「約 100% 美國公債曝險」。實務上通常不是去買整張美債本票，而是買美國公債期貨——2 年、5 年、10 年、長天期等，多半等權分散。債券報酬主要來自兩塊：持有一天算一天的利息（債息），以及利率變化造成的價格漲跌（利率升，債價通常跌；利率降，債價通常漲）。",
        "example": "假設多出來的 100% 全部配置在美債第二層：ETF 會同時持有數檔不同天期的美債期貨，讓利率敏感度分散，不必自己挑「買 10 年還是 30 年」。市場避險、利率下跌時，這層有機會抵銷部分股票回撤；通膨升溫、利率快速上升時，這層可能拖累整體。重點是：這是債券本身的投資邏輯，跟底下第一層是股還是債無關。",
        "points": [
            "工具是期貨，不是整張美債；用保證金撬動名義曝險，報酬疊加才做得到「100% 第二層」。",
            "RSSB 官報常見持倉如 2 年、5 年、10 年、長天期美債期貨（代碼會隨到期月份更新）。",
            "持倉表加總不到 100% 很正常：表列的是保證金佔淨值比例，不是名義曝險。",
        ],
        "official": "RSSB Product Brief：第二層等權配置 2 年、5 年、10 年、長天期美債期貨。",
        "diff": "不是「追趨勢的管理期貨」，也不是「賺展期價差的展期收益策略」。就是最傳統的利率／債券曝險——跟一般債券 ETF 邏輯相近，只是塞在第二層。",
    },
    "managed-futures": {
        "title": "管理期貨（趨勢追蹤）",
        "etfs": ["RSST", "RSIT", "RSBT"],
        "summary": "依價格趨勢做多或做空一籃子期貨，跟股票不同路。",
        "pitch": "這裡的「管理期貨」指的是趨勢追蹤（官方常稱管理期貨趨勢策略）。核心想法：價格形成上升趨勢就做多，形成下降趨勢就做空，盤整時可能減碼或換方向。不是看公司盈餘、也不是長期持有某個商品，而是跟著價格走。標的是一籃子期貨：原油、黃金、農產品、匯率、各國利率、股指等，分散在約二十多種市場。",
        "example": "多出來的 100% 會依模型訊號，在這些期貨上建立多頭或空頭。例如原油數月來屢創新高 → 模型可能維持做多原油期貨；若美股進入明顯空頭趨勢 → 可能放空標普 500 期貨。這 100% 的報酬來自「有沒有抓到趨勢」，可能跟股票完全不同步——官方 Presentation 提到，部分空頭月份這類策略曾出現正報酬（非保證未來）。RSST 這類結構還有一條 -100% 國庫券融資腿（空頭短期美債）支撐槓桿，通常不在前十大持倉表內。",
        "points": [
            "就算「做多原油」，持有的是原油期貨，不是石油公司股票。",
            "RSST 採由上而下加由下而上混合複製，同時看大盤趨勢與個別市場訊號。",
            "RSST、RSIT、RSBT 第二層邏輯相同，差別只在第一層是美股、國際股或美債。",
            "趨勢策略在盤整市可能來回被洗；不是每個空頭年都會賺。",
        ],
        "official": "RSST Presentation「Stacking in Action」：100% 美股／100% 管理期貨趨勢／-100% 國庫券；Q1 Commentary 另有管理期貨複製品質與不同股價環境績效。",
        "diff": "不要跟期貨展期收益搞混——展期收益賺的是「換月時遠近價差」，不管趨勢方向；管理期貨賭的是「價格有沒有持續往一個方向走」。",
    },
    "futures-carry": {
        "title": "期貨展期收益",
        "etfs": ["RSSY", "RSBY"],
        "summary": "賺期貨換月時，近月與遠月之間的結構性價差。",
        "pitch": "期貨每隔一段時間要展期：把快到期的近月合約賣掉，買入較遠的遠月合約，才能一直維持曝險。展期收益策略賺的就是這個換月過程裡，近月與遠月之間的價差。當近月比遠月貴（市場稱逆價差），賣近買遠時常能「高賣低買」，累積展期收益；當遠月比近月貴（正價差），換月可能要補貼遠月，可能拖累報酬。RSSY、RSBY 的第二層不是賭原油暴漲暴跌，而是長期持有這種展期結構因子。",
        "example": "多出來的 100% 會配置在一籃子商品、利率等期貨的展期收益模型上。簡化例子：天然氣近月 3 元、遠月 2.8 元 → 近月較貴；展期換成遠月時，價差中的一部分可能變成收益（實務更複雜，且有風控）。反之近月 2.8 元、遠月 3.2 元 → 遠月較貴，展期可能付出成本。官方 Product Brief 稱這類為期貨展期收益因子——重點在遠近月結構，不在猜單一商品漲跌方向。",
        "points": [
            "名字都有「期貨」，但跟管理期貨完全是兩套邏輯：一個管趨勢，一個管換月價差。",
            "部分商品長年正價差（例如某些年份的原油），展期收益可能平淡甚至為負——這是策略特性。",
            "RSSY 第一層是美股；RSBY 第一層是美債——第二層展期收益邏輯相同。",
        ],
        "official": "RSSY Product Brief：第二層為期貨展期收益策略；正價差／逆價差結構是報酬主要驅動。",
        "diff": "不是管理期貨趨勢追蹤，也不是買現貨商品 ETF；更不是「看技術分析猜方向」。",
    },
    "gold-bitcoin": {
        "title": "黃金＋比特幣（風險平價）",
        "nav_short": "金＋幣",
        "etfs": ["RSSX"],
        "summary": "黃金、比特幣期貨依波動調權重，風險貢獻盡量相等。",
        "pitch": "RSSX 的第二層同時配置黃金期貨與比特幣期貨，但不是固定各 50%。官方採風險平價：看過去 63 天誰的波動較大，波動大的減碼、波動小的加碼，大約每月再平衡，讓兩者對組合的風險貢獻盡量接近。黃金常被視為避險資產；比特幣波動通常更大——兩者一起配，是要在「硬資產」這條腿上分散，而不是只押一邊。",
        "example": "多出來的 100% 會依波動率動態調整黃金、比特幣期貨權重。假設某月比特幣波動明顯放大 → 模型可能減少比特幣曝險、增加黃金，避免整條第二層被高波動資產主導。反之比特幣進入相對穩定期 → 可能多配一點。這 100% 用期貨實現，不是買金條或冷錢包囤幣；期貨同樣有保證金與展期。黃金、比特幣與美股相關性歷史上較低（官方 Brief 約 0.09、0.23），因此適合作不同路的第二層——但相關性可能隨市場改變。",
        "points": [
            "不是「現貨買幣＋買黃金 ETF」的簡單疊加，是統一在風險平價框架下管兩種期貨。",
            "硬資產仍可能大跌——比特幣歷史回撤幅度遠大於黃金。",
            "持倉細節（期貨、現貨 ETF 比例）以該檔最新公開資料為準。",
        ],
        "official": "RSSX Product Brief：黃金與標普 500 相關約 0.09、比特幣約 0.23；約每 63 天依波動再平衡。",
        "diff": "不是買黃金 ETF 或現貨比特幣就畢事；也不是固定一半一半，而是動態風險平價。",
    },
    "merger-arb": {
        "title": "併購套利",
        "etfs": ["RSBA"],
        "summary": "投資已公告併購案，賭收購價與市價價差收斂。",
        "pitch": "併購套利是事件驅動策略：公司 A 宣布併購公司 B 之後，B 股價通常會往上跳，但多半仍低於 A 出價——市場擔心併購失敗、延期或削價。基金通常買 B（被併購方），並避險 A（併購方），賭的是：若併購順利完成，B 會漲向收購價，中間價差就是報酬來源。",
        "example": "多出來的 100% 會追蹤併購套利指數，分散在多起進行中的併購案。簡化例子：A 出價每股 50 元買 B，B 現價 45 → 買 B，並對沖相關風險（例如放空部分 A 或做市場避險），若成交 B 漲向 50，價差收斂即獲利。若監管否決、A 放棄、或 B 業績轉差 → B 可能跌回併購前，單一案子虧損可以很大；因此必須高度分散。這條腿與日常股債大盤連動性通常較低（官方約 -0.02 與美債），但不是無風險。",
        "points": [
            "不是長期押併購題材股「等消息」——而是已公告、進行中的案子，持續時間常以月計。",
            "換手率高、事件密集，跟買指數型 ETF 的體驗完全不同。",
            "最大風險是併購破局，不是一般熊市那種大盤連動回撤。",
        ],
        "official": "RSBA Product Brief：追蹤 AlphaBeta 併購套利指數；與美債相關約 -0.02。",
        "diff": "不是一般「併購概念股」投資；跟管理期貨、展期收益、債券曝險都無關。",
    },
}

LAYER2_ORDER = (
    "us-bonds",
    "managed-futures",
    "futures-carry",
    "gold-bitcoin",
    "merger-arb",
)

LAYER2_ACCENT: dict[str, str] = {
    "us-bonds": "bond",
    "managed-futures": "trend",
    "futures-carry": "carry",
    "gold-bitcoin": "hard",
    "merger-arb": "arb",
}


def layer2_strategy_key(stack_label: str) -> str | None:
    if "管理期貨" in stack_label:
        return "managed-futures"
    if "Carry" in stack_label or "展期" in stack_label:
        return "futures-carry"
    if "黃金" in stack_label or "比特幣" in stack_label:
        return "gold-bitcoin"
    if "併購" in stack_label:
        return "merger-arb"
    if "公債" in stack_label or stack_label == "美國公債":
        return "us-bonds"
    return None

LAYER1_TICKERS = frozenset({"SPYM", "SPAB", "SPTM", "VXUS", "IBIT"})
LAYER1_FUTURES = frozenset({"ESM6", "HWAM6"})

SUITE_ROWS = [
    ("RSSB", "全球股債", "Global Stocks & Bonds", "全球股票", "美國公債", "2023-12-04", "$431.6M", "capital", True),
    ("RSST", "美股＋管理期貨趨勢", "U.S. Stocks & Managed Futures", "美國股票", "管理期貨（趨勢）", "2023-09-06", "$347.5M", "alt", True),
    ("RSSY", "美股＋期貨展期收益", "U.S. Stocks & Futures Yield", "美國股票", "期貨展期收益", "2024-05-29", "$94.4M", "alt", True),
    ("RSIT", "國際股＋管理期貨", "International Stocks & Managed Futures", "國際股票", "管理期貨（趨勢）", "2026-05-07", "新標的", "alt", True),
    ("RSSX", "美股＋黃金／比特幣", "U.S. Stocks & Gold/Bitcoin", "美國股票", "黃金＋比特幣（風險平價）", "2025-05-29", "$57.8M", "alt", False),
    ("RSBT", "債券＋管理期貨", "Bonds & Managed Futures", "美國債券", "管理期貨（趨勢）", "2023-02-06", "$118.3M", "bond", False),
    ("RSBY", "債券＋期貨展期收益", "Bonds & Futures Yield", "美國債券", "期貨展期收益", "2024-08-20", "$84.2M", "bond", False),
    ("RSBA", "債券＋併購套利", "Bonds & Merger Arbitrage", "美國公債", "併購套利", "2024-12-17", "$57.1M", "bond", False),
]

ETF_DETAILS: dict[str, dict] = {
    "rssb": {
        "tagline": "Return Stacked 系列的地基：100% 全球股 ＋ 100% 美債，一檔 ETF 搞定 200% 曝險。",
        "layers": [
            ("第一層 · 全球股票 100%", "追蹤全球市值加權股票（SPTM + VXUS 等），目標覆蓋全球可投資股票市場。"),
            ("第二層 · 美國公債 100%", "等權配置 2 年、5 年、10 年、長天期美債期貨，提供與股票低相關的債券曝險。"),
        ],
        "why": [
            "🗺️ <strong>資本效率最大化</strong>：每配置 10% 的 RSSB，相當於在投資組合中同時擁有 <strong>10% 全球股票</strong>與 <strong>10% 美國公債</strong>。這能<strong>釋放 10% 的閒置資金</strong>（透過衍生性商品融資槓桿實現），讓你可以配置到與股債低相關的非傳統策略（如 CTA、黃金或套利），極大化資金效率。",
            "⚡ <strong>優化資產配置彈性</strong>：傳統上要增加分散化資產（如 trend），必須砍掉原有的股票或債券曝險。使用 RSSB 後，你可以賣掉原先 100% 股債的部分倉位，改買 RSSB，在維持「<strong>完全相同的股債曝險</strong>」的同時，<strong>騰出寶貴現金</strong>配置在新資產上。",
            "🧠 <strong>降低行為金融學偏差</strong>：當股票大漲、債券表現平平或回檔時，投資人往往會因為痛苦而手癢砍掉用來分散風險的債券部位。將股票與債券「疊加」在同一檔 ETF，在報表上只會看到單一淨值波動，能<strong>有效降低投資人因單一資產回撤而過早放棄分散配置的心理偏差</strong>。",
            "⚙️ <strong>自動化槓桿融資</strong>：透過 ETF 內部合約，投資人<strong>無需自行開立保證金帳戶</strong>或進行期貨滾倉操作，即可自動獲得低成本的短期國庫券融資，免去個人操作的稅務與保證金追繳風險。"
        ],
        "fund": {
            "inception": "2023-12-04",
            "holdings": "7",
            "expense_gross": "0.55%",
            "expense_net": "0.40%",
            "expense_note": "管理費減免至 2026-05-30，淨費率 0.40%",
            "sec_yield": "1.71%",
            "exchange": "CBOE",
        },
        "holdings": [
            ("SPTM", "SPDR Portfolio S&P 1500", "53.03%"),
            ("VXUS", "Vanguard Total International Stock", "37.44%"),
            ("TUM6", "US 2Y Treasury Note Fut Jun26", "25.71%"),
            ("FVM6", "US 5Y Treasury Note Fut Jun26", "25.61%"),
            ("USM6", "US Long Bond Fut Jun26", "25.56%"),
            ("TYM6", "US 10Y Treasury Note Fut Jun26", "25.55%"),
            ("ESM6", "S&P 500 E-mini Fut Jun26", "9.97%"),
        ],
        "perf": [
            ("YTD", "-2.88%", "-3.24%"),
            ("1 個月", "-8.28%", "-8.72%"),
            ("3 個月", "-2.88%", "-3.24%"),
            ("6 個月", "0.00%", "-0.18%"),
            ("1 年", "20.72%", "20.05%"),
            ("成立以來", "16.82%", "16.67%"),
        ],
        "benchmark": {
            "headers": ["期間", "RSSB NAV", "全球股票", "美國公債", "100/100 組合"],
            "rows": [
                ("3 個月", "-2.88%", "-2.74%", "-0.04%", "-3.66%"),
                ("6 個月", "-0.04%", "0.41%", "0.86%", "-0.63%"),
                ("1 年", "20.67%", "20.75%", "3.25%", "19.72%"),
                ("成立以來", "16.77%", "17.71%", "4.15%", "17.05%"),
            ],
            "note": "100/100 組合 ＝ 100% 全球股 ＋ 100% 美債期貨梯 － 100% 融資腿（國庫券）。截至 2026-03-31，摘自 Q1 2026 Commentary。",
        },
        "backtest": {
            "period": "2002-12-31 ～ 2024-12-31",
            "years": 22,
            "note": "100/100 組合同 Product Brief / Presentation。指數毛費用、稅前；你不能投資指數。",
            "stats": [
                ("全球股票", "8.8%", "15.7%", None),
                ("美國債券", "3.1%", "4.3%", None),
                ("現金（T-Bills）", "1.6%", "0.5%", None),
                ("100/100（Return Stacked 組合）", "10.4%", "16.1%", None),
            ],
            "highlight": "100/100（Return Stacked 組合）",
        },
        "corr": None,
        "risks": ["衍生品／槓桿", "債券利率", "匯率", "海外市場", "非分散", "標的 ETF 雙重費用", "新基金"],
        "tim_note": "Tim Wei 實驗的核心地基。目前部位表可見 RSSB 持倉與占比變化。",
    },
    "rsst": {
        "tagline": "底下全倉大盤美股，上面再疊一層會做多也會做空的管理期貨趨勢策略。",
        "layers": [
            ("第一層 · 美國股票 100%", "大型股美國股市（SPYM 等），追蹤 S&P 500 類曝險。"),
            ("第二層 · 管理期貨 100%", "27 種期貨（商品、匯率、利率、股指），以 Top-Down + Bottom-Up 混合複製 CTA 趨勢類別。"),
        ],
        "why": [
            "⚖️ <strong>「美股 beta」與「管理期貨 alpha」雙管齊下</strong>：底倉 100% 配置<strong>美國大盤股票</strong>（S&P 500），確保能完全參與美股長期向上的經濟成長紅利。同時疊加 100% 的<strong>管理期貨趨勢</strong>（Trend-following）策略，在不同的總體經濟週期與大波動中尋求非對稱的絕對回報。",
            "🛡️ <strong>危機阿爾法（Crisis Alpha）的分散效果</strong>：歷史上，CTA 趨勢策略在股市發生大跌、系統性危機或高通膨環境下（如 2008 年、2022 年），往往能透過做空股指、做多商品/美元等方式獲取正報酬，提供與股票市場<strong>極佳的互補性與下檔防護</strong>。",
            "⚡ <strong>無痛升級投資組合</strong>：只要將現有投資組合中的 20% 美股部位賣掉，改為配置 20% 的 RSST，即可在「<strong>不減少美股曝險</strong>」的同時，無額外資金負擔地在資產組合中<strong>疊加 20% 的管理期貨趨勢策略</strong>，實現真正的資金解耦。",
            "📈 <strong>高精準度的官方模型複製</strong>：此策略並非主觀交易，而是透過量化模型複製官方管理期貨趨勢指數。截至 2026 年 Q1 季報，複製模型 3 年日相關係數高達 <strong>0.84</strong>，追蹤誤差控制在 <strong>5.4%</strong>，展現穩健的複製能力。"
        ],
        "fund": {
            "inception": "2023-09-06",
            "holdings": "28",
            "expense_gross": "0.99%",
            "expense_net": "0.99%",
            "expense_note": "",
            "sec_yield": "0.38%",
            "exchange": "CBOE",
        },
        "holdings": [
            ("SPYM", "SPDR Portfolio S&P 500", "74.89%"),
            ("ESM6", "S&P 500 E-mini Fut Jun26", "24.39%"),
            ("ADM6", "AUD/USD Currency Fut Jun26", "10.46%"),
            ("Z M6", "FTSE 100 Index Fut Jun26", "8.21%"),
            ("GCM6", "Gold 100 oz Fut Jun26", "4.17%"),
            ("PTM6", "S&P/TSX 60 Fut Jun26", "3.70%"),
            ("NXM6", "Nikkei 225 Fut Jun26", "2.60%"),
            ("XBK6", "Gasoline RBOB Fut May26", "1.63%"),
            ("VGM6", "Euro STOXX 50 Jun26", "1.40%"),
            ("HOK6", "NY Harbor ULSD Fut May26", "1.34%"),
        ],
        "perf": [
            ("YTD", "0.09%", "-0.25%"),
            ("1 個月", "-7.65%", "-7.88%"),
            ("3 個月", "0.09%", "-0.25%"),
            ("6 個月", "8.12%", "8.06%"),
            ("1 年", "29.63%", "29.43%"),
            ("成立以來", "15.42%", "15.38%"),
        ],
        "benchmark": {
            "headers": ["期間", "RSST NAV", "美國股票", "官方管理期貨指數", "100/100 組合"],
            "rows": [
                ("3 個月", "0.09%", "-4.33%", "7.11%", "1.48%"),
                ("6 個月", "8.09%", "-1.79%", "12.21%", "7.83%"),
                ("1 年", "29.59%", "17.80%", "15.04%", "29.50%"),
                ("成立以來", "15.39%", "17.17%", "3.18%", "14.95%"),
            ],
            "note": "100/100 組合 ＝ 100% 美股 ＋ 100% 官方管理期貨指數 － 100% 融資腿（國庫券）。截至 2026-03-31。",
        },
        "backtest": {
            "period": "1999-12-31 ～ 2025-12-31",
            "years": 26,
            "note": "100% 美股 / 100% CTA Trend / -100% T-Bills，每日再平衡。摘自 Presentation「Stacking in Action」。",
            "stats": [
                ("美國股票（SPX）", "8.1%", "15.3%", "-50.91%"),
                ("管理期貨指數", "5.4%", "13.3%", "-20.74%"),
                ("短期國庫券", "1.9%", "0.6%", "-0.01%"),
                ("美股＋管理期貨（Return Stacked）", "12.0%", "18.9%", "-40.30%"),
            ],
            "highlight": "美股＋管理期貨（Return Stacked）",
        },
        "regimes": {
            "headers": ["市場環境", "美國股票", "管理期貨", "Return Stacked"],
            "rows": [
                ("熊市月份（約 17%）", "-25.1%", "16.5%", "-7.2%"),
                ("牛市月份（約 83%）", "23.9%", "2.0%", "16.3%"),
                ("全期間", "8.1%", "5.4%", "12.0%"),
            ],
            "note": "依官方定義之 equity regime 分段年化報酬。",
        },
        "replication": {
            "headers": ["複製子模型", "日相關（vs 官方管理期貨指數）", "追蹤誤差"],
            "rows": [
                ("Top Down #1", "0.63", "9.4%"),
                ("Top Down #2", "0.72", "6.7%"),
                ("Bottom Up", "0.82", "6.9%"),
                ("Blend（15/15/70）", "0.84", "5.4%"),
            ],
            "note": "模型上線 3 年回顧（至 2026-02-07），RSST／RSBT 共用管理期貨複製框架。",
        },
        "corr": [
            ("", "美股", "美債", "CTA 趨勢"),
            ("美股", "1.00", "-0.15", "0.12"),
            ("美債", "-0.15", "1.00", "0.01"),
            ("CTA 趨勢", "0.12", "0.01", "1.00"),
        ],
        "risks": ["衍生品／槓桿", "開曼子基金", "商品池監管", "商品／匯率", "非分散", "新基金"],
        "tim_note": "Tim Wei 實驗有配置 RSST，與 RSSB、RSSY、RSIT 搭配使用。",
    },
    "rssy": {
        "tagline": "100% 美股 ＋ 100% 跨資產期貨 Carry（展期收益）策略。",
        "layers": [
            ("第一層 · 美國股票 100%", "大型股美國股市曝險。"),
            ("第二層 · 期貨 Carry 100%", "系統化在多商品、匯率、債券、股指期貨上做多／做空，收割 roll yield。"),
        ],
        "why": [
            "💰 <strong>獨特的期貨展期收益（Carry）策略</strong>：底倉為 100% 美國大盤股。第二層則配置 100% 期貨展期收益（Carry）策略。Carry 策略透過系統化地在多商品、匯率、債券、股指期貨上，做多「近月價格低於遠月」的標的、並做空相反標的，藉此<strong>穩定收割展期折溢價（Roll Yield）</strong>。",
            "🔗 <strong>多重分散化利器</strong>：歷史上，期貨 Carry 策略與股票、債券市場皆呈現<strong>極低的相關性</strong>，甚至與傳統的趨勢追蹤（CTA/Trend）策略也是低相關。這為投資組合引入了另一種<strong>完全獨立的收益來源</strong>（Risk Premia），有效降低組合波動。",
            "⛅ <strong>牛市與盤整市的額外助力</strong>：相較於需要市場有明顯大趨勢才能賺錢的 CTA 策略，Carry 策略在市場波動較低、價格盤整或溫和走牛的環境下，往往能透過合約結構穩定賺取利差與時間價值，為投資組合提供<strong>持續的現金流支持</strong>。",
            "⚡ <strong>提高資本效率</strong>：透過將現有 20% 的美股部位轉換為 RSSY，投資人能在完全不犧牲任何美股長期上漲機會的前題下，在投資組合中<strong>額外疊加 20% 的展期收益策略</strong>，極大地提升了整體資金的獲利效率。"
        ],
        "fund": {
            "inception": "2024-05-29",
            "holdings": "—",
            "expense_gross": "0.98%",
            "expense_net": "0.98%",
            "expense_note": "截至 2026 Q1 Commentary 總年化費用率為 0.98%",
            "sec_yield": "—",
            "exchange": "CBOE",
        },
        "holdings": [],
        "perf": [
            ("YTD", "15.51%", "15.85%"),
            ("1 個月", "—", "—"),
            ("3 個月", "15.51%", "15.85%"),
            ("6 個月", "13.24%", "12.80%"),
            ("1 年", "27.41%", "27.45%"),
            ("成立以來", "7.32%", "7.08%"),
        ],
        "benchmark": {
            "headers": ["期間", "RSSY NAV", "美股", "短期美債"],
            "rows": [
                ("3 個月", "15.51%", "-4.33%", "0.88%"),
                ("6 個月", "13.24%", "-1.79%", "1.90%"),
                ("1 年", "27.41%", "17.80%", "4.13%"),
                ("成立以來", "7.32%", "13.38%", "4.50%"),
            ],
            "note": "截至 2026-03-31，摘自 Q1 2026 Commentary。",
        },
        "corr": [
            ("", "美股", "美債", "期貨展期收益"),
            ("美股", "1.00", "-0.15", "0.01"),
            ("美債", "-0.15", "1.00", "0.04"),
            ("期貨展期收益", "0.01", "0.04", "1.00"),
        ],
        "risks": ["衍生品／槓桿", "開曼子基金", "商品池", "匯率", "非分散", "新基金"],
        "tim_note": "Tim Wei 實驗有配置 RSSY。",
    },

    "rsit": {
        "tagline": "100% 已開發市場國際股 ＋ 100% 管理期貨趨勢——RSST 的國際版。",
        "layers": [
            ("第一層 · 國際股票 100%", "已開發市場非北美大型／中型／小型股（S&P Developed ex-US BMI 相關）。"),
            ("第二層 · 管理期貨 100%", "與 RSST 相同複製框架：27 期貨、Top-Down + Bottom-Up 混合。"),
        ],
        "why": [
            "🗺️ <strong>全球化資產配置的拼圖</strong>：對於想要<strong>分散美股集中度風險</strong>的投資人，RSIT 底倉提供 100% 的<strong>已開發市場非美股票曝險</strong>（涵蓋歐洲、亞太等發達國家中大型企業）。這有助於補齊全球化配置中非美股票的核心基本盤。",
            "🛡️ <strong>多重分散效應與危機保護</strong>：第二層配置 100% 管理期貨趨勢策略。歷史上，已開發國家非美股市的波動與跌幅往往高於美股，透過管理期貨在股市大跌時做空股指、做多防禦性資產，能為國際股部位提供寶貴的 <strong>Crisis Alpha 避險收益</strong>。",
            "⚡ <strong>高資本效率分散投資</strong>：如果你原本的投資組合中配置了 20% 的非美開發市場股票，只要將其改買 20% 的 RSIT，即可在「<strong>非美股票曝險不變</strong>」的同時，無痛地在資產組合中疊加 20% 的管理期貨策略，<strong>完美釋放資金</strong>。",
            "📈 <strong>精準追蹤官方管理期貨指標</strong>：與 RSST 採用相同的複製框架，截至 2026 年 Q1 季報，複製模型 3 年日相關高達 <strong>0.84</strong>，追蹤誤差控制在 <strong>5.4%</strong>，是一套成熟且經過市場驗證的量化交易系統。"
        ],
        "fund": {
            "inception": "2026-05-07",
            "holdings": "28",
            "expense_gross": "0.98%",
            "expense_net": "0.98%",
            "expense_note": "2026 Q2 新標的；掛牌日依 Tim Wei 實驗紀錄",
            "sec_yield": "—",
            "exchange": "CBOE",
        },
        "holdings": [],
        "perf": [],
        "backtest": {
            "period": "1999-12-31 ～ 2025-12-31",
            "years": 26,
            "note": "100% 國際股 / 100% CTA Trend / -100% T-Bills。摘自 RSIT Presentation。",
            "stats": [
                ("國際股票（MSCI EAFE）", "4.5%", "16.5%", "-56.68%"),
                ("管理期貨指數", "5.4%", "13.3%", "-20.74%"),
                ("短期國庫券", "1.9%", "0.6%", "-0.01%"),
                ("國際股＋管理期貨（Return Stacked）", "8.2%", "20.4%", "-47.46%"),
            ],
            "highlight": "國際股＋管理期貨（Return Stacked）",
        },
        "regimes": {
            "headers": ["市場環境", "國際股票", "管理期貨", "Return Stacked"],
            "rows": [
                ("熊市月份（約 17%）", "-24.3%", "15.0%", "-13.3%"),
                ("牛市月份（約 83%）", "15.7%", "2.5%", "15.6%"),
                ("全期間", "4.5%", "5.4%", "8.2%"),
            ],
            "note": "依官方定義之 equity regime 分段年化報酬。",
        },
        "replication": {
            "headers": ["複製子模型", "日相關（vs 官方管理期貨指數）", "追蹤誤差"],
            "rows": [
                ("Top Down #1", "0.63", "9.4%"),
                ("Top Down #2", "0.72", "6.7%"),
                ("Bottom Up", "0.82", "6.9%"),
                ("Blend（15/15/70）", "0.84", "5.4%"),
            ],
            "note": "與 RSST 相同之管理期貨複製框架（Q1 2026 Commentary）。",
        },
        "corr": [
            ("", "國際股", "美債", "管理期貨"),
            ("國際股", "1.00", "0.20", "-0.07"),
            ("美債", "0.20", "1.00", "0.01"),
            ("管理期貨", "-0.07", "0.01", "1.00"),
        ],
        "risks": ["衍生品／槓桿", "開曼子基金", "海外市場", "匯率", "非分散", "新基金"],
        "tim_note": "Tim Wei 實驗有配置 RSIT。",
    },
    "rssx": {
        "tagline": "100% 美股 ＋ 100% 黃金／比特幣——依 63 日波動做風險平價，每月再平衡。",
        "layers": [
            ("第一層 · 美國股票 100%", "大型股美國股市（SPYM 等）。"),
            ("第二層 · 黃金＋比特幣 100%", "透過黃金／比特幣期貨與 ETF（如 IBIT），讓兩者風險貢獻盡量相等；波動大者降權。"),
        ],
        "why": [
            "傳統美股與另類硬資產（Hard Assets）的結合：底倉配置 100% 美國大盤股。第二層則配置 100% 黃金＋比特幣。黃金與比特幣（被譽為數位黃金）作為另類貨幣與硬資產，在抗通膨、反法幣貶值以及防範總體信用危機方面，能發揮與傳統股債完全不同的保護與回報作用。",
            "風險平價（Risk Parity）動態權重調配：第二層並非簡單 of 50/50 分配，而是透過風險平價模型，根據兩者的歷史波動率動態調整配置權重，確保兩者對投資組合的風險貢獻基本相等。這可以有效降低因單一高波動資產（如比特幣）暴跌而對整體組合造成的巨大衝擊。",
            "極低相關性的多重多元化：歷史上，黃金與美股的相關性僅約 0.09，而比特幣與美股的相關性約為 0.23。這種極低的相關性使得第二層另類硬資產在美股回檔時，能產生優秀的分散風險效果，平滑資產淨值波動。",
            "一檔滿足所有防護與增值需求：適合想要在投資組合中加入黃金與比特幣等新世代資產，卻又不想自行開戶、調倉或承受實物存儲安全風險的投資人。投資人只需賣掉 20% 美股改買 RSSX，即可無痛擁有這兩種強大的另類資產。"
        ],
        "fund": {
            "inception": "2025-05-29",
            "holdings": "5",
            "expense_gross": "0.68%",
            "expense_net": "0.68%",
            "expense_note": "",
            "sec_yield": "0.41%",
            "exchange": "CBOE",
        },
        "holdings": [
            ("SPYM", "SPDR Portfolio S&P 500", "68.40%"),
            ("MGCM6", "Micro Gold Fut Jun26", "65.28%"),
            ("HWAM6", "Micro E-mini S&P Fut Jun26", "29.31%"),
            ("BTCJ6", "CME Bitcoin Fut Apr26", "24.89%"),
            ("IBIT", "iShares Bitcoin Trust", "7.26%"),
        ],
        "perf": [
            ("YTD", "-8.35%", "-7.94%"),
            ("1 個月", "-12.29%", "-12.18%"),
            ("3 個月", "-8.35%", "-7.94%"),
            ("6 個月", "-6.10%", "-6.20%"),
            ("成立以來", "18.54%", "18.93%"),
        ],
        "benchmark": {
            "headers": ["期間", "RSSX NAV", "美股", "U.S. T-Bills"],
            "rows": [
                ("3 個月", "-8.35%", "-4.33%", "0.88%"),
                ("6 個月", "-6.10%", "-1.79%", "1.90%"),
                ("成立以來", "18.54%", "11.59%", "—"),
            ],
            "note": "RSSX 成立較晚；部分基準期間摘自 Q1 2026 Commentary。",
        },
        "corr": [
            ("", "美股", "黃金", "比特幣"),
            ("美股", "1.00", "0.09", "0.23"),
            ("黃金", "0.09", "1.00", "0.12"),
            ("比特幣", "0.23", "0.12", "1.00"),
        ],
        "backtest": {
            "period": "2017-12-31 ～ 2024-12-31",
            "years": 7,
            "note": "Gold/Bitcoin 依 63 日波動逆權重每月再平衡；比特幣融資成本假設 +1000bp。",
            "stats": [],
            "highlight": None,
        },
        "risks": ["比特幣高度波動", "數位資產監管", "黃金期貨", "衍生品／槓桿", "非分散", "新基金"],
        "tim_note": "Tim Wei 實驗目前尚未配置 RSSX，但已準備相關說明貼文。",
    },
    "rsbt": {
        "tagline": "100% 美國債券 ＋ 100% 管理期貨趨勢——在債券底層上疊 CTA。",
        "layers": [
            ("第一層 · 美國債券 100%", "廣義美國固定收益（SPAB 等）＋公債期貨。"),
            ("第二層 · 管理期貨 100%", "與 RSST 相同的趨勢複製策略。"),
        ],
        "why": [
            "💵 <strong>傳統固定收益的增強版</strong>：底倉提供 100% 廣義美國綜合債券曝險（追蹤彭博美國綜合債券指數），作為資產配置 of 防禦與收息基石。第二層則配置 100% 管理期貨趨勢策略。管理期貨在商品、外匯、股指與利率市場中多空雙向靈活操作，為保守的債券組合<strong>注入動態增值的生命力</strong>。",
            "💥 <strong>降低股債同跌的風險</strong>：在像 2022 年那樣股債雙殺的高通膨環境中，傳統的股債平衡組合會失效。但 RSBT 疊加的管理期貨策略在此類趨勢明顯的市場環境中，往往能大放異彩（例如放空債券期貨與放空股票期貨），<strong>有效對沖債券利差走寬與利率上升的損失</strong>。",
            "⚡ <strong>無痛解放債券資金</strong>：投資人只需賣掉 20% 的債券部位改買 20% 的 RSBT，即可在「<strong>完全保留 20% 債券利息與曝險</strong>」的同時，無額外成本地在資產組合中新增 20% 的管理期貨策略，大幅優化資產配置彈性。",
            "📈 <strong>Return Stacked 系列的元老級奠基者</strong>：作為該系列最早於 2023 年初成立的代表性標的，擁有更長久的實盤運行紀錄與高穩健的模型複製度。截至 2026 Q1 季報，複製模型 3 年日相關高達 <strong>0.84</strong>，追蹤誤差控制在 <strong>5.4%</strong>。"
        ],
        "fund": {
            "inception": "2023-02-06",
            "holdings": "28",
            "expense_gross": "1.02%",
            "expense_net": "1.02%",
            "expense_note": "",
            "sec_yield": "2.32%",
            "exchange": "CBOE",
        },
        "holdings": [
            ("SPAB", "SPDR Portfolio Aggregate Bond", "74.86%"),
            ("ADM6", "AUD/USD Currency Fut Jun26", "10.71%"),
            ("Z M6", "FTSE 100 Index Fut Jun26", "8.41%"),
            ("USM6", "US Long Bond Fut Jun26", "4.81%"),
            ("GCM6", "Gold 100 oz Fut Jun26", "4.35%"),
            ("PTM6", "S&P/TSX 60 Fut Jun26", "3.70%"),
            ("NXM6", "Nikkei 225 Fut Jun26", "2.69%"),
            ("XBK6", "Gasoline RBOB Fut May26", "1.71%"),
            ("HOK6", "NY Harbor ULSD Fut May26", "1.46%"),
            ("VGM6", "Euro STOXX 50 Jun26", "1.45%"),
        ],
        "perf": [
            ("YTD", "4.91%", "5.19%"),
            ("1 個月", "-4.53%", "-4.56%"),
            ("3 個月", "4.91%", "5.19%"),
            ("6 個月", "11.74%", "11.56%"),
            ("1 年", "15.96%", "14.71%"),
            ("3 年", "2.99%", "2.92%"),
            ("成立以來", "-0.15%", "-0.15%"),
        ],
        "benchmark": {
            "headers": ["期間", "RSBT NAV", "美國債券", "官方管理期貨指數", "100/100 組合"],
            "rows": [
                ("3 個月", "4.91%", "-0.05%", "7.11%", "6.15%"),
                ("6 個月", "11.66%", "1.05%", "12.21%", "11.30%"),
                ("1 年", "15.87%", "4.35%", "15.04%", "15.23%"),
                ("3 年", "2.98%", "3.63%", "5.19%", "4.10%"),
                ("成立以來", "-0.17%", "3.71%", "3.18%", "2.24%"),
            ],
            "note": "100/100 組合 ＝ 100% 美債 ＋ 100% 官方管理期貨指數 － 100% 融資腿（國庫券）。截至 2026-03-31。",
        },
        "replication": {
            "headers": ["複製子模型", "日相關（vs 官方管理期貨指數）", "追蹤誤差"],
            "rows": [
                ("Top Down #1", "0.63", "9.4%"),
                ("Top Down #2", "0.72", "6.7%"),
                ("Bottom Up", "0.82", "6.9%"),
                ("Blend（15/15/70）", "0.84", "5.4%"),
            ],
            "note": "與 RSST 共用管理期貨複製框架。",
        },
        "corr": [
            ("", "美股", "美債", "管理期貨"),
            ("美股", "1.00", "0.13", "-0.13"),
            ("美債", "0.13", "1.00", "0.01"),
            ("管理期貨", "-0.13", "0.01", "1.00"),
        ],
        "risks": ["衍生品／槓桿", "利率", "開曼子基金", "商品池", "非分散"],
        "tim_note": "Tim Wei 實驗目前未配置 RSBT（債券底層變體）。",
    },
    "rsby": {
        "tagline": "100% 美國債券 ＋ 100% 跨資產期貨 Carry——RSBY 是 RSSY 的債券底層版。",
        "layers": [
            ("第一層 · 美國債券 100%", "廣義美國固定收益市場。"),
            ("第二層 · 期貨 Carry 100%", "多資產 roll yield 策略，與 RSSY 第二層邏輯相同。"),
        ],
        "why": [
            "🛡️ <strong>防守核心與多資產利差（Carry）策略</strong>：底倉提供 100% 美國綜合債券曝險，建立穩健的收息與防禦基石。第二層配置 100% 期貨展期收益（Carry）策略。Carry 策略透過系統化捕捉多商品、匯率、債券、股指期貨中因到期期限結構帶來的利差（Roll Yield），為債券組合提供多樣化的收益。",
            "🔀 <strong>獨立於趨勢的收益來源</strong>：與依賴價格大趨勢的 CTA/Trend 策略不同，期貨 Carry 策略即便在市場沒有明顯趨勢、呈現橫盤整理或低波動的環境下，仍能透過合約利差帶來穩定的回報。與股債的相關性極低，可<strong>進一步平滑淨值波動</strong>。",
            "⚡ <strong>解決「減債配置」的兩難困境</strong>：傳統配置中若要為資產組合加入另類利差收益，就必須縮減債券的基本配置。使用 RSBY 後，投資人只需賣出原先 20% 的債券改買 RSBY，即可在「<strong>1:1 完全保留 20% 債券曝險與利息</strong>」的同時，無痛疊加 20% 的另類 Carry 策略。",
            "📉 <strong>低波動多資產互補</strong>：結合了債券的穩定配息特徵，與 Carry 策略的低相關阿爾法，使 RSBY 成為防守型投資人尋求在低風險環境下提升整體資本效率與分散風險的<strong>理想標的</strong>。"
        ],
        "fund": {
            "inception": "2024-08-20",
            "holdings": "28",
            "expense_gross": "0.98%",
            "expense_net": "0.98%",
            "expense_note": "",
            "sec_yield": "1.79%",
            "exchange": "CBOE",
        },
        "holdings": [
            ("SPAB", "SPDR Portfolio Aggregate Bond", "75.67%"),
            ("BPM6", "BP Currency Fut Jun26", "40.72%"),
            ("FVM6", "US 5Y Treasury Note Fut Jun26", "33.90%"),
            ("ADM6", "AUD/USD Currency Fut Jun26", "31.54%"),
            ("TYM6", "US 10Y Treasury Note Fut Jun26", "25.18%"),
            ("USM6", "US Long Bond Fut Jun26", "16.09%"),
            ("TUM6", "US 2Y Treasury Note Fut Jun26", "6.40%"),
            ("XBK6", "Gasoline RBOB Fut May26", "6.39%"),
            ("COM6", "Brent Crude Fut Jun26", "3.09%"),
            ("HOK6", "NY Harbor ULSD Fut May26", "3.08%"),
        ],
        "perf": [
            ("YTD", "20.60%", "20.80%"),
            ("1 個月", "10.48%", "10.18%"),
            ("3 個月", "20.60%", "20.80%"),
            ("6 個月", "16.06%", "16.00%"),
            ("1 年", "11.92%", "11.34%"),
            ("成立以來", "-1.77%", "-1.85%"),
        ],
        "benchmark": {
            "headers": ["期間", "RSBY NAV", "美債", "短期美債"],
            "rows": [
                ("3 個月", "20.60%", "-0.05%", "0.88%"),
                ("6 個月", "16.09%", "1.05%", "1.90%"),
                ("1 年", "11.95%", "4.35%", "4.13%"),
                ("成立以來", "-1.76%", "3.10%", "4.35%"),
            ],
            "note": "截至 2026-03-31，摘自 Q1 2026 Commentary。",
        },
        "corr": [
            ("", "美股", "美債", "期貨展期收益"),
            ("美股", "1.00", "-0.15", "0.01"),
            ("美債", "-0.15", "1.00", "0.04"),
            ("期貨展期收益", "0.01", "0.04", "1.00"),
        ],
        "risks": ["衍生品／槓桿", "利率", "開曼子基金", "商品池", "非分散", "新基金"],
        "tim_note": "Tim Wei 實驗目前未配置 RSBY。",
    },
    "rsba": {
        "tagline": "100% 美國公債 ＋ 100% 併購套利——在債券底層上疊事件驅動型策略。",
        "layers": [
            ("第一層 · 美國公債 100%", "美國公債期貨／相關曝險。"),
            ("第二層 · 併購套利 100%", "被動追蹤併購套利指數，投資已公告併購案的多空組合。"),
        ],
        "why": [
            "🤝 <strong>穩健美債與事件驅動（Event-Driven）的巧妙融合</strong>：底倉提供 100% 美國公債曝險，作為無風險防禦與收益的定海神針。第二層則配置 100% 併購套利（Merger Arbitrage）策略。透過買入已公告被收購公司的股票、並同時賣出收購方股票，穩定賺取因「併購交易未最終完成」而存在的<strong>收購溢價差額</strong>。",
            "🎯 <strong>近乎股票但低相關的絕對回報</strong>：併購套利本質上是事件驅動型投資，其回報主要取決於「交易是否順利完成」，而非股票市場的牛熊大勢。因此，歷史上該策略與股票市場的相關性極低，與美債相關性也僅約 -0.02，為投資組合提供<strong>極佳的分散度</strong>。",
            "⛱️ <strong>牛市之外的防護傘與抗跌性</strong>：在股市發生大跌或新興熊市環境中，併購案的完成機率雖然可能受總體環境影響，但歷史上該策略的波動與最大回撤均遠低於大盤股市，甚至在多數歷史回檔期均<strong>表現出極強的抗跌性與正收益能力</strong>。",
            "⚡ <strong>提高債券部位的資本增值潛力</strong>：傳統債券投資人往往面臨收益率受限的問題。透過將 20% 的債券轉換為 RSBA，能在「<strong>1:1 完全維持 20% 債券曝險</strong>」的前提下，免費疊加 20% 的併購套利策略，為保守配置部位注入潛在的絕對回報增量。"
        ],
        "fund": {
            "inception": "2024-12-17",
            "holdings": "—",
            "expense_gross": "0.96%",
            "expense_net": "0.96%",
            "expense_note": "截至 2026 Q1 Commentary 總年化費用率為 0.96%",
            "sec_yield": "—",
            "exchange": "CBOE",
        },
        "holdings": [],
        "perf": [
            ("YTD", "-0.67%", "-0.50%"),
            ("1 個月", "—", "—"),
            ("3 個月", "-0.67%", "-0.50%"),
            ("6 個月", "0.58%", "0.51%"),
            ("1 年", "4.18%", "3.99%"),
            ("成立以來", "5.58%", "5.60%"),
        ],
        "benchmark": {
            "headers": ["期間", "RSBA NAV", "美債", "併購套利指數"],
            "rows": [
                ("3 個月", "-0.67%", "-0.04%", "0.57%"),
                ("6 個月", "0.58%", "0.86%", "2.12%"),
                ("1 年", "4.18%", "3.25%", "6.22%"),
                ("成立以來", "5.58%", "4.27%", "5.96%"),
            ],
            "note": "併購套利為 AlphaBeta Merger Arbitrage Index。截至 2026-03-31。",
        },
        "corr": [
            ("", "美債", "公司債", "併購套利"),
            ("美債", "1.00", "0.64", "-0.02"),
            ("公司債", "0.64", "1.00", "0.29"),
            ("併購套利", "-0.02", "0.29", "1.00"),
        ],
        "risks": ["併購失敗／延遲", "槓桿", "高換手", "指數策略", "做空", "非分散", "新基金"],
        "tim_note": "Tim Wei 實驗目前未配置 RSBA。",
    },
}


def esc(text: str) -> str:
    return html.escape(str(text), quote=True)


LAYER2_PHRASE_LINKS: tuple[tuple[str, str], ...] = (
    ("黃金＋比特幣（風險平價）", "gold-bitcoin"),
    ("管理期貨（趨勢追蹤）", "managed-futures"),
    ("期貨展期收益策略", "futures-carry"),
    ("期貨展期收益", "futures-carry"),
    ("展期收益策略", "futures-carry"),
    ("管理期貨趨勢", "managed-futures"),
    ("管理期貨", "managed-futures"),
    ("趨勢追蹤", "managed-futures"),
    ("展期收益", "futures-carry"),
    ("黃金比特幣", "gold-bitcoin"),
    ("併購套利", "merger-arb"),
    ("美國公債", "us-bonds"),
)

ALL_ETF_TICKERS: tuple[str, ...] = tuple(r[0] for r in SUITE_ROWS)


def layer2_href(key: str, prefix: str = "", *, same_page: bool = False) -> str:
    anchor = f"#layer2-{key}"
    if same_page:
        return anchor
    return f"{prefix}layer2.html{anchor}"


LAYER2_STACK_TOP = (
    "us-bonds",
    "managed-futures",
    "futures-carry",
    "merger-arb",
    "gold-bitcoin",
)


def link_etf(ticker: str, prefix: str = "", *, link_class: str = "guide-text-link") -> str:
    cls = f' class="{link_class}"' if link_class else ""
    return f'<a href="{prefix}etfs/{ticker.lower()}.html"{cls}>{esc(ticker)}</a>'


def link_layer2_key(
    key: str,
    label: str | None = None,
    prefix: str = "",
    *,
    same_page: bool = False,
    link_class: str = "guide-text-link",
) -> str:
    text = label or LAYER2_STRATEGIES[key]["title"]
    cls = f' class="{link_class}"' if link_class else ""
    return f'<a href="{layer2_href(key, prefix, same_page=same_page)}"{cls}>{esc(text)}</a>'


def link_layer2_stack(
    stack_label: str,
    prefix: str = "",
    *,
    same_page: bool = False,
    link_class: str = "guide-text-link",
) -> str:
    key = layer2_strategy_key(stack_label)
    if key:
        cls = f' class="{link_class}"' if link_class else ""
        return f'<a href="{layer2_href(key, prefix, same_page=same_page)}"{cls}>{esc(stack_label)}</a>'
    return esc(stack_label)


def render_layer2_stack_tags(
    prefix: str = "",
    *,
    same_page: bool = False,
    keys: tuple[str, ...] = LAYER2_STACK_TOP,
) -> str:
    tags = [
        f'<a class="guide-stack-tag" href="{layer2_href(key, prefix, same_page=same_page)}">'
        f"{T(f'layer2.{key}.title', LAYER2_STRATEGIES[key]['title'], layer2_en(key, 'title', LAYER2_STRATEGIES[key]['title']))}</a>"
        for key in keys
    ]
    return f'<span class="guide-stack-tags">{"".join(tags)}</span>'


def render_layer2_inline_tags(
    prefix: str = "",
    *,
    same_page: bool = False,
    keys: tuple[str, ...] = LAYER2_ORDER,
) -> str:
    tags = [
        f'<a class="guide-inline-tag" href="{layer2_href(key, prefix, same_page=same_page)}">'
        f"{T(f'layer2.{key}.title', LAYER2_STRATEGIES[key]['title'], layer2_en(key, 'title', LAYER2_STRATEGIES[key]['title']))}</a>"
        for key in keys
    ]
    return f'<span class="guide-inline-tags">{"".join(tags)}</span>'


def linkify_guide_text(
    text: str,
    *,
    prefix: str = "",
    same_page: bool = False,
    skip_key: str | None = None,
) -> str:
    spans: list[tuple[int, int, str]] = []
    for phrase, key in LAYER2_PHRASE_LINKS:
        if skip_key and key == skip_key:
            continue
        for match in re.finditer(re.escape(phrase), text):
            spans.append(
                (
                    match.start(),
                    match.end(),
                    f'<a class="guide-text-link" href="{layer2_href(key, prefix, same_page=same_page)}">{esc(phrase)}</a>',
                )
            )
    for ticker in ALL_ETF_TICKERS:
        for match in re.finditer(rf"\b{re.escape(ticker)}\b", text):
            spans.append((match.start(), match.end(), link_etf(ticker, prefix)))
    spans.sort(key=lambda item: (item[0], -(item[1] - item[0])))
    merged: list[tuple[int, int, str]] = []
    for span in spans:
        start, end, chunk = span
        if merged and start < merged[-1][1]:
            continue
        merged.append(span)
    if not merged:
        return esc(text)
    parts: list[str] = []
    pos = 0
    for start, end, chunk in merged:
        if start > pos:
            parts.append(esc(text[pos:start]))
        parts.append(chunk)
        pos = end
    if pos < len(text):
        parts.append(esc(text[pos:]))
    return "".join(parts)


def render_layer2_inline_links(prefix: str = "", *, same_page: bool = False) -> str:
    return render_layer2_inline_tags(prefix, same_page=same_page)


def render_suite_table_rows(*, prefix: str = "") -> list[tuple]:
    rows = []
    for row in SUITE_ROWS:
        ticker, zh, en_name, base, stack, launch, aum, _tone, in_port = row
        slug = ticker.lower()
        rows.append(
            (
                esc(ticker),
                T(f"etf.{slug}.name", zh, en_name),
                T(f"etf.{slug}.base", base, BASE_EN.get(base, base)),
                T(f"etf.{slug}.stack", stack, STACK_EN.get(stack, stack)),
                esc(launch),
                esc(aum),
                "●" if tim_configured(row) else "—",
            )
        )
    return rows


def render_learn_suite_table_rows() -> list[tuple]:
    rows = []
    for row in SUITE_ROWS:
        ticker, zh, en_name, base, stack, _launch, _aum, _tone, in_port = row
        slug = ticker.lower()
        tim_key = "guide.table.tim.yes" if tim_configured(row) else "guide.table.tim.no"
        tim_zh = "有配置" if tim_configured(row) else "未配置"
        rows.append(
            (
                esc(ticker),
                T(f"etf.{slug}.name", zh, en_name),
                T(f"etf.{slug}.base", base, BASE_EN.get(base, base)),
                T(f"etf.{slug}.stack", stack, STACK_EN.get(stack, stack)),
                T(tim_key, tim_zh, ui_en(tim_key, tim_zh)),
            )
        )
    return rows


def render_layer2_map_table(*, prefix: str = "", same_page: bool = True) -> str:
    rows = []
    for key in LAYER2_ORDER:
        strategy = LAYER2_STRATEGIES[key]
        title = T(
            f"layer2.{key}.title",
            strategy["title"],
            layer2_en(key, "title", strategy["title"]),
        )
        etfs = "、".join(strategy["etfs"])
        summary = T(
            f"layer2.{key}.summary",
            strategy["summary"],
            layer2_en(key, "summary", strategy["summary"]),
        )
        rows.append((title, etfs, summary))
    return render_table(
        [
            ("guide.table.strategy", "第二層策略"),
            ("guide.table.etfs_using", "用到此策略的 ETF"),
            ("guide.table.what", "在做什麼"),
        ],
        rows,
        table_class="guide-table-suite",
        html_cells=True,
    )


def render_layer2_card_nav(key: str, prefix: str = "", *, same_page: bool = False) -> str:
    etfs = " · ".join(link_etf(ticker, prefix) for ticker in LAYER2_STRATEGIES[key]["etfs"])
    jump = "#layer2-jump-nav" if same_page else f"{prefix}layer2.html#layer2-jump-nav"
    return (
        f'<p class="guide-l2-card-nav">'
        f'<a class="guide-text-link" href="{jump}">↑ 策略捷徑</a> · '
        f"{etfs} · "
        f'<a class="guide-text-link" href="{prefix}etfs.html">ETF 百科</a> · '
        f'<span class="guide-l2-card-nav-others">其他 {render_layer2_inline_tags(prefix, same_page=same_page, keys=tuple(k for k in LAYER2_ORDER if k != key))}</span>'
        f"</p>"
    )


def nav(active: str, prefix: str = "") -> str:
    links = [
        ("overview", f"{prefix}index.html", "nav.overview", "實測總覽"),
        ("learn", f"{prefix}learn.html", "nav.learn", "認識實驗"),
        ("layer2", f"{prefix}layer2.html", "nav.layer2", "第二層策略"),
        ("etfs", f"{prefix}etfs.html", "nav.etfs", "ETF 百科"),
        ("details", f"{prefix}details.html#performance", "nav.details", "帳本明細"),
    ]
    parts = []
    for key, href, i18n_key, label in links:
        cls = "site-nav-link is-active" if key == active else "site-nav-link"
        aria = ' aria-current="page"' if key == active else ""
        parts.append(
            f'<a class="{cls}" href="{href}" data-i18n="{i18n_key}"{aria}>{esc(label)}</a>'
        )
    return "\n          ".join(parts)


def lang_switch_html() -> str:
    return """<div class="lang-switch" role="group" aria-label="Language">
            <button type="button" class="lang-switch-btn" data-set-lang="zh-Hant" data-i18n="nav.lang.zh">中文</button>
            <button type="button" class="lang-switch-btn" data-set-lang="en" data-i18n="nav.lang.en">EN</button>
          </div>"""


def favicon_head(*, prefix: str = "") -> str:
    return f'    <link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml" />\n'


def head(title: str, desc: str, page_id: str, *, title_en: str = "", desc_en: str = "") -> str:
    title_en = title_en or title
    desc_en = desc_en or desc
    register_i18n(f"meta.title.{page_id}", title, title_en)
    register_i18n(f"meta.desc.{page_id}", desc, desc_en)
    asset_prefix = "../" if page_id.startswith("etf-") else ""
    return f"""<!DOCTYPE html>
<html lang="zh-Hant" data-page="{esc(page_id)}" data-title-i18n="meta.title.{esc(page_id)}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
{favicon_head(prefix=asset_prefix)}    <title>{esc(title)}</title>
    <meta name="description" content="{esc(desc)}" />
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-P1F0YJSFDW"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag() {{ window.dataLayer.push(arguments); }}
      gtag("js", new Date());
      gtag("config", "G-P1F0YJSFDW", {{ anonymize_ip: true }});
    </script>
    <script src="{asset_prefix}site-config.js"></script>
    <script src="{asset_prefix}js/analytics.js"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;600;700&family=Noto+Serif+TC:wght@500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="{asset_prefix}styles.css?v={STYLES_VER}" />
    <link rel="stylesheet" href="{asset_prefix}guide.css?v={CSS_VER}" />
  </head>
"""


def shell_start(active: str, page_id: str) -> str:
    prefix = "../" if page_id.startswith("etf-") else ""
    nav_active = "etfs" if page_id.startswith("etf-") else active
    return f"""  <body class="guide-page">
    <div class="paper-noise" aria-hidden="true"></div>
    <div class="bg-orb bg-orb-1" aria-hidden="true"></div>
    <div class="bg-orb bg-orb-2" aria-hidden="true"></div>
    <div class="wrap">
      <nav class="site-nav" aria-label="Site navigation">
        <div class="brand-block">
          <span class="site-nav-brand" data-i18n="nav.brand">25歲貸款投資實錄</span>
          <a class="site-nav-title" href="{prefix}index.html" data-i18n="nav.title">Tim Wei 報酬疊加實驗</a>
        </div>
        <div class="site-nav-row">
          <div class="site-nav-links">
          {nav(nav_active, prefix)}
          </div>
          <div class="site-nav-actions">
            {lang_switch_html()}
          </div>
        </div>
      </nav>"""


def shell_end(page_id: str) -> str:
    prefix = "../" if page_id.startswith("etf-") else ""
    return f"""
      <div class="guide-footer-cta card">
        <div>
          <p class="section-kicker" data-i18n="guide.footer.kicker">下一步</p>
          <h2 data-i18n="guide.footer.title">學完概念，看 Tim Wei 的實測數據</h2>
          <p class="guide-lead" data-i18n="guide.footer.lead">總覽頁有 NAV、持倉、再平衡與貸款進度；細節可到帳本明細。想討論歡迎加入 FB 社團。</p>
        </div>
        <div class="guide-footer-actions">
          <a class="btn-primary" href="{prefix}index.html" data-i18n="guide.footer.overview">看實測總覽</a>
          <a class="btn-secondary" href="{prefix}details.html#performance" data-i18n="guide.footer.details">看帳本明細</a>
          <a class="btn-secondary guide-btn-fb" href="https://www.facebook.com/share/g/18vB1iMhcY/" target="_blank" rel="noopener" data-i18n="social.join_fb">加入 FB 交流社團</a>
        </div>
      </div>
    </div>
    <aside id="social-dock" class="social-dock" hidden aria-label="Community links"></aside>
    <script src="{prefix}locale.js?v={LOCALE_VER}"></script>
    <script src="{prefix}guide-locale.js?v={CSS_VER}"></script>
    <script src="{prefix}js/guide.js?v={JS_VER}"></script>
    <script src="{prefix}js/social-dock.js"></script>
  </body>
</html>"""


def render_table(
    headers: list[str] | list[tuple[str, str]],
    rows: list[tuple],
    *,
    compact: bool = False,
    table_class: str = "guide-table-num",
    html_cells: bool = False,
) -> str:
    wrap_cls = "table-wrap table-scroll guide-table-wrap"
    if compact:
        wrap_cls += " guide-table-compact"
    th_parts = []
    for item in headers:
        if isinstance(item, tuple):
            i18n_key, label = item
            register_i18n(i18n_key, label, ui_en(i18n_key, label))
            th_parts.append(f'<th data-i18n="{i18n_key}">{esc(label)}</th>')
        else:
            th_parts.append(f"<th>{esc(item)}</th>")
    th = "".join(th_parts)
    body = []
    for row in rows:
        if html_cells:
            tds = "".join(f"<td>{cell}</td>" for cell in row)
        else:
            tds = "".join(f"<td>{esc(c)}</td>" for c in row)
        body.append(f"<tr>{tds}</tr>")
    return f"""<div class="{wrap_cls}">
      <table class="quotes guide-table {table_class}">
        <thead><tr>{th}</tr></thead>
        <tbody>{"".join(body)}</tbody>
      </table>
    </div>"""


def render_spec_dl(rows: list[tuple[str, str]]) -> str:
    items = []
    for label, value in rows:
        items.append(
            f'<div class="guide-spec-row"><dt>{esc(label)}</dt><dd>{esc(value)}</dd></div>'
        )
    return f'<dl class="guide-spec-dl">{"".join(items)}</dl>'


def render_tim_allocation_section() -> str:
    def chip(ticker: str, slug: str, *, live: bool) -> str:
        cls = "guide-tim-chip guide-tim-chip-live" if live else "guide-tim-chip guide-tim-chip-ref"
        return f'<a class="{cls}" href="etfs/{slug}.html">{esc(ticker)}</a>'

    core = chip("RSSB", "rssb", live=True)
    overlay = "".join(
        chip(ticker, slug, live=True)
        for ticker, slug in (("RSST", "rsst"), ("RSSY", "rssy"), ("RSIT", "rsit"))
    )
    ref = "".join(
        chip(ticker, slug, live=False)
        for ticker, slug in (("RSSX", "rssx"), ("RSBT", "rsbt"), ("RSBY", "rsby"), ("RSBA", "rsba"))
    )
    return f"""<section class="card guide-card guide-tim-allocation">
        <p class="section-kicker" data-i18n="guide.etfs.tim.kicker">Tim Wei 的配置</p>
        <h2 data-i18n="guide.etfs.tim.title">目前實測用哪幾檔？</h2>
        <div class="guide-tim-groups">
          <div class="guide-tim-group">
            <p class="guide-tim-group-label" data-i18n="guide.etfs.tim.group.core">核心</p>
            <div class="guide-tim-chips">{core}</div>
          </div>
          <div class="guide-tim-group">
            <p class="guide-tim-group-label" data-i18n="guide.etfs.tim.group.overlay">疊加（實測有配）</p>
            <div class="guide-tim-chips">{overlay}</div>
          </div>
          <div class="guide-tim-group guide-tim-group-ref">
            <p class="guide-tim-group-label" data-i18n="guide.etfs.tim.group.ref">百科收錄、尚未配置</p>
            <div class="guide-tim-chips">{ref}</div>
          </div>
        </div>
        <p class="guide-note" data-i18n="guide.etfs.tim.note">配置比例與再平衡邏輯見實測總覽的策略拆解與帳本明細的配置明細。</p>
      </section>"""


def render_card_foot(*items: str) -> str:
    blocks = []
    for item in items:
        if not item or not str(item).strip():
            continue
        text = str(item).strip()
        if text.startswith("<"):
            blocks.append(text)
        else:
            blocks.append(f'<p class="fineprint guide-fineprint">{esc(text)}</p>')
    if not blocks:
        return ""
    return f'<div class="guide-card-foot">{"".join(blocks)}</div>'


def render_card(kicker: str, title: str, body: str, extra_class: str = "", footnote: str = "") -> str:
    cls = "card"
    if extra_class:
        cls = f"{cls} {extra_class}"
    foot = render_card_foot(footnote) if footnote else ""
    return f"""<section class="{cls}">
        <div class="section-head section-head-tight"><div><p class="section-kicker">{esc(kicker)}</p><h2>{esc(title)}</h2></div></div>
        {body}
        {foot}
      </section>"""


def render_split_row(*sections: str) -> str:
    parts = [s for s in sections if s and s.strip()]
    if not parts:
        return ""
    if len(parts) == 1:
        return parts[0]
    return f'<div class="guide-split-row">{"".join(parts)}</div>'


def render_section_rows(*sections: str) -> str:
    parts = [s for s in sections if s and s.strip()]
    if not parts:
        return ""
    rows = []
    for idx in range(0, len(parts), 2):
        rows.append(render_split_row(*parts[idx : idx + 2]))
    return "".join(rows)


def render_layer2_jump_nav() -> str:
    items = []
    for idx, key in enumerate(LAYER2_ORDER, 1):
        s = LAYER2_STRATEGIES[key]
        accent = LAYER2_ACCENT[key]
        label = layer2_nav_label(key)
        label_html = T(
            f"layer2.{key}.nav",
            label,
            layer2_en(key, "nav", label),
        )
        etfs = " · ".join(s["etfs"])
        items.append(
            f'<a class="guide-l2-jump guide-l2-jump-{accent}" href="#layer2-{key}">'
            f'<span class="guide-l2-jump-num" aria-hidden="true">{idx:02d}</span>'
            f'<span class="guide-l2-jump-copy">'
            f'<span class="guide-l2-jump-name">{label_html}</span>'
            f'<span class="guide-l2-jump-etfs">{esc(etfs)}</span>'
            f"</span></a>"
        )
    return (
        f'<nav class="guide-l2-jump-nav" id="layer2-jump-nav" aria-label="Strategy shortcuts">'
        f'<div class="guide-l2-jump-track">{"".join(items)}</div></nav>'
    )


def render_layer2_visual(key: str) -> str:
    visuals = {
        "us-bonds": """
          <div class="guide-l2-viz guide-l2-viz-bonds">
            <div class="guide-l2-ladder">
              <div class="guide-l2-ladder-bar" style="--h:42%"><span>2Y</span></div>
              <div class="guide-l2-ladder-bar" style="--h:58%"><span>5Y</span></div>
              <div class="guide-l2-ladder-bar" style="--h:72%"><span>10Y</span></div>
              <div class="guide-l2-ladder-bar" style="--h:88%"><span>長天期</span></div>
            </div>
            <p class="guide-l2-viz-cap">美債期貨梯 · 等權分散</p>
          </div>""",
        "managed-futures": """
          <div class="guide-l2-viz guide-l2-viz-trend">
            <svg class="guide-l2-trend-svg" viewBox="0 0 160 72" aria-hidden="true">
              <polyline points="8,58 40,48 72,52 104,28 152,12" />
            </svg>
            <div class="guide-l2-trend-tags">
              <span class="guide-l2-pill guide-l2-pill-up">上升 → 做多</span>
              <span class="guide-l2-pill guide-l2-pill-down">下降 → 做空</span>
            </div>
            <p class="guide-l2-viz-cap">跟價格走 · 約 27 種期貨</p>
          </div>""",
        "futures-carry": """
          <div class="guide-l2-viz guide-l2-viz-carry">
            <div class="guide-l2-carry-row">
              <span class="guide-l2-carry-label">近月</span>
              <div class="guide-l2-carry-bar guide-l2-carry-bar-high"><span>較貴</span></div>
            </div>
            <div class="guide-l2-carry-row">
              <span class="guide-l2-carry-label">遠月</span>
              <div class="guide-l2-carry-bar guide-l2-carry-bar-low"><span>較便宜</span></div>
            </div>
            <p class="guide-l2-viz-cap">逆價差 · 換月可能賺展期</p>
          </div>""",
        "gold-bitcoin": """
          <div class="guide-l2-viz guide-l2-viz-hard">
            <div class="guide-l2-balance">
              <div class="guide-l2-balance-side">
                <span class="guide-l2-balance-icon guide-l2-balance-gold"></span>
                <span>黃金</span>
              </div>
              <div class="guide-l2-balance-beam" aria-hidden="true"></div>
              <div class="guide-l2-balance-side">
                <span class="guide-l2-balance-icon guide-l2-balance-btc"></span>
                <span>比特幣</span>
              </div>
            </div>
            <p class="guide-l2-viz-cap">63 天波動 · 動態調權</p>
          </div>""",
        "merger-arb": """
          <div class="guide-l2-viz guide-l2-viz-arb">
            <div class="guide-l2-arb-track">
              <span class="guide-l2-arb-price">市價 45</span>
              <span class="guide-l2-arb-gap">價差</span>
              <span class="guide-l2-arb-price guide-l2-arb-target">收購價 50</span>
            </div>
            <p class="guide-l2-viz-cap">成交 → 價差收斂</p>
          </div>""",
    }
    return visuals.get(key, "")


def render_layer2_body_text(
    text: str,
    *,
    l2_key: str,
    field: str,
    prefix: str = "",
    same_page: bool = False,
    skip_key: str | None = None,
) -> str:
    if same_page:
        return T(f"layer2.{l2_key}.{field}", text, layer2_en(l2_key, field, text))
    return linkify_guide_text(text, prefix=prefix, same_page=same_page, skip_key=skip_key)


def render_layer2_strategy_card(key: str, prefix: str = "", *, index: int = 0, same_page: bool = False) -> str:
    s = LAYER2_STRATEGIES[key]
    accent = LAYER2_ACCENT[key]

    def l2body(field: str, text: str) -> str:
        return render_layer2_body_text(
            text,
            l2_key=key,
            field=field,
            prefix=prefix,
            same_page=same_page,
            skip_key=key if not same_page else None,
        )

    etf_list = "、".join(s["etfs"]) if same_page else " · ".join(link_etf(t, prefix) for t in s["etfs"])
    points_html = ""
    if s.get("points"):
        cards = []
        for pidx, point in enumerate(s["points"]):
            cards.append(
                f"""<div class="guide-l2-point-card">
              <span class="guide-l2-point-num">{pidx + 1}</span>
              <p>{l2body(f"points.{pidx}", point)}</p>
            </div>"""
            )
        points_html = f"""<div class="guide-l2-points-block">
          <p class="guide-l2-block-label" data-i18n="guide.l2.block.points">重點整理</p>
          <div class="guide-l2-points-grid">{"".join(cards)}</div>
        </div>"""
    num = f"{index:02d}" if index else ""
    if same_page:
        num_html = f'<span class="guide-l2-card-num" aria-hidden="true">{num}</span>'
        title_html = f"<h3>{l2body('title', s['title'])}</h3>"
        seen_in = f'<span data-i18n="guide.l2.seen_in">見於</span> {etf_list}'
    else:
        num_html = (
            f'<a class="guide-l2-card-num" href="{layer2_href(key, prefix, same_page=same_page)}"'
            f' aria-hidden="true">{num}</a>'
        )
        title_html = (
            f"<h3>{link_layer2_key(key, prefix=prefix, same_page=same_page, link_class='guide-heading-link')}</h3>"
        )
        seen_in = f"見於 {etf_list}"
    card_nav = "" if same_page else render_layer2_card_nav(key, prefix, same_page=same_page)
    return f"""<article class="guide-layer2-card guide-layer2-card-rich guide-l2-accent-{accent}" id="layer2-{key}">
        <header class="guide-l2-card-head">
          {num_html}
          <div class="guide-l2-card-head-copy">
            {title_html}
            <p class="guide-layer2-card-etfs">{seen_in}</p>
          </div>
        </header>
        <div class="guide-l2-card-split">
          <div class="guide-l2-pane guide-l2-pane-def">
            <p class="guide-l2-block-label" data-i18n="guide.l2.block.what">在做什麼</p>
            <p class="guide-layer2-card-lead">{l2body("pitch", s["pitch"])}</p>
          </div>
          <div class="guide-l2-pane guide-l2-pane-viz" aria-hidden="false">
            <p class="guide-l2-block-label guide-l2-block-label-viz" data-i18n="guide.l2.block.viz">結構示意</p>
            {render_layer2_visual(key)}
          </div>
        </div>
        <div class="guide-example-box guide-l2-how-box">
          <p class="guide-example-label" data-i18n="guide.l2.block.how">這 100% 怎麼運作</p>
          <p>{l2body("example", s["example"])}</p>
        </div>
        {points_html}
        <div class="guide-l2-footnotes">
          <div class="guide-l2-footnote guide-l2-footnote-official">
            <p class="guide-l2-block-label" data-i18n="guide.l2.block.official">官方怎麼說</p>
            <p>{l2body("official", s["official"])}</p>
          </div>
          <div class="guide-l2-footnote guide-l2-footnote-diff">
            <p class="guide-l2-block-label" data-i18n="guide.l2.block.diff">別跟誰搞混</p>
            <p>{l2body("diff", s["diff"])}</p>
          </div>
        </div>
        {card_nav}
      </article>"""


def render_layer2_explainer(stack_label: str, current_ticker: str = "", *, compact: bool = False) -> str:
    key = layer2_strategy_key(stack_label)
    if not key or key not in LAYER2_STRATEGIES:
        return ""
    s = LAYER2_STRATEGIES[key]
    return f"""<div class="guide-layer2-deep guide-layer2-deep-compact">
        <p class="guide-layer2-deep-kicker">第二層策略 · {esc(s["title"])}</p>
        <p class="guide-layer2-card-lead">{esc(s["pitch"])}</p>
      </div>"""


def render_why_section(why_list: list[str]) -> str:
    cards = []
    for x in why_list:
        parts = re.split(r"[:：]", x, maxsplit=1)
        if len(parts) == 2:
            header, desc = parts[0].strip(), parts[1].strip()
        else:
            header, desc = "", x.strip()

        emoji_match = re.match(r"^([^\w\s<]+)", header)
        if emoji_match:
            emoji = emoji_match.group(1).strip()
            header_text = header[len(emoji_match.group(0)):].strip()
        else:
            emoji = "💡"
            header_text = header.strip()

        header_text = re.sub(r"<[^>]+>", "", header_text)

        cards.append(
            f'<div class="why-card">'
            f'  <div class="why-card-header">'
            f'    <span class="why-card-icon">{emoji}</span>'
            f'    <h4 class="why-card-title">{esc(header_text)}</h4>'
            f'  </div>'
            f'  <p class="why-card-desc">{desc}</p>'
            f'</div>'
        )
    return f'<div class="why-grid">{"".join(cards)}</div>'


def render_etf_nav_tags(current_slug: str) -> str:

    tags = []
    for ticker, zh_name, *_ in SUITE_ROWS:
        slug = ticker.lower()
        if slug == current_slug:
            continue
        tags.append(
            f'<a class="guide-inline-tag" href="{slug}.html">'
            f'<span class="nav-ticker">{esc(ticker)}</span>'
            f'<span class="nav-name">{esc(zh_name)}</span>'
            f'</a>'
        )
    return f'<div class="guide-inline-tags">{"".join(tags)}</div>'


def render_layer2_promo_card() -> str:
    return """<section class="card guide-layer2-promo">
        <div class="section-head section-head-tight">
          <div>
            <p class="section-kicker" data-i18n="guide.learn.promo.kicker">建議閱讀順序</p>
            <h2 data-i18n="guide.learn.promo.title">第二層策略才是關卡</h2>
          </div>
          <a class="card-jump-link" href="layer2.html" data-i18n="guide.learn.promo.link">前往第二層策略</a>
        </div>
        <p class="guide-note" data-i18n="guide.learn.promo.note">各檔真正不同的地方在第二層。專頁用白話拆解「多出來的 100% 在買什麼」，不含第一層。</p>
      </section>"""


def parse_pct(value: str) -> float:
    return float(str(value).replace("%", "").strip())


def holding_layer(ticker: str) -> int:
    if ticker in LAYER1_TICKERS or ticker in LAYER1_FUTURES:
        return 1
    return 2


def render_holdings_section(
    holdings: list[tuple],
    layer1_name: str,
    layer2_name: str,
    ticker: str = "",
    holding_count: str = "",
) -> str:
    if not holdings:
        return ""
    layer1_rows: list[tuple] = []
    layer2_rows: list[tuple] = []
    layer1_sum = 0.0
    layer2_sum = 0.0
    for t, name, pct_str in holdings:
        pct = parse_pct(pct_str)
        if holding_layer(t) == 1:
            layer1_rows.append((t, name, pct_str))
            layer1_sum += pct
        else:
            layer2_rows.append((t, name, pct_str))
            layer2_sum += pct
    listed_sum = layer1_sum + layer2_sum
    count_note = f"全組合約 {holding_count} 檔" if holding_count and holding_count != "—" else "其餘小部位"

    tbills_row = ""
    if ticker.lower() in ("rssb", "rsst", "rsit", "rsbt"):
        tbills_row = f"<tr><td>融資腿（國庫券）</td><td>-100%</td><td>不在前十</td><td>空頭 T-Bills 負責融資（{ticker.upper()} 為 100/100/-100 結構），通常不跟多頭一起列在前十大</td></tr>"

    summary = f"""<div class="guide-exposure-summary">
        <p class="guide-exposure-lead">策略<strong>確實目標 200% 多頭曝險</strong>（100% ＋ 100%）。下方表列數字是「持倉市值占 NAV」，不是把曝險直接相加，所以<strong>不會</strong>加總成 200%。</p>
        <div class="table-wrap table-scroll guide-table-wrap guide-table-compact">
          <table class="quotes guide-table guide-exposure-table">
            <thead><tr><th>項目</th><th>策略目標</th><th>前十大表列</th><th>為何不同</th></tr></thead>
            <tbody>
              <tr><td>第一層 · {esc(layer1_name)}</td><td>100%</td><td>{layer1_sum:.2f}%</td><td>現股 ETF 加股指期貨；期貨列的是保證金市值/NAV，不是 1:1 名義曝險</td></tr>
              <tr><td>第二層 · {esc(layer2_name)}</td><td>100%</td><td>{layer2_sum:.2f}%</td><td>僅列前十大；{count_note}，且期貨同樣有保證金槓桿</td></tr>
              {tbills_row}
              <tr class="guide-row-highlight"><td><strong>多頭合計</strong></td><td><strong>200%</strong></td><td>{listed_sum:.2f}%</td><td>200% 是疊加設計；表列 {listed_sum:.2f}% 是會計占比，兩者口徑不同</td></tr>
            </tbody>
          </table>
        </div>
        
        <div class="guide-analogy-box">
          <div class="guide-analogy-header">
            <span class="guide-analogy-icon">💡</span>
            <span class="guide-analogy-title">為什麼表格加總不等於 200%？（會計占比 vs. 真實曝險）</span>
          </div>
          <div class="guide-analogy-content">
            <div class="guide-analogy-col">
              <div class="guide-analogy-card analogy-margin">
                <span class="analogy-card-label">會計記帳 (官方持倉表)</span>
                <span class="analogy-card-value">{listed_sum:.2f}%</span>
                <p class="analogy-card-desc">僅記錄期貨的<strong>「保證金占比」</strong>（通常僅為 5% ~ 15%）而非 1:1 名義合約價值。</p>
              </div>
            </div>
            <div class="guide-analogy-col">
              <div class="guide-analogy-card analogy-notional">
                <span class="analogy-card-label">策略目標 (真實曝險)</span>
                <span class="analogy-card-value">200%</span>
                <p class="analogy-card-desc">每投入 $1，即疊加 $1 基礎 ＋ $1 策略，獲取 200% 的<strong>名義曝險</strong>。</p>
              </div>
            </div>
          </div>
          <div class="guide-analogy-example">
            <span class="example-tag">🏠 生活比喻</span>
            <p>買一間 <strong>1,000 萬</strong> 的房子，你只需支付 <strong>200 萬首付款</strong>（20% 資金占用），但你背後擁有的是 <strong>1,000 萬</strong> 的房價波動曝險（100% 名義曝險）。官方持倉表像<strong>首付款</strong>，而 200% 則是背後的<strong>總房屋價值</strong>。</p>
          </div>
        </div>
      </div>"""

    layer_tables = render_split_row(
        f"""<div class="guide-holdings-layer">
          <h3 class="guide-holdings-layer-title">第一層 · {esc(layer1_name)}</h3>
          {render_table(["代碼", "名稱", "占比"], layer1_rows, compact=True, table_class="guide-table-holdings")}
        </div>""",
        f"""<div class="guide-holdings-layer">
          <h3 class="guide-holdings-layer-title">第二層 · {esc(layer2_name)}</h3>
          {render_table(["代碼", "名稱", "占比"], layer2_rows, compact=True, table_class="guide-table-holdings")}
        </div>""",
    )

    return f"""{summary}
      <div class="guide-holdings-tables">{layer_tables}</div>"""


def parse_pct_num(value: str | None) -> float | None:
    if not value or value in ("—", "-", "None"):
        return None
    try:
        return float(str(value).replace("%", "").strip())
    except ValueError:
        return None


def growth_end_value(ann_pct: str, years: float) -> float | None:
    rate = parse_pct_num(ann_pct)
    if rate is None or years <= 0:
        return None
    return round(100 * ((1 + rate / 100) ** years), 1)


def render_backtest_section(backtest: dict) -> str:
    stats = backtest.get("stats") or []
    if not stats:
        return ""
    highlight = backtest.get("highlight")
    stat_rows = []
    for label, ret, vol, mdd in stats:
        mdd_disp = mdd if mdd is not None else "—"
        row_cls = ' class="guide-row-highlight"' if label == highlight else ""
        stat_rows.append(
            f"<tr{row_cls}><td>{esc(label)}</td><td>{esc(ret)}</td><td>{esc(vol)}</td><td>{esc(mdd_disp)}</td></tr>"
        )
    period = backtest.get("period", "")
    note = backtest.get("note", "")
    # 使用者有 20 年的投資/直播打算，估值年數一律固定為 20 年
    years = 20
    table = f"""<div class="table-wrap table-scroll guide-table-wrap guide-table-compact">
      <table class="quotes guide-table guide-table-num">
        <thead><tr><th>資產／組合</th><th>年化報酬</th><th>年化波動</th><th>最大回撤</th></tr></thead>
        <tbody>{"".join(stat_rows)}</tbody>
      </table>
    </div>"""
    growth_rows = []
    if years:
        for label, ret, _vol, _mdd in stats:
            end_val = growth_end_value(ret, years)
            if end_val is not None:
                row_cls = ' class="guide-row-highlight"' if label == highlight else ""
                growth_rows.append(
                    f"<tr{row_cls}><td>{esc(label)}</td><td>${end_val:,.1f}</td></tr>"
                )
    growth_block = ""
    if growth_rows:
        growth_block = f"""
        <div class="guide-backtest-col guide-backtest-col-growth">
          <p class="guide-backtest-col-label">Growth of $100（{int(years)} 年後估算終值）</p>
          <div class="table-wrap table-scroll guide-table-wrap guide-table-compact">
            <table class="quotes guide-table guide-table-num">
              <thead><tr><th>資產／組合</th><th>{int(years)} 年後</th></tr></thead>
              <tbody>{"".join(growth_rows)}</tbody>
            </table>
          </div>
        </div>"""
    foot_items = []
    if growth_block:
        foot_items.append(
            f'<p class="fineprint guide-fineprint guide-backtest-growth-note">'
            f"※「歷史回測」年化報酬數據源自官方歷史回測資料；"
            f"「{int(years)} 年後估算終值」為本站依此報酬率複利自行推算，"
            f"非官方數據，亦非逐日回測曲線。</p>"
        )
        tables = f"""<div class="guide-backtest-layout">
        <div class="guide-backtest-col guide-backtest-col-stats">
          <p class="guide-backtest-col-label guide-backtest-col-label-spacer" aria-hidden="true">Growth of $100</p>
          {table}
        </div>
        {growth_block}
      </div>"""
    else:
        tables = table
    foot_items.append(
        f"{esc(note)} 過往績效不代表未來結果；指數報酬為官方回測毛回報，未扣除費用與稅負。"
    )
    footnotes = render_card_foot(*foot_items)
    return f"""
      <section class="card guide-backtest-card">
        <div class="section-head section-head-tight"><div><p class="section-kicker">官方歷史回測</p><h2>Stacking in Action（{esc(period)}）</h2></div></div>
        {tables}
        {footnotes}
      </section>"""


def render_regime_section(regimes: dict) -> str:
    if not regimes or not regimes.get("rows"):
        return ""
    return f"""
      <section class="card">
        <div class="section-head section-head-tight"><div><p class="section-kicker">市場環境</p><h2>不同股價環境下的年化報酬</h2></div></div>
        {render_table(regimes["headers"], regimes["rows"], compact=True)}
        {render_card_foot(regimes.get("note", ""))}
      </section>"""


def render_replication_section(replication: dict) -> str:
    if not replication or not replication.get("rows"):
        return ""
    return f"""
      <section class="card">
        <div class="section-head section-head-tight"><div><p class="section-kicker">複製品質</p><h2>管理期貨複製模型（3 年回顧）</h2></div></div>
        {render_table(replication["headers"], replication["rows"], compact=True)}
        {render_card_foot(replication.get("note", ""))}
      </section>"""


def render_corr_matrix(corr: list[tuple]) -> str:
    if not corr:
        return ""
    headers = corr[0]
    rows = corr[1:]
    th_parts = []
    for idx, label in enumerate(headers):
        if idx == 0:
            th_parts.append(f'<th class="guide-corr-corner">{esc(label)}</th>')
        else:
            th_parts.append(f"<th>{esc(label)}</th>")
    body = []
    for row in rows:
        tds = []
        for idx, cell in enumerate(row):
            if idx == 0:
                tds.append(f'<td class="guide-corr-rowhead">{esc(cell)}</td>')
            else:
                cls = "guide-corr-val"
                if cell == "1.00":
                    cls += " guide-corr-diag"
                tds.append(f'<td class="{cls}">{esc(cell)}</td>')
        body.append(f"<tr>{''.join(tds)}</tr>")
    return f"""<div class="table-wrap guide-table-wrap guide-corr-wrap">
      <table class="quotes guide-table guide-table-corr">
        <thead><tr>{"".join(th_parts)}</tr></thead>
        <tbody>{"".join(body)}</tbody>
      </table>
    </div>"""


def render_benchmark_section(benchmark: dict) -> str:
    if not benchmark or not benchmark.get("rows"):
        return ""
    return f"""
      <section class="card">
        <div class="section-head section-head-tight"><div><p class="section-kicker">基準對照</p><h2>與基準指數及 100/100 組合對照</h2></div></div>
        {render_table(benchmark["headers"], benchmark["rows"], compact=True)}
        {render_card_foot(benchmark.get("note", ""))}
      </section>"""


def tim_configured(row: tuple) -> bool:
    return bool(row[8])


def build_learn() -> str:
    suite_table = render_table(
        [
            ("guide.table.ticker", "代號"),
            ("guide.table.name", "名稱"),
            ("guide.table.layer1", "第一層（100%）"),
            ("guide.table.layer2", "第二層（100%）"),
            ("guide.table.tim", "Tim 實測"),
        ],
        render_learn_suite_table_rows(),
        table_class="guide-table-suite",
        html_cells=True,
    )
    stack_tags = render_layer2_stack_tags()
    return (
        head(
            "認識實驗 · Return Stacking | Tim Wei",
            "Return Stacking 是什麼？Tim Wei 透明實驗紀錄。先懂概念，再看實測數據。",
            "learn",
            title_en="Learn · Return Stacking | Tim Wei",
            desc_en="What is Return Stacking? Tim Wei's transparent experiment log.",
        )
        + shell_start("learn", "learn")
        + f"""
      <header class="hero hero-compact guide-hero">
        <div class="hero-copy hero-copy-compact guide-hero-copy">
          <p class="hero-tag" data-i18n="guide.learn.hero.tag">學習中心</p>
          <h1 data-i18n="guide.learn.hero.title">認識這個實驗</h1>
          <p class="guide-lead" data-i18n="guide.learn.hero.lead">這個網站是完整教材：先把 Return Stacking 與 ETF 家族講清楚，再到總覽頁看 Tim Wei 的實測數據。Threads、FB 等社群貼文只挑幾個重點，完整內容都在這裡。</p>
        </div>
      </header>

      <section class="guide-path card" aria-label="建議閱讀路徑">
        <div class="section-head section-head-tight">
          <div>
            <p class="section-kicker" data-i18n="guide.learn.path.kicker">怎麼讀</p>
            <h2 data-i18n="guide.learn.path.title">建議路徑（約 15 分鐘）</h2>
          </div>
        </div>
        <ol class="guide-steps">
          <li data-i18n="guide.learn.path.1"><strong>認識實驗</strong>（本頁）— 報酬疊加是什麼、Tim 在做什麼</li>
          <li data-i18n="guide.learn.path.2"><strong>ETF 百科</strong> — 8 檔家族一覽；挑標的前先看第二層</li>
          <li data-i18n="guide.learn.path.3"><strong>第二層策略</strong> — 只講多出來的 100% 在買什麼</li>
          <li data-i18n="guide.learn.path.4"><strong>實測總覽</strong> — NAV、策略拆解、部位表</li>
          <li data-i18n="guide.learn.path.5"><strong>帳本明細</strong> — 績效、貸款、換匯紀錄</li>
          <li data-i18n="guide.learn.path.6"><strong>FB 社團</strong> — 有問題再討論（總覽頁底部可加入）</li>
        </ol>
      </section>

      <section class="guide-grid">
        <article class="card guide-card">
          <p class="section-kicker" data-i18n="guide.learn.tim.kicker">30 秒版</p>
          <h2 data-i18n="guide.learn.tim.title">Tim Wei 在做什麼？</h2>
          <ul class="guide-list">
            <li data-i18n="guide.learn.tim.1">剛滿 25 歲，以 135 萬台幣貸款作為本金來源之一，公開紀錄這個 Return Stacking 實驗（NAV、再平衡、還款進度全部透明；細節見帳本明細）。</li>
            <li data-i18n="guide.learn.tim.2">資金投入 Return Stacked ETFs 系列，策略稱為 Return Stacking（報酬疊加）。</li>
            <li data-i18n="guide.learn.tim.3">每一筆買賣、NAV、再平衡、還款進度全部公開——不賣課、不是投資建議。</li>
            <li data-i18n="guide.learn.tim.4">白天做量化選擇權交易；這個實驗是用自己的錢做長期透明紀錄。</li>
          </ul>
        </article>

        <article class="card guide-card guide-card-accent">
          <p class="section-kicker" data-i18n="guide.learn.core.kicker">核心概念</p>
          <h2 data-i18n="guide.learn.core.title">Return Stacking 是什麼？</h2>
          <div class="guide-analogy">
            <p data-i18n="guide.learn.core.analogy.1"><strong>100 元買股票</strong> → 100 元股票曝險（100%）</p>
            <p data-i18n="guide.learn.core.analogy.2"><strong>100 元買正二</strong> → 200 元<strong>同一種</strong>股票曝險（200%）</p>
            <p data-i18n="guide.learn.core.analogy.3"><strong>100 元買報酬疊加 ETF</strong> → 100 元股票 ＋ 100 元<strong>不同路</strong>的資產（例如美國公債、管理期貨（趨勢追蹤）、期貨展期收益）</p>
          </div>
          <p class="guide-note" data-i18n="guide.learn.core.note">同樣是 200% 總曝險，但第二層與第一層<strong>低相關</strong>，波動通常小於槓桿單一資產。這就是「讓每一塊錢工作兩次，但兩次做不同的事」。</p>
        </article>
      </section>

      <section class="card guide-stack-viz" aria-label="雙層結構">
        <div class="section-head section-head-tight">
          <div>
            <p class="section-kicker" data-i18n="guide.learn.stack.kicker">結構</p>
            <h2 data-i18n="guide.learn.stack.title">每一檔 Return Stacked ETF 的共通設計</h2>
          </div>
        </div>
        <div class="guide-stack-diagram">
          <div class="guide-stack-layer guide-stack-layer-top">
            <span class="guide-stack-pct">100%</span>
            <span class="guide-stack-label" data-i18n="guide.learn.stack.layer2">第二層 · 疊加策略</span>
            <div class="guide-stack-examples">{stack_tags}</div>
          </div>
          <div class="guide-stack-layer guide-stack-layer-base">
            <span class="guide-stack-pct">100%</span>
            <span class="guide-stack-label" data-i18n="guide.learn.stack.layer1">第一層 · 基礎曝險</span>
            <span class="guide-stack-examples" data-i18n="guide.learn.stack.layer1.examples">全球股／美股／國際股／債券…</span>
          </div>
          <div class="guide-stack-foot" data-i18n="guide.learn.stack.foot">投入 1 美元 → 目標約 2 美元總曝險（透過期貨等衍生品實現，非保證）</div>
        </div>
      </section>

      """
        + render_layer2_promo_card()
        + """
      <section class="guide-grid">
        <article class="card guide-card guide-dilemma-card">
          <p class="section-kicker" data-i18n="guide.learn.why.kicker">為什麼需要它？</p>
          <h2 data-i18n="guide.learn.why.title">傳統分散化的困境</h2>
          <div class="guide-dilemma-body">
            <div class="guide-dilemma-block guide-dilemma-block-problem">
              <p class="guide-dilemma-tag" data-i18n="guide.learn.why.problem.label">減法分散</p>
              <p class="guide-dilemma-copy" data-i18n="guide.learn.why.p1">一般做法要加「替代策略」，得從<strong>股票或債券減碼</strong>（例如 60/40 改成 50/30/20）。替代策略落後時，投資人容易在股票創高時賣掉它——官方稱這是<strong>「用減法做分散」</strong>，容易產生行為摩擦。</p>
            </div>
          </div>
          <div class="guide-card-foot">
            <div class="guide-dilemma-block guide-dilemma-block-solution">
              <p class="guide-dilemma-tag guide-dilemma-tag-solution" data-i18n="guide.learn.why.solution.label">報酬疊加</p>
              <p class="guide-dilemma-copy guide-dilemma-copy-solution" data-i18n="guide.learn.why.note">維持<strong>核心市場曝險不減</strong>，用一檔 ETF 同時持有基礎曝險與分散化策略。</p>
            </div>
          </div>
        </article>
        <article class="card guide-card guide-compare-card">
          <p class="section-kicker" data-i18n="guide.learn.compare.kicker">跟正二差在哪？</p>
          <h2 data-i18n="guide.learn.compare.title">200% 曝險，但不是同一種風險</h2>
          <table class="guide-compare-table">
            <thead><tr><th data-i18n="guide.learn.compare.h.empty"></th><th data-i18n="guide.learn.compare.h.lev">正二（槓桿 ETF）</th><th data-i18n="guide.learn.compare.h.rs">Return Stacking</th></tr></thead>
            <tbody>
              <tr><td data-i18n="guide.learn.compare.r1.label">曝險組成</td><td data-i18n="guide.learn.compare.r1.lev">200% 同一資產</td><td data-i18n="guide.learn.compare.r1.rs">100% A ＋ 100% B（低相關）</td></tr>
              <tr><td data-i18n="guide.learn.compare.r2.label">波動來源</td><td data-i18n="guide.learn.compare.r2.lev">單一市場放大</td><td data-i18n="guide.learn.compare.r2.rs">兩條腿互相分散</td></tr>
              <tr><td data-i18n="guide.learn.compare.r3.label">典型第二層</td><td data-i18n="guide.learn.compare.r3.lev">—</td><td data-i18n="guide.learn.compare.r3.rs">美國公債、管理期貨（趨勢追蹤）、期貨展期收益、併購套利…</td></tr>
            </tbody>
          </table>
        </article>
      </section>

      <section class="card">
        <div class="section-head section-head-tight">
          <div>
            <p class="section-kicker" data-i18n="guide.learn.suite.kicker">系列一覽</p>
            <h2 data-i18n="guide.learn.suite.title">Return Stacked ETF 家族（2026 Q1 資料）</h2>
          </div>
          <a class="card-jump-link" href="etfs.html" data-i18n="guide.learn.suite.link">全部詳解</a>
        </div>
        """
        + suite_table
        + """
        <div class="guide-card-foot">
          <p class="fineprint guide-fineprint" data-i18n="guide.learn.suite.foot">AUM 資料截至 2026-03-31，摘自 Return Stacked Q1 2026 Commentary。過往績效不代表未來結果。</p>
        </div>
      </section>

      <section class="card guide-card-warn">
        <p class="section-kicker" data-i18n="guide.learn.warn.kicker">風險聲明</p>
        <h2 data-i18n="guide.learn.warn.title">請先讀這段</h2>
        <ul class="guide-list guide-list-compact">
          <li data-i18n="guide.learn.warn.1">本網站為 Tim Wei 個人實驗紀錄與教育整理，<strong>不是投資建議</strong>。</li>
          <li data-i18n="guide.learn.warn.2">使用貸款投資、衍生品與槓桿具高度風險，可能損失全部本金。</li>
          <li data-i18n="guide.learn.warn.3">ETF 可能折溢價、追蹤誤差；新基金歷史資料有限。</li>
          <li data-i18n="guide.learn.warn.4">投資前請閱讀各檔公開說明書。</li>
        </ul>
      </section>
"""
        + shell_end("learn")
    )


def build_layer2() -> str:
    cards = "".join(
        render_layer2_strategy_card(key, index=idx, same_page=True)
        for idx, key in enumerate(LAYER2_ORDER, 1)
    )
    return (
        head(
            "第二層策略 · Return Stacking | Tim Wei",
            "管理期貨、期貨展期收益、黃金比特幣、併購套利——白話拆解多出來的 100% 在買什麼。",
            "layer2",
            title_en="Layer 2 Strategies · Return Stacking | Tim Wei",
            desc_en="Managed futures, futures yield, gold/Bitcoin, merger arb—what the extra 100% overlay is doing.",
        )
        + shell_start("layer2", "layer2")
        + """
      <header class="hero hero-compact guide-hero">
        <div class="hero-copy hero-copy-compact guide-hero-copy">
          <p class="hero-tag" data-i18n="guide.l2.hero.tag">第二層策略</p>
          <h1 data-i18n="guide.l2.hero.title">多出來的 100% 在買什麼？</h1>
          <p class="guide-lead" data-i18n="guide.l2.hero.lead">報酬疊加 ETF 用衍生品再建立約 100% 的額外曝險。以下只講這一層——不含第一層股票或債券。</p>
        </div>
      </header>

      """
        + render_layer2_jump_nav()
        + """
      <section class="guide-layer2-section" aria-label="第二層策略詳解">
        <div class="guide-layer2-grid guide-layer2-grid-stacked">
          """
        + cards
        + """
        </div>
      </section>

      """
        + shell_end("layer2")
    )


def build_etfs_index() -> str:
    cards = []
    tone_map = {"capital": "guide-etf-capital", "alt": "guide-etf-alt", "bond": "guide-etf-bond"}
    for row in SUITE_ROWS:
        ticker, zh, en, base, stack, launch, aum, tone, in_port = row
        slug = ticker.lower()
        badge = "guide-badge-live" if in_port else "guide-badge-ref"
        badge_key = "guide.etfs.badge.live" if in_port else "guide.etfs.badge.ref"
        badge_zh = "實測有配" if in_port else "參考標的"
        badge_text = T(badge_key, badge_zh, ui_en(badge_key, badge_zh))
        cards.append(
            f"""<article class="card guide-etf-card {tone_map[tone]}">
          <div class="guide-etf-card-head">
            <a class="guide-etf-ticker" href="etfs/{slug}.html">{esc(ticker)}</a>
            <span class="guide-badge {badge}">{badge_text}</span>
          </div>
          <h2 class="guide-etf-title">{T(f"etf.{slug}.name", zh, en)}</h2>
          <p class="guide-etf-sub">{esc(en)}</p>
          <dl class="guide-etf-meta">
            <div><dt data-i18n="guide.etfs.meta.layer1">第一層</dt><dd>{T(f"etf.{slug}.base", base, BASE_EN.get(base, base))}</dd></div>
            <div><dt data-i18n="guide.etfs.meta.layer2">第二層</dt><dd>{T(f"etf.{slug}.stack", stack, STACK_EN.get(stack, stack))}</dd></div>
            <div><dt data-i18n="guide.etfs.meta.inception">成立</dt><dd>{esc(launch)}</dd></div>
            <div><dt data-i18n="guide.table.aum">AUM</dt><dd>{esc(aum)}</dd></div>
          </dl>
          <p class="guide-etf-blurb">{esc(ETF_DETAILS[slug]["tagline"])}</p>
          <a class="btn-secondary guide-etf-card-btn" href="etfs/{slug}.html" data-i18n="guide.etfs.card.read">閱讀完整說明</a>
        </article>"""
        )

    suite_table = render_table(
        [
            ("guide.table.ticker", "代號"),
            ("guide.table.zh_name", "中文名"),
            ("guide.table.layer1", "第一層"),
            ("guide.table.layer2", "第二層"),
            ("guide.table.inception", "成立"),
            ("guide.table.aum", "AUM"),
            ("guide.table.tim", "Tim 實測"),
        ],
        render_suite_table_rows(),
        table_class="guide-table-suite guide-table-suite-metrics",
        html_cells=True,
    )

    return (
        head(
            "ETF 百科 | Return Stacked 全系列",
            "8 檔 Return Stacked ETF 完整說明：結構、費率、持股、績效、相關性。",
            "etfs",
            title_en="ETF Guide | Return Stacked Lineup",
            desc_en="Full guide to all 8 Return Stacked ETFs: structure, fees, holdings, performance, correlations.",
        )
        + shell_start("etfs", "etfs")
        + """
      <header class="hero hero-compact guide-hero">
        <div class="hero-copy hero-copy-compact guide-hero-copy">
          <p class="hero-tag" data-i18n="guide.etfs.hero.tag">ETF 百科</p>
          <h1 data-i18n="guide.etfs.hero.title">Return Stacked 全系列</h1>
          <p class="guide-lead" data-i18n="guide.etfs.hero.lead">以下整理自各檔 Product Brief、Fact Sheet 與 Q1 2026 Commentary（截至 2026-03-31）。這是網站上的完整教材；社群貼文只會挑其中幾個重點。</p>
        </div>
      </header>

      """
        + render_layer2_promo_card()
        + f"""
      <section class="card" aria-label="ETF lineup table">
        <div class="section-head section-head-tight">
          <div><p class="section-kicker">總表</p><h2 data-i18n="guide.etfs.table.title">8 檔對照</h2></div>
        </div>
        {suite_table}
      </section>

      <section class="guide-etf-grid" aria-label="ETF cards">
        {"".join(cards)}
      </section>

      {render_tim_allocation_section()}
"""
        + shell_end("etfs")
    )


def build_etf_page(slug: str) -> str:
    meta = next(r for r in SUITE_ROWS if r[0].lower() == slug)
    ticker, zh, en, base, stack, launch, aum, tone, in_port = meta
    d = ETF_DETAILS[slug]
    f = d["fund"]

    fund_rows = [
        ("交易所", f["exchange"]),
        ("成立日", f["inception"]),
        ("持股數", f["holdings"]),
        ("總費率（毛）", f["expense_gross"]),
        ("總費率（淨）", f["expense_net"]),
        ("30 日 SEC 殖利率", f["sec_yield"]),
    ]
    if f.get("expense_note"):
        fund_rows.append(("費率備註", f["expense_note"]))

    layers_html_parts = []
    for title, body in d["layers"]:
        layers_html_parts.append(
            f'<div class="guide-layer-block"><h3>{esc(title)}</h3>'
            f"<p>{esc(body)}</p></div>"
        )
    layers_html = "".join(layers_html_parts)
    why_html = render_why_section(d["why"])
    risks_html = "".join(f"<li>{esc(x)}</li>" for x in d["risks"])

    holdings_html = ""
    if d["holdings"]:
        holdings_html = render_card(
            "持股",
            "主要持倉（2026-03-31）",
            render_holdings_section(d["holdings"], base, stack, ticker, f.get("holdings", "")),
            "guide-holdings-card",
            "持倉會變動，僅供理解結構，非即時資料。占比摘自官方 Q1 Commentary。",
        )

    perf_html = ""
    if d["perf"]:
        perf_html = render_card(
            "績效",
            "基金報酬（截至 2026-03-31）",
            render_table(["期間", "NAV", "市價"], d["perf"], compact=True),
            footnote="過往績效不代表未來結果。短於一年為累計報酬。",
        )

    fund_card = render_card(
        "基金資料",
        "規格表",
        render_spec_dl(fund_rows),
    )

    structure_card = render_card(
        "雙層結構",
        "這一檔怎麼疊？",
        f'<div class="guide-layers">{layers_html}</div>{render_layer2_explainer(stack, ticker, compact=True)}',
    )

    why_card = render_card(
        "為什麼存在",
        "設計邏輯與使用情境",
        why_html,
        "guide-why-card",
    )

    benchmark_html = render_benchmark_section(d.get("benchmark"))
    backtest_html = render_backtest_section(d.get("backtest") or {})
    regime_html = render_regime_section(d.get("regimes") or {})
    replication_html = render_replication_section(d.get("replication") or {})

    corr_html = ""
    if d["corr"]:
        corr_html = render_card(
            "相關性",
            "歷史相關矩陣（官方 Product Brief）",
            render_corr_matrix(d["corr"]),
            footnote="相關性會隨時間改變，僅供理解第二層與核心的關係。",
        )

    badge = "guide-badge-live" if in_port else "guide-badge-ref"
    badge_text = "Tim 實測有配置" if in_port else "Tim 實測未配置"
    tim_holdings_link = (
        f'<p><a class="card-jump-link" href="../index.html">在總覽看 {esc(ticker)} 持倉 →</a></p>'
        if in_port
        else ""
    )

    return (
        head(f"{ticker} · {zh} | ETF 百科", d["tagline"], f"etf-{slug}")
        + shell_start("etfs", f"etf-{slug}")
        + f"""
      <nav class="guide-breadcrumb" aria-label="麵包屑">
        <span>ETF 百科</span>
        <span aria-hidden="true">/</span>
        <span>{esc(ticker)}</span>
      </nav>

      <header class="hero hero-compact guide-hero guide-etf-hero">
        <div class="hero-copy hero-copy-compact guide-hero-copy">
          <p class="hero-tag">{esc(en)}</p>
          <h1><span class="guide-etf-ticker guide-etf-ticker-lg">{esc(ticker)}</span> {esc(zh)}</h1>
          <p class="guide-lead">{esc(d["tagline"])}</p>
          <span class="guide-badge {badge}">{badge_text}</span>
        </div>
      </header>

      <section class="guide-metric-strip focus-metric-grid" aria-label="Quick facts">
        <article class="focus-metric"><span class="focus-metric-label">第一層</span><strong class="focus-metric-value guide-metric-text">{esc(base)}</strong></article>
        <article class="focus-metric"><span class="focus-metric-label">第二層</span><strong class="focus-metric-value guide-metric-text">{esc(stack)}</strong></article>
        <article class="focus-metric"><span class="focus-metric-label">AUM</span><strong class="focus-metric-value">{esc(aum)}</strong></article>
        <article class="focus-metric"><span class="focus-metric-label">淨費率</span><strong class="focus-metric-value">{esc(f["expense_net"])}</strong></article>
      </section>

      {render_split_row(structure_card, "")}
      {why_card}
      {render_split_row(perf_html, benchmark_html)}
      {render_split_row(fund_card, corr_html)}
      {holdings_html}
      {backtest_html}
      {render_split_row(regime_html, replication_html)}

      {render_split_row(
        render_card(
          "Tim Wei 實測",
          "這一檔與本實驗的關係",
          f"<p>{esc(d['tim_note'])}</p>{tim_holdings_link}",
          "guide-card-accent-soft",
        ),
        render_card(
          "主要風險",
          "投資前必知（摘要）",
          f'<ul class="guide-list guide-list-compact">{risks_html}</ul>',
          "guide-card-warn",
          "完整風險請見各檔公開說明書。本頁為教育整理，非投資建議。",
        ),
      )}

      <nav class="guide-etf-nav card" aria-label="其他 ETF">
        <div class="section-head section-head-tight">
          <div>
            <p class="section-kicker">延伸閱讀</p>
            <h2>Return Stacked 系列其他標的</h2>
          </div>
        </div>
        <p class="guide-nav-desc">目前頁面為 <strong>{esc(ticker)}</strong>。其他標的：</p>
        {render_etf_nav_tags(slug)}
      </nav>
"""
        + shell_end(f"etf-{slug}")
    )


def main() -> None:
    I18N_REGISTRY.clear()
    bootstrap_i18n()
    ETF_DIR.mkdir(parents=True, exist_ok=True)
    (SITE / "learn.html").write_text(build_learn(), encoding="utf-8")
    (SITE / "layer2.html").write_text(build_layer2(), encoding="utf-8")
    (SITE / "etfs.html").write_text(build_etfs_index(), encoding="utf-8")
    for slug in ETF_DETAILS:
        (ETF_DIR / f"{slug}.html").write_text(build_etf_page(slug), encoding="utf-8")
    write_guide_locale_js()
    print(f"Wrote learn.html, layer2.html, etfs.html, guide-locale.js, and {len(ETF_DETAILS)} pages under etfs/")


if __name__ == "__main__":
    main()
