# run_web_app.py
import subprocess
import sys
import os
from pathlib import Path
import platform
import shutil

ROOT_DIR = Path(__file__).parent.resolve()
FRONTEND_DIR = ROOT_DIR / "frontend"
RUN_FLASK_SCRIPT = ROOT_DIR / "run_flask.py"

def npm_cmd() -> str:
    # On Windows, npm is distributed as npm.cmd
    return "npm.cmd" if platform.system().lower().startswith("win") else "npm"

def ensure_frontend_ready() -> None:
    if not FRONTEND_DIR.exists():
        raise FileNotFoundError(f"Frontend directory not found: {FRONTEND_DIR}")
    if not (FRONTEND_DIR / "package.json").exists():
        raise FileNotFoundError(f"package.json not found in {FRONTEND_DIR}")

    # Check npm availability
    if shutil.which(npm_cmd()) is None:
        raise FileNotFoundError("npm not found in PATH. Install Node.js/npm and reopen your terminal.")

    # If node_modules doesn't exist, initialize the project once
    node_modules = FRONTEND_DIR / "node_modules"
    if not node_modules.exists():
        print("[INIT] node_modules not found. Running 'npm install'...")
        subprocess.check_call([npm_cmd(), "install"], cwd=FRONTEND_DIR, env=os.environ.copy())
        print("[INIT] npm install completed.")

def main():
    processes = []
    try:
        # 0) Make sure frontend is ready (npm installed + deps installed if missing)
        ensure_frontend_ready()

        # 1) Start Flask backend via your existing script
        print("[STARTING] Flask backend...")
        processes.append(
            subprocess.Popen(
                [sys.executable, str(RUN_FLASK_SCRIPT)],
                cwd=ROOT_DIR,
                env=os.environ.copy(),
            )
        )

        # 2) Start React frontend
        print("[STARTING] React frontend...")
        processes.append(
            subprocess.Popen(
                [npm_cmd(), "start"],
                cwd=FRONTEND_DIR,
                env=os.environ.copy(),
            )
        )

        # 3) Wait for both to exit
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        print("\n[STOPPING] Shutting down servers...")
        for p in processes:
            p.terminate()
        for p in processes:
            try:
                p.wait(timeout=5)
            except Exception:
                p.kill()
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        print("Hints:")
        print("  • Install Node.js from https://nodejs.org and ensure npm is on PATH.")
        print(f"  • Check that FRONTEND_DIR exists and has package.json: {FRONTEND_DIR}")
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")
        sys.exit(e.returncode)

if __name__ == "__main__":
    main()
