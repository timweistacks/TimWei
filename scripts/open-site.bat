@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0.."
set "SITE=%ROOT%\chronicle\site"
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

start "ChronicleLocal" /MIN cmd /c "cd /d \"%SITE%\" && python -m http.server %PORT%"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:%PORT%/"
exit /b 0
