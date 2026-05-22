# Chronicle

Investment chronicle product tree: ledger data, build pipeline, static site, and exports.

| Folder | Role |
|--------|------|
| `data/` | Source-of-truth JSON ledger |
| `build/` | Python tools that compile `data/` into site snapshots |
| `site/` | Public static website (GitHub Pages artifact root) |
| `export/` | Generated markdown summaries for handoff |

Build entry point:

```powershell
python chronicle/build/build_dashboard_data.py
```
