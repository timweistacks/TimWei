@echo off
setlocal
chcp 65001 >nul
set "SITE=%~dp0..\chronicle\site"
set "PORT=8766"
cd /d "%SITE%"
echo.
echo [Chronicle] Local site preview
echo   Folder: %SITE%
echo   URL:    http://127.0.0.1:%PORT%/
echo   Stop:   Ctrl+C in this window
echo.
python -m http.server %PORT% --bind 127.0.0.1
if errorlevel 1 (
  echo.
  echo Failed to start server on port %PORT%.
  echo Port may be in use. Close other preview windows or change PORT in serve-site.bat
  pause
)
