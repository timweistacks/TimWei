@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0.."
set "PORT=8765"
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

start "ChronicleLocal" /MIN "%~dp0serve-site.bat"
timeout /t 3 /nobreak >nul
start "" "http://127.0.0.1:%PORT%/"
exit /b 0
