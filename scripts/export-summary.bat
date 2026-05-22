@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0.."
cd /d "%ROOT%"

python "%ROOT%\chronicle\build\build_dashboard_data.py"
if errorlevel 1 (
  echo Failed to refresh chronicle snapshot.
  pause
  exit /b 1
)

python "%ROOT%\chronicle\build\export_current_summary.py"
if errorlevel 1 (
  echo Failed to export handoff summary.
  pause
  exit /b 1
)

start "" "%ROOT%\chronicle\export\current_summary.md"
exit /b 0
