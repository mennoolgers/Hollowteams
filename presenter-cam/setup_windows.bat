@echo off
REM Double-click once to set up Presenter Cam on Windows.
REM Creates a private Python environment INSIDE this folder (.venv). Nothing system-wide.
cd /d "%~dp0"
where py >nul 2>nul || (echo Python was not found. Install Python 3.11+ from python.org first. & pause & exit /b 1)
py -3 -m venv .venv || (pause & exit /b 1)
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\python -m pip install -r requirements.txt
echo.
echo Setup finished.
pause
