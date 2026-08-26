# backend/app/cli/paths.py

from pathlib import Path


CLI_ROOT = Path(__file__).resolve().parents[0]

CLI_HISTORY_FILE = CLI_ROOT / ".cli_history"