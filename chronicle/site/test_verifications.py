import os
import re

def test_styles_css_colors():
    print("Testing styles.css colors (red for up, green for down)...")
    with open("styles.css", "r", encoding="utf-8") as f:
        content = f.read()
        
    # 檢查 data-state="good" 是否為 var(--danger)
    good_state = re.search(r'\[data-state="good"\]\s*\{\s*color:\s*var\(--danger\);', content)
    if not good_state:
        raise AssertionError('[data-state="good"] color must be var(--danger) for red-up')
        
    # 檢查 data-state="bad" 是否為 var(--success)
    bad_state = re.search(r'\[data-state="bad"\]\s*\{\s*color:\s*var\(--success\);', content)
    if not bad_state:
        raise AssertionError('[data-state="bad"] color must be var(--success) for green-down')

    # 檢查 phase-target-delta.is-up 是否為 var(--danger) 及 var(--danger-soft)
    is_up = re.search(r'\.phase-target-delta\.is-up\s*\{\s*background:\s*var\(--danger-soft\);\s*color:\s*var\(--danger\);', content)
    if not is_up:
        raise AssertionError('.phase-target-delta.is-up styling must use danger for red-up')

    # 檢查 phase-target-delta.is-down 是否為 var(--success) 及 var(--success-soft)
    is_down = re.search(r'\.phase-target-delta\.is-down\s*\{\s*background:\s*var\(--success-soft\);\s*color:\s*var\(--success\);', content)
    if not is_down:
        raise AssertionError('.phase-target-delta.is-down styling must use success for green-down')
        
    # 檢查是否含有 .activity-item.is-highlighted 的動態焦點卡片樣式
    if ".activity-item.is-highlighted" not in content:
        raise AssertionError(".activity-item.is-highlighted styles not found in styles.css")

    print("[OK] styles.css color & carousel styles passed")

def test_app_js_changes():
    print("Testing app.js for fmtUsdSigned (+) and live ticker carousel...")
    with open("app.js", "r", encoding="utf-8") as f:
        content = f.read()

    # 檢查 fmtUsdSigned 中的正數加號邏輯
    if 'amount > 0 ? "+"' not in content:
        raise AssertionError("fmtUsdSigned positive values must include '+' sign")
        
    # 檢查 liveTickerInterval 是否存在且在 renderLiveTicker 中被呼叫
    if "window.liveTickerInterval" not in content or "clearInterval(window.liveTickerInterval)" not in content:
        raise AssertionError("liveTickerInterval management not found in app.js")

    print("[OK] app.js verified")

def test_locale_js_social():
    print("Testing locale.js FB group title...")
    with open("locale.js", "r", encoding="utf-8") as f:
        content = f.read()
        
    if '"social.join_fb": { en: "Join FB Return Stacking Group", zh: "加入 FB 報酬疊加交流社團" }' not in content:
        raise AssertionError("social.join_fb must be translated to Return Stacking Group and 報酬疊加交流社團")
    print("[OK] locale.js FB group title passed")

def test_styles_css_carousel_one():
    print("Testing styles.css for single card display (display: none by default)...")
    with open("styles.css", "r", encoding="utf-8") as f:
        content = f.read()
        
    # 檢查 .activity-item 預設是否為 display: none
    activity_item_none = re.search(r'\.activity-item\s*\{\s*display:\s*none;', content)
    if not activity_item_none:
        raise AssertionError(".activity-item must be hidden by default (display: none) for single-card carousel")
        
    # 檢查 .activity-item.is-highlighted 是否為 display: flex
    activity_item_flex = re.search(r'\.activity-item\.is-highlighted\s*\{\s*display:\s*flex;', content)
    if not activity_item_flex:
        raise AssertionError(".activity-item.is-highlighted must use display: flex to reveal active card")
        
    print("[OK] styles.css single card carousel passed")

def compare_bak_files():
    print("Comparing changed files with backups for safety...")
    files = ["styles.css", "app.js", "locale.js"]
    for fn in files:
        bak_fn = fn + ".bak"
        if not os.path.exists(bak_fn):
            raise AssertionError(f"Backup file {bak_fn} does not exist")
            
        with open(fn, "r", encoding="utf-8") as f:
            curr = f.read()
        with open(bak_fn, "r", encoding="utf-8") as f:
            bak = f.read()
            
        diff_len = len(curr) - len(bak)
        print(f"File {fn} vs {bak_fn} diff length: {diff_len} chars")
        if abs(diff_len) > 1000:
            raise AssertionError(f"Unexpected large file size diff between {fn} and {bak_fn}")
            
    print("[OK] Backup comparison passed")

if __name__ == "__main__":
    try:
        test_styles_css_colors()
        test_styles_css_carousel_one()
        test_app_js_changes()
        test_locale_js_social()
        compare_bak_files()
        print("\nAll custom verifications passed successfully!")
    except AssertionError as e:
        print(f"\nAssertion Error: {e}")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected Error: {e}")
        exit(1)
