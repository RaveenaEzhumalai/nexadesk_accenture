@echo off
title NexaDesk AI Service Desk
color 0A & cls
echo.
echo  ==========================================
echo    NexaDesk -- Agentic AI Service Desk
echo  ==========================================
echo.

:: Always run from THIS file's directory
cd /d "%~dp0backend"
echo  Working directory: %CD%
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found!
    echo  Install from: https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" during install!
    pause & exit /b 1
)
for /f "tokens=*" %%i in ('python --version 2^>^&1') do echo  Python: %%i

:: Create venv if not exists
if not exist "venv\Scripts\activate.bat" (
    echo  Creating virtual environment...
    python -m venv venv
    if errorlevel 1 ( echo  ERROR creating venv! & pause & exit /b 1 )
)
echo  Virtual environment: OK

:: Activate venv
call venv\Scripts\activate.bat

:: Install packages if needed
python -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo  Installing packages -- please wait 2-3 minutes...
    pip install -r requirements.txt
    if errorlevel 1 ( echo  ERROR installing packages! & pause & exit /b 1 )
)
echo  Packages: OK

:: Create logs folder
if not exist "logs" mkdir logs
echo  Logs folder: OK

echo.
echo  ==========================================
echo    SERVER STARTING...
echo  ------------------------------------------
echo    Frontend : Open ..\frontend\index.html
echo    API Docs : http://localhost:8000/docs
echo    Login    : admin@nexadesk.com
echo    Password : Admin@123
echo  ------------------------------------------
echo    Press Ctrl+C to stop
echo  ==========================================
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
pause
