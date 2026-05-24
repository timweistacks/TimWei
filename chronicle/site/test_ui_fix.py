import os
import re

def test_styles_css():
    print("Testing styles.css...")
    with open("styles.css", "r", encoding="utf-8") as f:
        content = f.read()
    
    # 檢查 .site-nav 中是否包含 position: sticky
    site_nav_match = re.search(r'\.site-nav\s*\{([^}]+)\}', content)
    if not site_nav_match:
        raise AssertionError(".site-nav selector not found in styles.css")
        
    site_nav_body = site_nav_match.group(1)
    if "position: sticky" not in site_nav_body:
        raise AssertionError("position: sticky not found in .site-nav styling")
    if "top: 1rem" not in site_nav_body:
        raise AssertionError("top: 1rem not found in .site-nav styling")
    if "z-index: 100" not in site_nav_body:
        raise AssertionError("z-index: 100 not found in .site-nav styling")

    # 檢查天平滑桿新樣式
    if ".deviation-slider-range" not in content:
        raise AssertionError(".deviation-slider-range style class not found in styles.css")
    
    print("[OK] styles.css test passed")

def test_locale_js():
    print("Testing locale.js...")
    with open("locale.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    # 檢查 nav.brand 翻譯是否已被改為 25歲貸款投資實錄
    brand_zh_match = re.search(r'"nav\.brand":\s*\{\s*en:\s*"[^"]+",\s*zh:\s*"([^"]+)"\s*\}', content)
    if not brand_zh_match:
        raise AssertionError("nav.brand translation not found or format incorrect in locale.js")
    
    if brand_zh_match.group(1) != "25歲貸款投資實錄":
        raise AssertionError(f"Expected nav.brand zh translation '25歲貸款投資實錄', got '{brand_zh_match.group(1)}'")
        
    # 檢查是否含有 hero.overview_title
    if "hero.overview_title" not in content:
        raise AssertionError("hero.overview_title key not found in locale.js")
        
    # 檢查是否包含 timeline 切換相關字串
    if "portfolio.view.table" not in content or "portfolio.view.timeline" not in content:
        raise AssertionError("Timeline switcher translation keys not found in locale.js")
        
    print("[OK] locale.js test passed")

def test_index_html():
    print("Testing index.html...")
    with open("index.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # 檢查導覽列 brand-block 預設文字
    if "25歲貸款投資實錄" not in content:
        raise AssertionError("Default brand-block text '25歲貸款投資實錄' not found in index.html")
        
    # 檢查 hero h1 中的 data-i18n
    if 'data-i18n="hero.overview_title"' not in content:
        raise AssertionError("data-i18n='hero.overview_title' not found in index.html hero h1")
        
    # 檢查 hero-tag 是否改為 meta.snapshot
    if 'data-i18n="meta.snapshot">快照' not in content:
        raise AssertionError("data-i18n='meta.snapshot' with '快照' not found in index.html hero-tag")
        
    # 檢查折線圖卡片是否移入 overview-primary-stack，且排在部位表上方
    idx_stack = content.find('class="overview-primary-stack"')
    idx_chart = content.find('class="card overview-chart-card"')
    idx_table = content.find('class="card overview-table-card"')
    
    if idx_stack == -1:
        raise AssertionError("overview-primary-stack block not found in index.html")
    if idx_chart == -1 or idx_chart < idx_stack:
        raise AssertionError("overview-chart-card (折線圖) not found inside or after overview-primary-stack")
    if idx_table == -1 or idx_table < idx_chart:
        raise AssertionError("overview-table-card (部位表) must be placed after overview-chart-card")

    # 檢查是否含有最新動態卡片與官網連結
    if "live-activity-section" not in content or "live-ticker-content" not in content:
        raise AssertionError("live-activity-section or live-ticker-content not found in index.html")
    if "strategy-official-link" not in content or "https://www.returnstackedetfs.com/" not in content:
        raise AssertionError("strategy-official-link pointing to returnstackedetfs.com not found in index.html")

    print("[OK] index.html test passed")

def test_details_html():
    print("Testing details.html...")
    with open("details.html", "r", encoding="utf-8") as f:
        content = f.read()
        
    # 檢查導覽列 brand-block 預設文字是否與 index.html 一致
    if "25歲貸款投資實錄" not in content:
        raise AssertionError("Default brand-block text '25歲貸款投資實錄' not found in details.html")
        
    # 檢查是否已成功移除 fx-flow-card
    if "fx-flow-card" in content:
        raise AssertionError("fx-flow-card still exists in details.html")
        
    # 檢查成交紀錄中是否加入 switcher
    if "portfolio-history-controls" not in content or "history-view-switcher" not in content:
        raise AssertionError("portfolio-history-controls or history-view-switcher not found in details.html")
        
    print("[OK] details.html test passed")

def test_app_js():
    print("Testing app.js...")
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 檢查天平渲染中是否已移除 🎯 EMOJI
    if "\\U0001f3af" in content or "🎯" in content:
        raise AssertionError("🎯 emoji or target symbol still found in app.js slider labels")

    # 檢查配置表中是否移除了 th.band (獨立容許帶欄位)
    if 'th.band' in content:
        raise AssertionError("Independent th.band column still exists in renderAllocationTable in app.js")

    # 檢查天平渲染中是否已整合 bandLow 和 bandHigh 區間
    if "bandLow" not in content or "bandHigh" not in content:
        raise AssertionError("bandLow/bandHigh ranges are not integrated into generateRebalanceSliderHtml")

    # 檢查是否包含時間軸渲染與切換邏輯
    if "currentHistoryViewMode" not in content:
        raise AssertionError("currentHistoryViewMode not found in app.js")
    if "tradeHistoryTimelineHtml" not in content or "sellHistoryTimelineHtml" not in content:
        raise AssertionError("tradeHistoryTimelineHtml or sellHistoryTimelineHtml function not found in app.js")

    # 檢查是否包含直播天數計時器與動態 Ticker 邏輯
    if "renderLiveTicker" not in content:
        raise AssertionError("renderLiveTicker function not found in app.js")

    print("[OK] app.js test passed")

if __name__ == "__main__":
    try:
        test_styles_css()
        test_locale_js()
        test_index_html()
        test_details_html()
        test_app_js()
        print("\nAll tests passed successfully!")
    except AssertionError as e:
        print(f"\nAssertion Error: {e}")
        exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        exit(1)
