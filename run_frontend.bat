@echo off
cd /d "%~dp0\frontend"
REM Minimal frontend launcher (static server)
set "PORT=8080"
start "browser" http://127.0.0.1:%PORT%/index.html
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
  py -3 -m http.server %PORT%
) else (
  python -m http.server %PORT%
)
