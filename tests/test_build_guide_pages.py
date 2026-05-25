import unittest
from pathlib import Path

class TestBuildGuidePages(unittest.TestCase):
    def setUp(self):
        self.site_dir = Path(r"d:\Tim work station\25-45 6000 Tsenyu\chronicle\site")
        self.etf_dir = self.site_dir / "etfs"

    def test_files_exist(self):
        """驗證生成的靜態 HTML 檔案是否存在。"""
        self.assertTrue((self.site_dir / "learn.html").exists())
        self.assertTrue((self.site_dir / "layer2.html").exists())
        self.assertTrue((self.site_dir / "etfs.html").exists())
        self.assertTrue((self.site_dir / "guide-locale.js").exists())
        
        # 驗證 8 個 ETF 詳情頁
        tickers = ["rssb", "rsst", "rssy", "rsit", "rssx", "rsbt", "rsby", "rsba"]
        for t in tickers:
            p = self.etf_dir / f"{t}.html"
            self.assertTrue(p.exists(), f"Missing {p}")

    def test_rssy_data(self):
        """驗證 RSSY 的費用率與績效數據是否正確寫入。"""
        rssy_html = (self.etf_dir / "rssy.html").read_text(encoding="utf-8")
        
        # 費用率應為 0.98%
        self.assertIn("0.98%", rssy_html)
        # 淨值回報 3個月應為 15.51%
        self.assertIn("15.51%", rssy_html)
        # 市價回報 3個月應為 15.85%
        self.assertIn("15.85%", rssy_html)
        # 成立以來 NAV 應為 7.32%
        self.assertIn("7.32%", rssy_html)

    def test_rsba_data(self):
        """驗證 RSBA 的費用率與績效數據是否正確寫入，特別是修正的數據錯置 Bug。"""
        rsba_html = (self.etf_dir / "rsba.html").read_text(encoding="utf-8")
        
        # 費用率應為 0.96%
        self.assertIn("0.96%", rsba_html)
        # 淨值回報 3個月應為 -0.67%
        self.assertIn("-0.67%", rsba_html)
        # 市價回報 3個月應為 -0.50%
        self.assertIn("-0.50%", rsba_html)
        # 併購套利指數 3個月為 0.57%
        self.assertIn("0.57%", rsba_html)
        # 併購套利指數 6個月為 2.12%
        self.assertIn("2.12%", rsba_html)

    def test_rsit_why_cards(self):
        """Verify RSIT why section renders as highlight cards."""
        rsit_html = (self.etf_dir / "rsit.html").read_text(encoding="utf-8")
        self.assertIn('class="why-grid"', rsit_html)
        self.assertIn('class="why-card"', rsit_html)
        self.assertIn("全球化資產配置的拼圖", rsit_html)
        self.assertNotIn('<ul class="guide-list"><li>全球化資產配置的拼圖', rsit_html)

    def test_layer2_compact_intro(self):
        layer2_html = (self.site_dir / "layer2.html").read_text(encoding="utf-8")
        self.assertIn('id="layer2-jump-nav"', layer2_html)
        self.assertNotIn("guide-l2-map-card", layer2_html)
        self.assertNotIn("逐一拆解", layer2_html)
        self.assertNotIn("五種第二層怎麼運作", layer2_html)
        self.assertNotIn("五種第二層策略", layer2_html)

    def test_learn_dilemma_card(self):
        learn_html = (self.site_dir / "learn.html").read_text(encoding="utf-8")
        self.assertIn("guide-dilemma-card", learn_html)
        self.assertIn("guide-dilemma-block-solution", learn_html)
        self.assertIn("guide-card-foot", learn_html)

if __name__ == "__main__":
    unittest.main()
