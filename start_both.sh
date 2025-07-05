#!/bin/bash

echo "🚀 Starting Scheduling Assistant"
echo "================================"

# Function to kill background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Start backend server
echo "🔧 Starting backend server..."
cd backend
python3 start_server.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend server
echo "🎨 Starting frontend server..."
cd ../camp-scheduler
npm run dev &
FRONTEND_PID=$!

echo ""
echo "🌟 Both servers are starting up!"
echo "================================"
echo "📱 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:8000"
echo "📋 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"
echo ""

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 