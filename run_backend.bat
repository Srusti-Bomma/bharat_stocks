@echo off
cd /d "%~dp0"
REM Minimal backend launcher (installs deps if uvicorn missing)
set "PY=python"
where py >nul 2>nul
if %ERRORLEVEL% EQU 0 set "PY=py -3"

REM Check uvicorn presence; install requirements if missing
%PY% -c "import uvicorn" 1>nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Installing Python dependencies...
  %PY% -m pip install --upgrade pip
  if exist requirements.txt (
    %PY% -m pip install -r requirements.txt
  ) else (
    %PY% -m pip install uvicorn fastapi requests python-dotenv SQLAlchemy pymysql
  )
)

REM Ensure python-multipart is present (required by FastAPI for forms)
%PY% -c "import multipart" 1>nul 2>nul
if %ERRORLEVEL% NEQ 0 (
  echo Installing python-multipart...
  %PY% -m pip install python-multipart
)

REM Ensure admin user exists silently (NO OUTPUT)
%PY% backend\init_admin.py >nul 2>&1

REM Start server normally
%PY% -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
if %ERRORLEVEL% NEQ 0 (
  echo Backend failed to start. See error above.
  pause
)
