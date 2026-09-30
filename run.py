#!/usr/bin/env python3
"""
ResearchFlow AI Launch Assistant
Runs FastAPI Backend and Vite Frontend concurrently for local development.
"""
import os
import sys
import subprocess
import time
import shutil

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("=" * 60)
    print("ResearchFlow AI (Local Development Environment)")
    print("=" * 60)

    # Check for GROQ_API_KEY
    env_file = os.path.join(ROOT_DIR, ".env")
    if not os.path.exists(env_file):
        print("[!] Warning: .env file not found. Creating from .env.example...")
        example_file = os.path.join(ROOT_DIR, ".env.example")
        if os.path.exists(example_file):
            shutil.copy(example_file, env_file)

    # Detect python executable in venv or default
    venv_py = os.path.join(ROOT_DIR, ".venv", "Scripts", "python.exe") if os.name == 'nt' else os.path.join(ROOT_DIR, ".venv", "bin", "python")
    python_cmd = venv_py if os.path.exists(venv_py) else sys.executable

    print("\n1. Starting FastAPI Backend Server on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        [python_cmd, "-m", "uvicorn", "backend.api:app", "--reload", "--port", "8000"],
        cwd=ROOT_DIR
    )

    frontend_dir = os.path.join(ROOT_DIR, "frontend")
    print("2. Starting Vite Frontend Server on http://localhost:5173 ...")
    npm_cmd = "npm.cmd" if os.name == 'nt' else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=frontend_dir
    )

    print("\n" + "=" * 60)
    print("[*] Both Backend and Frontend are running!")
    print("   - Frontend UI: http://localhost:5173")
    print("   - Backend API: http://127.0.0.1:8000")
    print("   Press CTRL+C to terminate both servers.")
    print("=" * 60 + "\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        print("Done!")

if __name__ == "__main__":
    main()
