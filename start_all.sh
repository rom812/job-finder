#!/bin/bash

# Job Finder - Quick Start Script
# Starts both frontend and backend

echo "=================================="
echo "🚀 Job Finder - Quick Start"
echo "=================================="
echo ""

# Kill any existing processes on the ports
echo "🧹 Cleaning up existing processes..."
lsof -ti:5173 | xargs kill -9 2>/dev/null || true
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Start frontend
echo "📦 Starting Frontend (Vite)..."
cd frontend
npx vite &
FRONTEND_PID=$!
cd ..

# Wait a bit for frontend to start
sleep 3

# Start backend (without full dependencies for now)
echo "🐍 Starting Backend (Flask)..."
cd /Users/romsheynis/Documents/GitHub/job-finder

# Start the simple backend server
python3 simple_backend.py &
BACKEND_PID=$!

echo ""
echo "=================================="
echo "✅ All servers started!"
echo "=================================="
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🔌 Backend:  http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop all servers"
echo "=================================="

# Cleanup function
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $FRONTEND_PID $BACKEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for both processes
wait $FRONTEND_PID $BACKEND_PID
