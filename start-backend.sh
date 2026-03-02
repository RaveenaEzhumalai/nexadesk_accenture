#!/bin/bash
echo "========================================"
echo " NexaDesk - Starting Backend"
echo "========================================"

cd backend

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt -q

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from template"
fi

echo ""
echo "========================================"
echo " Starting NexaDesk API on port 8000"
echo " API Docs: http://localhost:8000/docs"
echo " Login: admin@nexadesk.com / Admin@123"
echo "========================================"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
