# Scripts

Windows shortcuts for local workflows. Run from Explorer or PowerShell.

| Script | Action |
|--------|--------|
| `open-site.bat` | Rebuild snapshot + guide pages, start local server, open `http://127.0.0.1:8766/` |
| `serve-site.bat` | Start local preview server only (port **8766**, serves `chronicle/site/`) |
| `export-summary.bat` | Rebuild snapshot and open `chronicle/export/current_summary.md` |

Both scripts run from the repository root (`%ROOT%` = parent of this folder).

**Note:** Port 8765 may be used by another local tool (e.g. `signal_receiver`). This project uses **8766** for the chronicle preview.
