#!/bin/bash

# Start the noise estimator backend and frontend

echo "Starting Noise Estimator Application..."
echo "======================================"

# Start the backend server in the background
echo "Starting backend server on port 8000..."
source venv/bin/activate
python backend_server.py &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 3

# Start the frontend
echo "Starting frontend on port 3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!

echo ""
echo "======================================"
echo "Application is running!"
echo "Frontend: http://localhost:3000"
echo "Backend API: http://localhost:8000"
echo "======================================"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "Servers stopped."
    exit
}

# Trap Ctrl+C and call cleanup
trap cleanup INT

# Wait for both processes
wait
