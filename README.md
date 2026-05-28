# Investment Chronicle | 投資史冊

公開、可驗證的個人投資紀錄：持倉、交易、NAV、貸款攤還、再平衡與配息；另含 Return Stacked 教材與 ETF 百科（中／英切換）。原始 JSON 與靜態網站同 repo 保存。

> **Live site:** https://timweistacks.github.io/TimWei/

---

## 目錄結構

```
.
├── chronicle/              # 投資史冊（資料 + 建置 + 網站）— 公開核心
│   ├── data/               # 帳本 JSON（source of truth）
│   ├── build/              # Python 建置腳本
│   ├── site/               # 靜態網站（GitHub Pages 根目錄）
│   │                       #   index / details = 實測儀表板
│   │                       #   learn / layer2 / etfs = 教材與 ETF 百科
│   └── export/             # 自動產生的交接摘要
├── research/               # 選用：量化研究（公開 repo 內，不影響 Pages 部署）
├── scripts/                # 本機捷徑（.bat）
├── tests/                  # 建置與 guide 頁面測試
├── .github/workflows/      # 自動 build + 部署
├── requirements.txt
└── LICENSE
```

### 本機專用（不推送 GitHub）

| 路徑 | 說明 |
|------|------|
| `.cursor/` | Cursor IDE 設定 |
| `.agents/` | Cursor Agent Skills（UI 審查、impeccable 等） |
| `.impeccable/` | 本機 UI 審查報告 |
| `PRODUCT.md` / `DESIGN.md` | 本機設計筆記（impeccable teach 產物） |
| `AII/` | 私人研究 PDF、草稿 |
| `chronicle/__pycache__/` | Python 快取 |
| `site-config.local.js` | 本機覆寫 GA / 網址（若有） |

公開訪客只看 **`chronicle/site/`** 與 GitHub Actions 建置結果；其餘為開發或私人資料。

| 路徑 | 說明 |
|------|------|
| `chronicle/data/trades.json` | 成交紀錄 |
| `chronicle/data/portfolio.json` | 持倉與估值設定 |
| `chronicle/site/data/snapshot.json` | 網站快照（build 產生，勿手改） |
| `chronicle/export/current_summary.md` | AI / 人工交接摘要 |

---

## 本機使用

需求：Python 3.11+

```powershell
pip install -r requirements.txt
python chronicle/build/build_dashboard_data.py
python chronicle/build/build_guide_pages.py
python chronicle/build/export_current_summary.py
```

或雙擊 `scripts/open-site.bat`（依序 rebuild 儀表板快照、guide 頁、交接摘要，並開本機預覽 **8766**）。

| 腳本 | 用途 |
|------|------|
| `scripts/open-site.bat` | 完整 rebuild → 本機預覽 |
| `scripts/export-summary.bat` | rebuild 快照 + 摘要 |
| `scripts/serve-site.bat` | 只開本機伺服器（不 rebuild） |

改教材／ETF 百科／英文文案：編輯 `chronicle/build/build_guide_pages.py`、`guide_i18n_en.py`、`guide_etf_en.py` 後重跑 `build_guide_pages.py`（詳見 `chronicle/README.md`）。

---

## 發布到 GitHub Pages

### 1. 建立公開 repository

建議名稱：`TimWei`（你的 repo：[timweistacks/TimWei](https://github.com/timweistacks/TimWei)）

### 2. 推送

```powershell
cd "D:\Tim work station\25-45 6000 Tsenyu"
git init
git branch -M main
git add .
git commit -m "Initial public investment chronicle"
git remote add origin https://github.com/timweistacks/TimWei.git
git push -u origin main
```

### 3. 啟用 Pages

**Settings → Pages → Source → GitHub Actions**

部署完成後：`https://timweistacks.github.io/TimWei/`

### 4. 網站設定（必做）

編輯 `chronicle/site/site-config.js`：

```javascript
window.PERSONAL_LEDGER_SITE = {
  gaMeasurementId: "G-XXXXXXXXXX",
  siteUrl: "https://timweistacks.github.io/TimWei",
};
```

同步更新 `chronicle/site/robots.txt` 與 `chronicle/site/sitemap.xml` 中的網址。

---

## 流量追蹤（Google Analytics 4）

GitHub **Insights → Traffic** 只統計 repo 頁面，**不是**網站訪客。

1. [Google Analytics](https://analytics.google.com/) 建立 GA4 資源
2. 新增 Web 資料串流（填 GitHub Pages 網址）
3. 複製 Measurement ID（`G-XXXXXXXXXX`）
4. 填入 `chronicle/site/site-config.js` 的 `gaMeasurementId`
5. Push 後，在 GA4 **Reports → Realtime** 驗證

`gaMeasurementId` 留空時不載入追蹤 script。範例：`chronicle/site/site-config.example.js`

---

## 日常更新

| 情境 | 做法 |
|------|------|
| 改交易 / 持倉 | 編輯 `chronicle/data/*.json` → `git push` |
| 改教材 / ETF 頁 / 英文 | 改 `chronicle/build/` 下 guide 腳本 → `build_guide_pages.py` → `git push` |
| 每天 07:00 台灣更新報價 | GitHub Actions 排程自動 build 儀表板快照並部署 |
| 手動觸發 | Actions → **Publish Investment Chronicle** → Run workflow |

Actions 會 rebuild **儀表板快照**（`snapshot.*`、`current_summary.md`）並推回 repo；**guide 頁**需在本機跑 `build_guide_pages.py` 後一併 commit。

---

## 授權

MIT License — 見 [LICENSE](LICENSE)。
