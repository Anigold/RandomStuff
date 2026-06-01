from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_FILE = PROJECT_ROOT / "requirements.txt"


def install_package(package: str) -> None:
    package = package.strip()

    if not package:
        raise ValueError("Package name cannot be empty.")

    subprocess.run(
        [sys.executable, "-m", "pip", "install", package],
        check=True,
    )

    update_requirements()


def update_requirements() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pip", "freeze"],
        check=True,
        capture_output=True,
        text=True,
    )

    REQUIREMENTS_FILE.write_text(
        result.stdout,
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Install a pip package and update requirements.txt."
    )

    parser.add_argument(
        "package",
        help="Package spec to install, e.g. requests, openpyxl, or openpyxl==3.1.5",
    )

    args = parser.parse_args()

    install_package(args.package)

    print(f"Installed {args.package}")
    print(f"Updated {REQUIREMENTS_FILE}")


if __name__ == "__main__":
    main()