@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Python 3.11+ is required. Run these setup commands in this folder:
  echo py -3 -m venv .venv
  echo .venv\Scripts\python.exe -m pip install .
  pause
  exit /b 1
)
".venv\Scripts\python.exe" -m sovereign_macro app
set "screener_exit=%ERRORLEVEL%"
pause
exit /b %screener_exit%
