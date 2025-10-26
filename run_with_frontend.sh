#!/bin/bash

# Job Finder - Run with Frontend
# This script starts both the backend API and frontend dev server

set -e

echo "=================================="
echo "Job Finder - Full Stack Runner"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}Error: Python virtual environment not found${NC}"
    echo "Please run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Check if Node modules are installed
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    cd frontend && npm install && cd ..
fi

echo -e "${BLUE}Starting Job Finder Full Stack...${NC}"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Flask backend in background
echo -e "${GREEN}[1/2] Starting Flask API Server...${NC}"
source venv/bin/activate
python api/server.py &
BACKEND_PID=$!

# Wait for backend to be ready
echo "Waiting for backend to start..."
sleep 5

# Start Vite frontend in background
echo -e "${GREEN}[2/2] Starting React Frontend...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "=================================="
echo -e "${GREEN}Servers Started Successfully!${NC}"
echo "=================================="
echo ""
echo -e "${BLUE}Backend API:${NC}  http://localhost:5000"
echo -e "${BLUE}Frontend UI:${NC}  http://localhost:5173"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all servers${NC}"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
