from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


API_HOST = "127.0.0.1"
API_PORT = "8000"
FRONTEND_PORT = "5173"


def run_checked(command: list[str], cwd: Path) -> None:
    print()
    print(" ".join(command))
    subprocess.check_call(command, cwd=cwd)


def get_venv_python(project_root: Path) -> Path:
    venv_dir = project_root / ".venv"

    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"

    return venv_dir / "bin" / "python"


def ensure_venv(project_root: Path) -> Path:
    venv_python = get_venv_python(project_root)

    if venv_python.exists():
        print(f"Using virtual environment: {venv_python}")
        return venv_python

    print("No virtual environment found.")
    print("Creating .venv...")

    run_checked(
        [sys.executable, "-m", "venv", ".venv"],
        cwd=project_root,
    )

    if not venv_python.exists():
        raise RuntimeError(
            "Virtual environment was created, but Python was not found at: "
            f"{venv_python}"
        )

    print(f"Created virtual environment: {venv_python}")
    return venv_python


def ensure_pip(venv_python: Path, project_root: Path) -> None:
    run_checked(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=project_root,
    )


def install_requirements_if_present(venv_python: Path, project_root: Path) -> None:
    requirements_file = project_root / "requirements.txt"

    if not requirements_file.exists():
        print()
        print("No requirements.txt found. Skipping dependency sync.")
        return

    print()
    print("Syncing virtual environment with requirements.txt...")

    run_checked(
        [
            str(venv_python),
            "-m",
            "pip",
            "install",
            "-r",
            str(requirements_file),
        ],
        cwd=project_root,
    )


def check_required_packages(venv_python: Path, project_root: Path) -> None:
    print()
    print("Checking required startup packages...")

    required_imports = [
        "uvicorn",
        "fastapi",
    ]

    for package_name in required_imports:
        result = subprocess.run(
            [
                str(venv_python),
                "-c",
                f"import {package_name}",
            ],
            cwd=project_root,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Required package is missing: {package_name}\n"
                f"Try running:\n"
                f"  {venv_python} -m pip install -r requirements.txt"
            )

    print("Startup packages look good.")


def check_frontend_present(project_root: Path) -> Path:
    frontend_dir = project_root / "apps" / "web" / "frontend"
    package_json = frontend_dir / "package.json"

    if not package_json.exists():
        raise RuntimeError(
            "React frontend package.json was not found at:\n"
            f"  {package_json}"
        )

    return frontend_dir


def ensure_frontend_dependencies(frontend_dir: Path) -> None:
    node_modules = frontend_dir / "node_modules"

    if node_modules.exists():
        print()
        print("Frontend dependencies already installed.")
        return

    print()
    print("Installing frontend dependencies...")

    run_checked(
        [get_npm_command(), "install"],
        cwd=frontend_dir,
    )


def get_process_creation_flags() -> int:
    if os.name == "nt":
        return subprocess.CREATE_NEW_PROCESS_GROUP

    return 0


def start_api(venv_python: Path, project_root: Path) -> subprocess.Popen:
    command = [
        str(venv_python),
        "-m",
        "uvicorn",
        "apps.api.main:app",
        "--host",
        API_HOST,
        "--port",
        API_PORT,
    ]

    print()
    print("Starting API server...")
    print(" ".join(command))

    return subprocess.Popen(
        command,
        cwd=project_root,
        creationflags=get_process_creation_flags(),
    )


def start_frontend(frontend_dir: Path) -> subprocess.Popen:
    npm_command = get_npm_command()

    command = [
        npm_command,
        "run",
        "dev",
        "--",
        "--host",
        "127.0.0.1",
        "--port",
        FRONTEND_PORT,
    ]

    print()
    print("Starting React frontend...")
    print(" ".join(command))

    return subprocess.Popen(
        command,
        cwd=frontend_dir,
        creationflags=get_process_creation_flags(),
    )


def terminate_process(
    process: subprocess.Popen,
    name: str,
    timeout_seconds: int = 5,
    kill_tree: bool = False,
) -> None:
    if process.poll() is not None:
        print(f"{name} parent process already stopped.")

        if os.name == "nt" and kill_tree:
            print(f"Ensuring {name} child processes are stopped...")
            kill_process_tree_windows(process.pid)

        return

    print(f"Stopping {name}...")

    try:
        process.terminate()
        process.wait(timeout=timeout_seconds)
        print(f"{name} parent process stopped.")

        if os.name == "nt" and kill_tree:
            print(f"Stopping {name} child processes...")
            kill_process_tree_windows(process.pid)

        print(f"{name} stopped cleanly.")
        return

    except subprocess.TimeoutExpired:
        print(f"{name} did not stop cleanly.")

        if os.name == "nt" and kill_tree:
            print(f"Killing {name} process tree...")
            kill_process_tree_windows(process.pid)
        else:
            process.kill()
            process.wait()

        print(f"{name} killed.")

def kill_process_tree_windows(pid: int) -> None:
    subprocess.run(
        [
            "taskkill",
            "/PID",
            str(pid),
            "/T",
            "/F",
        ],
        capture_output=True,
        text=True,
    )

def kill_processes_on_port_windows(port: str) -> None:
    result = subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            (
                f"Get-NetTCPConnection -LocalPort {port} "
                "-ErrorAction SilentlyContinue | "
                "Select-Object -ExpandProperty OwningProcess"
            ),
        ],
        capture_output=True,
        text=True,
    )

    pids = {
        line.strip()
        for line in result.stdout.splitlines()
        if line.strip().isdigit()
    }

    for pid in pids:
        subprocess.run(
            [
                "taskkill",
                "/PID",
                pid,
                "/T",
                "/F",
            ],
            capture_output=True,
            text=True,
        )

def stop_processes(processes: list[tuple[str, subprocess.Popen]]) -> None:
    # Stop frontend first, then API.
    for name, process in reversed(processes):
        terminate_process(
            process,
            name,
            kill_tree=name == "React frontend",
        )

    if os.name == "nt":
        kill_processes_on_port_windows(FRONTEND_PORT)


def wait_for_processes(processes: list[tuple[str, subprocess.Popen]]) -> int:
    print()
    print("Development servers are running.")
    print(f"API:      http://{API_HOST}:{API_PORT}")
    print(f"Frontend: http://127.0.0.1:{FRONTEND_PORT}")
    print()
    print("Press Ctrl+C to stop both servers.")

    while True:
        for name, process in processes:
            return_code = process.poll()

            if return_code is not None:
                print()
                print(f"{name} exited with code {return_code}.")
                return return_code

        time.sleep(0.5)

def get_npm_command() -> str:
    if os.name == "nt":
        return "npm.cmd"

    return "npm"

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]

    print("Starting WorkBot development environment...")
    print(f"Project root: {project_root}")

    os.chdir(project_root)

    venv_python = ensure_venv(project_root)

    print()
    print("Python executable:")
    print(venv_python)

    ensure_pip(venv_python, project_root)
    install_requirements_if_present(venv_python, project_root)
    check_required_packages(venv_python, project_root)

    frontend_dir = check_frontend_present(project_root)
    ensure_frontend_dependencies(frontend_dir)

    processes: list[tuple[str, subprocess.Popen]] = []

    try:
        api_process = start_api(venv_python, project_root)
        processes.append(("API server", api_process))

        frontend_process = start_frontend(frontend_dir)
        processes.append(("React frontend", frontend_process))

        return wait_for_processes(processes)

    except KeyboardInterrupt:
        print()
        print("Shutdown requested.")
        return 0

    finally:
        stop_processes(processes)


if __name__ == "__main__":
    raise SystemExit(main())