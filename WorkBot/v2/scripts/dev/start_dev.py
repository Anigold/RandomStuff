from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(command: list[str], cwd: Path) -> int:
    print()
    print(" ".join(command))
    return subprocess.call(command, cwd=cwd)


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
        raise RuntimeError(f"Virtual environment was created, but Python was not found at: {venv_python}")

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


def start_api(venv_python: Path, project_root: Path) -> int:
    print()
    print("Starting API server...")

    return run(
        [
            str(venv_python),
            "-m",
            "uvicorn",
            "apps.api.main:app",
            "--reload",
        ],
        cwd=project_root,
    )


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

    return start_api(venv_python, project_root)


if __name__ == "__main__":
    raise SystemExit(main())