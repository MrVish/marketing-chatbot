#!/usr/bin/env python3
"""
Startup script for the AI Marketing Chatbot backend.
"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env file not found!")
        print("Please copy config_template.txt to .env and update with your OpenAI API key.")
        print("\nExample:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("LLM_MODEL=gpt-4o-mini")
        print("DATABASE_URL=sqlite:///marketing.db")
        print("ALLOWED_ORIGINS=*")
        return 1
    
    # Check if database exists
    db_file = Path("marketing.db")
    if not db_file.exists():
        print("⚠️  marketing.db not found!")
        print("Please ensure the database file is in the current directory.")
        return 1
    
    print("🚀 Starting AI Marketing Chatbot Backend...")
    print("📊 Backend will be available at: http://localhost:8000")
    print("📋 API docs will be available at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        # Start the FastAPI server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "backend.app.main:app", 
            "--reload", 
            "--port", "8001",
            "--host", "0.0.0.0"
        ], check=True)
    except KeyboardInterrupt:
        print("\n✅ Backend stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())