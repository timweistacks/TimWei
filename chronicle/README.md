# Chronicle

Investment chronicle product tree: ledger data, build pipeline, static site, and exports.

| Folder | Role |
|--------|------|
| `data/` | Source-of-truth JSON ledger |
| `build/` | Python tools that compile `data/` into site snapshots |
| `site/` | Public static website (GitHub Pages artifact root) |
| `export/` | Generated markdown summaries for handoff |

Build entry points:

```powershell
python chronicle/build/build_dashboard_data.py
python chronicle/build/build_guide_pages.py
```

Before pushing to GitHub:

- Run both build commands above so `site/data/snapshot.*` and guide pages stay in sync.
- Do not commit local-only paths listed in the repo root `.gitignore` (e.g. `AII/`, `site-config.local.js`, build scratch `_stats_*.txt`).
- Guide HTML/CSS/JS under `chronicle/site/` are partly generated; edit `chronicle/build/build_guide_pages.py`, `guide_i18n_en.py`, and `guide_etf_en.py`, then re-run the guide build.
- GitHub Actions rebuilds the dashboard snapshot on schedule; it does **not** run `build_guide_pages.py` — commit generated guide files when you change guide sources.
