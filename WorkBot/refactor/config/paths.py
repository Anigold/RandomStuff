from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASE_PATH    = BASE_DIR / "data" / "inventory.db"
ORDER_FILES_PATH = BASE_DIR / 'data' / 'orders'
CLI_HISTORY_FILE = BASE_DIR / 'data' / 'cli' / '.cli_history'
MASTER_LOG_FILE  = BASE_DIR / 'data' / 'logging' / 'master.log'
DOWNLOADS_PATH   = BASE_DIR / 'data' / 'downloads'
CREDENTIALS_DIR  = BASE_DIR / 'config' / 'secrets'
