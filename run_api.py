"""
Pixely Partners - Quick Start Scripts

This file provides commands to start the API server.

Usage:
    # Development mode (with auto-reload)
    python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

    # Production mode
    python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4

    # Direct execution
    python -m api.main
"""

# Development startup script
if __name__ == "__main__":
    import sys
    import os
    
    # Ensure we're in the right directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Development with auto-reload
    import subprocess
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "api.main:app",
        "--reload",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--log-level", "info"
    ]
    
    print("Starting Pixely Partners API (Development Mode)")
    print(f"Command: {' '.join(cmd)}")
    print("API will be available at: http://localhost:8000")
    print("Documentation: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop")
    
    subprocess.run(cmd)
