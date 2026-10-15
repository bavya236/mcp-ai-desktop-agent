"""
1-Click Launcher for MCP AI Desktop Agent ("Talk to Your Computer").
Runs both FastAPI Backend and Vite Frontend concurrently.
"""

import sys
import os
import subprocess
import time
import webbrowser
from pathlib import Path

def main():
    root_dir = Path(__file__).parent.resolve()
    os.chdir(root_dir)

    print("=" * 65)
    print("🧠 Talk to Your Computer — MCP AI Desktop Agent")
    print("=" * 65)
    print(f"📁 Workspace: {root_dir}")

    # Determine Python executable
    venv_python = root_dir / ".venv" / "Scripts" / "python.exe"
    if not venv_python.exists():
        venv_python = sys.executable

    # 1. Populate Demo Sandbox
    print("\n📦 Ensuring Demo Sandbox is populated with sample PDFs & Code...")
    subprocess.run([str(venv_python), "-m", "backend.sample_data_gen"], cwd=str(root_dir))

    # 2. Start Backend Server
    print("\n⚡ Starting FastAPI Backend on http://localhost:8000...")
    backend_proc = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"],
        cwd=str(root_dir)
    )

    # 3. Start Frontend Dev Server
    print("✨ Starting Vite Frontend on http://localhost:5173...")
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    frontend_proc = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(root_dir / "frontend")
    )

    time.sleep(2)
    print("\n" + "=" * 65)
    print("✅ MCP Desktop Agent is LIVE!")
    print("🔗 Frontend Dashboard: http://localhost:5173")
    print("🔗 Backend API Docs:   http://localhost:8000/docs")
    print("=" * 65 + "\n")

    try:
        webbrowser.open("http://localhost:5173")
        backend_proc.wait()
        frontend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()

if __name__ == "__main__":
    main()
