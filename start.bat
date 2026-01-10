@echo off
REM Discharge Summary Validator - Startup Script for Windows
REM This script starts both backend and frontend servers

echo ===================================
echo Discharge Summary Validator MVP
echo ===================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo Error: .env file not found!
    echo Please create .env file with your API keys.
    echo Copy .env.example to .env and add your keys.
    pause
    exit /b 1
)

echo Starting Backend Server...
echo.

REM Start backend in new window
cd backend

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating Python virtual environment...
    python -m venv venv
)

REM Activate virtual environment and start backend
start "Backend Server" cmd /k "venv\Scripts\activate && pip install -r ../requirements.txt && uvicorn main:app --reload --port 8000"

cd ..

REM Wait for backend to start
timeout /t 5 /nobreak >nul

echo.
echo Starting Frontend Server...
echo.

REM Start frontend in new window
cd frontend

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)

start "Frontend Server" cmd /k "npm run dev"

cd ..

echo.
echo ===================================
echo Both servers are starting!
echo ===================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Check the opened terminal windows for server status.
echo Close the terminal windows to stop the servers.
echo.

pause
