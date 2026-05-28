"""English copy for Return Stacked ETF detail pages (8 tickers)."""

from __future__ import annotations

ETF_EN: dict[str, dict] = {
    "rssb": {
        "display_name": "Global Stocks & Bonds",
        "tagline": "The foundation of the Return Stacked suite: 100% global equities plus 100% US Treasuries—one ETF for 200% exposure.",
        "layers": [
            (
                "Layer 1 · Global stocks 100%",
                "Tracks global cap-weighted equities (SPTM, VXUS, and similar holdings) to cover the investable global stock market.",
            ),
            (
                "Layer 2 · US Treasuries 100%",
                "Equal-weight 2-, 5-, 10-, and long Treasury futures for bond exposure that is typically lowly correlated with stocks.",
            ),
        ],
        "why": [
            "🗺️ <strong>Capital efficiency</strong>: Every 10% allocated to RSSB is equivalent to holding <strong>10% global stocks</strong> and <strong>10% US Treasuries</strong> at once. That can <strong>free 10% of idle cash</strong> (via derivatives financing) to deploy into low-correlation alternatives such as CTAs, gold, or arbitrage—maximizing how hard each dollar works.",
            "⚡ <strong>Allocation flexibility</strong>: Traditionally, adding diversifiers (e.g. trend) means trimming stocks or bonds. With RSSB you can sell part of a 100% stock/bond sleeve, buy RSSB instead, keep <strong>the same stock/bond exposure</strong>, and <strong>release cash</strong> for new assets.",
            "🧠 <strong>Behavioral bias</strong>: When stocks rally and bonds lag or draw down, investors often cut bonds out of discomfort. Stacking stocks and bonds in one ETF shows a single NAV, which can <strong>reduce the urge to abandon diversification after a single-leg drawdown</strong>.",
            "⚙️ <strong>Automated financing</strong>: Through in-fund contracts, investors <strong>do not need a margin account</strong> or manual futures rolls to access low-cost short T-Bill financing—avoiding personal tax complexity and margin-call risk.",
        ],
        "tim_note": "Core building block of the Tim Wei experiment. Holdings and weights are visible on the live portfolio page.",
        "expense_note": "Management fee waived through 2026-05-30; net expense ratio 0.40%.",
    },
    "rsst": {
        "display_name": "U.S. Stocks & Managed Futures",
        "tagline": "Full US large-cap equity exposure underneath, with a managed-futures trend overlay that can go long or short.",
        "layers": [
            (
                "Layer 1 · US stocks 100%",
                "Large-cap US equity market (e.g. SPYM), tracking S&P 500–style exposure.",
            ),
            (
                "Layer 2 · Managed futures 100%",
                "27 futures across commodities, FX, rates, and equity indices; top-down + bottom-up blend replicating a CTA trend sleeve.",
            ),
        ],
        "why": [
            "⚖️ <strong>US beta and managed-futures alpha</strong>: Layer 1 is <strong>100% US large-cap stocks</strong> (S&P 500) to participate in long-run US growth. Layer 2 adds <strong>100% managed-futures trend</strong> seeking asymmetric absolute return across macro regimes and volatility spikes.",
            "🛡️ <strong>Crisis alpha diversification</strong>: Historically, CTA trend strategies have often posted positive returns in equity crashes, systemic stress, and high inflation (e.g. 2008, 2022) by shorting equity indices and going long commodities or the dollar—offering <strong>complementary downside protection</strong> versus stocks.",
            "⚡ <strong>Painless portfolio upgrade</strong>: Sell 20% of an existing US equity sleeve and buy 20% RSST to keep <strong>unchanged US stock exposure</strong> while <strong>stacking 20% managed-futures trend</strong> with no extra cash—true capital decoupling.",
            "📈 <strong>High-fidelity index replication</strong>: Not discretionary trading—a quantitative replica of the sponsor managed-futures trend index. As of Q1 2026 commentary, the blend model’s 3-year daily correlation is <strong>0.84</strong> with tracking error <strong>5.4%</strong>.",
        ],
        "tim_note": "Tim Wei holds RSST alongside RSSB, RSSY, and RSIT.",
    },
    "rssy": {
        "display_name": "U.S. Stocks & Futures Yield",
        "tagline": "100% US stocks plus 100% cross-asset futures carry (roll yield).",
        "layers": [
            (
                "Layer 1 · US stocks 100%",
                "Large-cap US equity market exposure.",
            ),
            (
                "Layer 2 · Futures carry 100%",
                "Systematic long/short across commodity, FX, bond, and equity index futures to harvest roll yield.",
            ),
        ],
        "why": [
            "💰 <strong>Futures carry (roll yield)</strong>: Layer 1 is <strong>100% US large-cap stocks</strong>. Layer 2 is <strong>100% futures carry</strong>—systematically long markets where the near contract trades below the far, and short the opposite, to <strong>harvest roll premia and discounts</strong>.",
            "🔗 <strong>Multi-asset diversifier</strong>: Historically, futures carry has been <strong>lowly correlated</strong> with stocks and bonds—and often with trend (CTA) as well—adding another <strong>independent return stream</strong> (risk premia) to smooth portfolio volatility.",
            "⛅ <strong>Help in bull and range markets</strong>: Unlike trend, which needs clear direction, carry can earn structural spreads and time value in low-vol, range-bound, or gently bullish regimes—providing <strong>steady portfolio support</strong>.",
            "⚡ <strong>Capital efficiency</strong>: Convert 20% of a US equity sleeve into RSSY to keep <strong>full US upside participation</strong> while <strong>stacking 20% carry exposure</strong>—raising how efficiently capital is deployed.",
        ],
        "tim_note": "Tim Wei holds RSSY.",
    },
    "rsit": {
        "display_name": "International Stocks & Managed Futures",
        "tagline": "100% developed-market international equities plus 100% managed-futures trend—the international version of RSST.",
        "layers": [
            (
                "Layer 1 · International stocks 100%",
                "Developed markets ex-North America large, mid, and small caps (S&P Developed ex-US BMI–related exposure).",
            ),
            (
                "Layer 2 · Managed futures 100%",
                "Same replication framework as RSST: 27 futures, top-down + bottom-up blend.",
            ),
        ],
        "why": [
            "🗺️ <strong>Global allocation building block</strong>: For investors who want to <strong>reduce US concentration</strong>, RSIT’s base is <strong>100% developed ex-US equities</strong> (Europe, Asia-Pacific, and other DM large caps)—the core non-US equity sleeve in a global portfolio.",
            "🛡️ <strong>Diversification and crisis protection</strong>: Layer 2 is <strong>100% managed-futures trend</strong>. DM ex-US equities can be more volatile than the US; trend overlays that short equity indices and lean defensive in crashes can add valuable <strong>crisis alpha</strong> for the international sleeve.",
            "⚡ <strong>Efficient international diversification</strong>: If you already hold 20% DM ex-US stocks, swap that slice for 20% RSIT to keep <strong>the same non-US equity exposure</strong> while painlessly stacking <strong>20% managed futures</strong>—<strong>freeing capital</strong> for other uses.",
            "📈 <strong>Precise trend index tracking</strong>: Shares RSST’s replication framework; as of Q1 2026, 3-year daily correlation <strong>0.84</strong> and tracking error <strong>5.4%</strong>—a mature, market-tested quantitative sleeve.",
        ],
        "tim_note": "Tim Wei holds RSIT.",
        "expense_note": "New listing in 2026 Q2; listing date per Tim Wei experiment log.",
    },
    "rssx": {
        "display_name": "U.S. Stocks & Gold/Bitcoin",
        "tagline": "100% US stocks plus 100% gold and Bitcoin—risk parity on 63-day volatility, rebalanced monthly.",
        "layers": [
            (
                "Layer 1 · US stocks 100%",
                "Large-cap US equity market (e.g. SPYM).",
            ),
            (
                "Layer 2 · Gold + Bitcoin 100%",
                "Gold and Bitcoin via futures and ETFs (e.g. IBIT); weights aim for equal risk contribution, scaling down the higher-vol asset.",
            ),
        ],
        "why": [
            "💎 <strong>US stocks plus hard assets</strong>: Layer 1 is <strong>100% US large-cap stocks</strong>. Layer 2 is <strong>100% gold and Bitcoin</strong>. As alternative monetary and hard assets, they can behave differently from traditional stocks and bonds—inflation hedging, fiat debasement, and credit-stress scenarios.",
            "⚖️ <strong>Risk-parity dynamic weights</strong>: Layer 2 is not a static 50/50 split. A risk-parity model adjusts weights from historical volatility so each asset contributes roughly equal risk—helping limit damage when a high-vol leg (e.g. Bitcoin) sells off sharply.",
            "🔗 <strong>Low-correlation diversification</strong>: Historically, gold’s correlation to US stocks is about 0.09; Bitcoin to US stocks about 0.23. That low overlap lets the hard-asset sleeve <strong>diversify US equity drawdowns</strong> and smooth combined NAV volatility.",
            "📦 <strong>One-ticket access</strong>: For investors who want gold and Bitcoin without separate accounts, rebalancing, or physical custody—sell 20% US equity, buy 20% RSSX, and <strong>stack both alternatives</strong> without giving up the stock sleeve.",
        ],
        "tim_note": "Tim Wei does not hold RSSX yet; explanatory posts are prepared.",
    },
    "rsbt": {
        "display_name": "Bonds & Managed Futures",
        "tagline": "100% US bonds plus 100% managed-futures trend—CTA stacked on a bond base.",
        "layers": [
            (
                "Layer 1 · US bonds 100%",
                "Broad US fixed income (e.g. SPAB) plus Treasury futures exposure.",
            ),
            (
                "Layer 2 · Managed futures 100%",
                "Same trend replication strategy as RSST.",
            ),
        ],
        "why": [
            "💵 <strong>Enhanced core fixed income</strong>: Layer 1 is <strong>100% broad US aggregate bond exposure</strong> (Bloomberg US Aggregate–style)—the defensive, income anchor. Layer 2 adds <strong>100% managed-futures trend</strong>, long/short across commodities, FX, equity indices, and rates to <strong>inject dynamic return potential</strong> into a conservative bond book.",
            "💥 <strong>When stocks and bonds fall together</strong>: In high-inflation, rates-up regimes (e.g. 2022), classic stock/bond balances can fail. RSBT’s trend sleeve has often shone in directional markets—e.g. short bond and equity futures—<strong>offsetting spread widening and rate-driven bond losses</strong>.",
            "⚡ <strong>Free the bond sleeve</strong>: Sell 20% of a bond allocation, buy 20% RSBT, and keep <strong>full 20% bond income and exposure</strong> while adding <strong>20% managed futures</strong> at no extra cash—more allocation flexibility.",
            "📈 <strong>Series pioneer with live track record</strong>: Among the earliest Return Stacked listings (Feb 2023) with longer live history and robust replication. Q1 2026: 3-year daily correlation <strong>0.84</strong>, tracking error <strong>5.4%</strong>.",
        ],
        "tim_note": "Tim Wei does not hold RSBT (bond-base variant).",
    },
    "rsby": {
        "display_name": "Bonds & Futures Yield",
        "tagline": "100% US bonds plus 100% cross-asset futures carry—the bond-base version of RSSY.",
        "layers": [
            (
                "Layer 1 · US bonds 100%",
                "Broad US fixed income market exposure.",
            ),
            (
                "Layer 2 · Futures carry 100%",
                "Multi-asset roll-yield strategy; same Layer 2 logic as RSSY.",
            ),
        ],
        "why": [
            "🛡️ <strong>Defensive core plus carry</strong>: Layer 1 is <strong>100% US aggregate bond exposure</strong> for income and defense. Layer 2 is <strong>100% futures carry</strong>—systematically harvesting roll yield across commodities, FX, bonds, and equity index futures from term-structure spreads.",
            "🔀 <strong>Returns independent of trend</strong>: Unlike trend, carry can earn in sideways, low-vol markets without a strong directional move. It is typically <strong>lowly correlated</strong> with stocks and bonds—helping <strong>smooth NAV volatility</strong> further.",
            "⚡ <strong>Escape the trim-bonds dilemma</strong>: To add alternative yield in a traditional portfolio you usually cut bonds. With RSBY, sell 20% bonds, buy 20% RSBY, and <strong>preserve 1:1 bond exposure and coupon</strong> while stacking <strong>20% carry</strong>.",
            "📉 <strong>Low-vol multi-asset complement</strong>: Combines stable bond income with low-correlation carry alpha—an <strong>ideal fit</strong> for defensive investors seeking capital efficiency and diversification without abandoning the bond anchor.",
        ],
        "tim_note": "Tim Wei does not hold RSBY.",
    },
    "rsba": {
        "display_name": "Bonds & Merger Arbitrage",
        "tagline": "100% US Treasuries plus 100% merger arbitrage—event-driven overlay on a Treasury base.",
        "layers": [
            (
                "Layer 1 · US Treasuries 100%",
                "US Treasury futures and related rate exposure.",
            ),
            (
                "Layer 2 · Merger arbitrage 100%",
                "Passive tracking of a merger-arbitrage index; long/short baskets in announced deals.",
            ),
        ],
        "why": [
            "🤝 <strong>Treasuries plus event-driven merger arb</strong>: Layer 1 is <strong>100% US Treasury exposure</strong> as the defensive anchor. Layer 2 is <strong>100% merger arbitrage</strong>—buy announced targets, hedge acquirers, and earn the <strong>deal spread</strong> while completion risk remains.",
            "🎯 <strong>Equity-like but low correlation</strong>: Merger arb is event-driven; returns hinge on <strong>deal closure</strong>, not broad bull/bear markets. Historically low correlation to equities and roughly -0.02 to Treasuries—<strong>strong diversifier</strong> potential.",
            "⛱️ <strong>Umbrella outside bull markets</strong>: In equity selloffs or new bear phases, deal completion can be stressed, yet the strategy’s volatility and max drawdown have often been far below the broad market—with <strong>resilience and positive periods</strong> in many historical equity drawdowns.",
            "⚡ <strong>Upgrade the bond sleeve</strong>: Bond investors often face yield constraints. Convert 20% of bonds to RSBA to keep <strong>1:1 Treasury exposure</strong> while stacking <strong>20% merger arb</strong> for potential absolute-return increment on a conservative allocation.",
        ],
        "tim_note": "Tim Wei does not hold RSBA.",
    },
}

