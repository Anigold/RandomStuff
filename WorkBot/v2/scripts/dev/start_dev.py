from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    project_root = Path(__file__).resolve().parents[1]

    print("Starting WorkBot dev environment...")
    print(f"Project root: {project_root}")
    print(f"Python: {sys.executable}")

    os.chdir(project_root)

    try:
        import uvicorn  # noqa: F401
    except ImportError:
        print()
        print("ERROR: uvicorn is not installed in this Python environment.")
        print("Install it with:")
        print("  python -m pip install uvicorn")
        return 1

    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "apps.api.main:app",
        "--reload",
    ]

    print()
    print("Starting API server...")
    print(" ".join(command))

    return subprocess.call(command, cwd=project_root)


if __name__ == "__main__":
    raise SystemExit(main())