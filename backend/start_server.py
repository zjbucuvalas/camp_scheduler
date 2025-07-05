#!/usr/bin/env python3
"""
Simple script to start the scheduling assistant backend server.
"""
import os
import sys
import subprocess

def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'httpx',
        'pydantic'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def check_api_key():
    """Check if Google API key is set"""
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  Warning: No Google API key found!")
        print("Please set either GOOGLE_API_KEY or GEMINI_API_KEY environment variable")
        print("Get your API key from: https://makersuite.google.com/app/apikey")
        print()
        return False
    
    print(f"✅ Google API key found: {api_key[:8]}...")
    return True

def main():
    print("🚀 Starting Scheduling Assistant Backend Server")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Check API key
    if not check_api_key():
        response = input("Continue without API key? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("\n🔧 Server Configuration:")
    print("- Host: localhost")
    print("- Port: 8000")
    print("- Model: gemini-2.5-flash-lite-preview-06-17")
    print("- Max Tokens: 8192 (no limit)")
    print("- Frontend CORS: http://localhost:5173, http://localhost:3000")
    print()
    
    # Start the server
    try:
        print("🌟 Starting server...")
        print("📱 Open your React app and try the chat!")
        print("🔗 API Health Check: http://localhost:8000/api/health")
        print("📋 API Documentation: http://localhost:8000/docs")
        print()
        print("Press Ctrl+C to stop the server")
        print("-" * 50)
        
        # Run the server
        subprocess.run([
            "python3", "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 