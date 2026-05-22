@echo off
setlocal
chcp 65001 >nul
set "SITE=%~dp0..\chronicle\site"
set "PORT=8765"
cd /d "%SITE%"
echo Local preview: http://127.0.0.1:%PORT%/
echo Press Ctrl+C to stop.
python -m http.server %PORT%
