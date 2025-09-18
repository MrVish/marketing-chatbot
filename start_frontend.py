#!/usr/bin/env python3
"""
Startup script for the AI Marketing Chatbot frontend.
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def check_backend():
    """Check if backend is running"""
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("Please copy config_template.txt to .env and update with your OpenAI API key.")
        return 1
    
    print("🔍 Checking if backend is running...")
    if not check_backend():
        print("⚠️  Backend not detected at http://localhost:8000")
        print("Please start the backend first using: python start_backend.py")
        print("Or run: uvicorn backend.app.main:app --reload --port 8000")
        return 1
    
    print("✅ Backend is running!")
    print("🚀 Starting AI Marketing Chatbot Frontend...")
    print("🌐 Frontend will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Start the Streamlit app
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "frontend/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ Frontend stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())