BENCHMARK_NOTES: dict[str, str] = {
    "rssb": "100/100 blend = 100% global stocks + 100% Treasury futures ladder - 100% financing leg (T-Bills). As of 2026-03-31, from Q1 2026 Commentary.",
    "rsst": "100/100 blend = 100% US stocks + 100% official managed-futures index - 100% financing leg (T-Bills). As of 2026-03-31.",
    "rssy": "As of 2026-03-31, from Q1 2026 Commentary.",
    "rsit": "100% international stocks / 100% CTA trend / -100% T-Bills. From RSIT Presentation.",
    "rssx": "RSSX has a shorter history; some benchmark periods are from Q1 2026 Commentary.",
    "rsbt": "100/100 blend = 100% US bonds + 100% official managed-futures index - 100% financing leg (T-Bills). As of 2026-03-31.",
    "rsby": "As of 2026-03-31, from Q1 2026 Commentary.",
    "rsba": "Merger arb tracks the AlphaBeta Merger Arbitrage Index. As of 2026-03-31.",
}

BACKTEST_NOTES: dict[str, str] = {
    "rssb": "100/100 blend per Product Brief / Presentation. Gross index returns, pre-tax; you cannot invest in an index.",
    "rsst": "100% US stocks / 100% CTA trend / -100% T-Bills, daily rebalance. From Presentation \"Stacking in Action\".",
    "rsit": "100% international stocks / 100% CTA trend / -100% T-Bills. From RSIT Presentation.",
    "rssx": "Gold/Bitcoin risk parity on 63-day vol, rebalanced monthly; Bitcoin financing cost assumed +1000 bps.",
}

REPLICATION_NOTES: dict[str, str] = {
    "rsst": "Three-year review since model launch (through 2026-02-07). RSST and RSBT share the same managed-futures replication framework.",
    "rsit": "Same managed-futures replication framework as RSST (Q1 2026 Commentary).",
    "rsbt": "Three-year review since model launch (through 2026-02-07). RSST and RSBT share the same managed-futures replication framework.",
}
