#!/bin/bash

echo "🚀 Setting up Scheduling Assistant powered by Google Gemini"
echo "========================================================="

# Check if Google API key is set
if [ -z "$GOOGLE_API_KEY" ] && [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: No Google API key found!"
    echo ""
    echo "Please set your Google API key first:"
    echo "export GOOGLE_API_KEY=\"your-api-key-here\""
    echo ""
    echo "Get your API key from: https://makersuite.google.com/app/apikey"
    echo ""
    read -p "Continue without API key? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo "✅ Google API key found!"
fi

# Install Python dependencies
echo ""
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Python dependencies"
    exit 1
fi

echo "✅ Python dependencies installed successfully"

# Install Node.js dependencies
echo ""
echo "📦 Installing Node.js dependencies..."
cd ../camp-scheduler
npm install

if [ $? -ne 0 ]; then
    echo "❌ Failed to install Node.js dependencies"
    exit 1
fi

echo "✅ Node.js dependencies installed successfully"

# Create start script
echo ""
echo "📝 Creating start script..."
cat > ../start_both.sh << 'EOF'
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
EOF

chmod +x ../start_both.sh

echo "✅ Setup completed successfully!"
echo ""
echo "🎉 Ready to use the Scheduling Assistant!"
echo "========================================"
echo ""
echo "To start both servers, run:"
echo "  ./start_both.sh"
echo ""
echo "Or start them separately:"
echo "  Backend:  cd backend && python start_server.py"
echo "  Frontend: cd camp-scheduler && npm run dev"
echo ""
echo "The scheduling assistant will be available at:"
echo "  http://localhost:5173"
echo ""
echo "Features:"
echo "  ✅ Powered by Google Gemini-2.5-Flash-Lite-Preview-06-17"
echo "  ✅ No token limits (8192 max tokens)"
echo "  ✅ Conversation context maintained"
echo "  ✅ Real-time responses"
echo "  ✅ Specialized for scheduling tasks"
echo "" 