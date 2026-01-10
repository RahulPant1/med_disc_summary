#!/bin/bash

# Discharge Summary Validator - Startup Script
# This script starts both backend and frontend servers

echo "==================================="
echo "Discharge Summary Validator MVP"
echo "==================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your API keys."
    echo "Copy .env.example to .env and add your keys."
    exit 1
fi

# Check if API keys are configured
if grep -q "your_gemini_api_key_here" .env || grep -q "your_anthropic_api_key_here" .env; then
    echo "⚠️  Warning: API keys appear to be placeholders."
    echo "Please update .env with your actual API keys."
    echo ""
fi

echo "Starting Backend Server..."
echo ""

# Start backend in background
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing backend dependencies..."
    pip install -r ../requirements.txt
    touch venv/.installed
fi

# Start backend
echo "Backend starting on http://localhost:8000"
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

cd ..

# Wait a moment for backend to start
sleep 3

echo ""
echo "Starting Frontend Server..."
echo ""

# Start frontend
cd frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Frontend starting on http://localhost:5173"
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "==================================="
echo "✅ Both servers are running!"
echo "==================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit 0
}

# Set trap to catch Ctrl+C
trap cleanup INT TERM

# Wait for background processes
wait
