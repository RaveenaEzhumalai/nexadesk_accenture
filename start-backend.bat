@echo off
echo ========================================
echo  NexaDesk - Starting Backend
echo ========================================

cd backend

IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt -q

IF NOT EXIST .env (
    copy .env.example .env
    echo Created .env from template
)

echo.
echo ========================================
echo  Starting NexaDesk API on port 8000
echo  API Docs: http://localhost:8000/docs
echo  Login: admin@nexadesk.com / Admin@123
echo ========================================
echo.

uvicorn main:app --reload --host 0.0.0.0 --port 8000
