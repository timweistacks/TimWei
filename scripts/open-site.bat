@echo off
setlocal
chcp 65001 >nul
set "ROOT=%~dp0.."
set "PORT=8766"
cd /d "%ROOT%"

echo.
echo [1/4] Rebuilding chronicle snapshot...
python "%ROOT%\chronicle\build\build_dashboard_data.py"
if errorlevel 1 (
  echo Failed to refresh chronicle snapshot.
  pause
  exit /b 1
)

echo [2/4] Rebuilding guide pages...
python "%ROOT%\chronicle\build\build_guide_pages.py"
if errorlevel 1 (
  echo Failed to rebuild guide pages.
  pause
  exit /b 1
)

echo [3/4] Exporting handoff summary...
python "%ROOT%\chronicle\build\export_current_summary.py"
if errorlevel 1 (
  echo Failed to export handoff summary.
  pause
  exit /b 1
)

echo [4/4] Starting local preview on port %PORT%...
start "ChronicleLocal" /MIN "%~dp0serve-site.bat"
timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:%PORT%/"
echo.
echo Browser opened: http://127.0.0.1:%PORT%/
echo If you see JSON like signal_receiver, port %PORT% is wrong or blocked.
echo Preview server runs minimized in taskbar title "ChronicleLocal".
echo.
exit /b 0
