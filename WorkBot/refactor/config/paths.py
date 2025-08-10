from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_STORAGE_DIR   = BASE_DIR / 'data'
DATABASE_PATH      = DATA_STORAGE_DIR / 'inventory.db'
ORDER_FILES_DIR    = DATA_STORAGE_DIR / 'orders'
CLI_HISTORY_FILE   = DATA_STORAGE_DIR / 'cli' / '.cli_history'
MASTER_LOG_FILE    = DATA_STORAGE_DIR / 'logging' / 'master.log'
DOWNLOADS_PATH     = DATA_STORAGE_DIR / 'downloads'
STORES_DATA_FILE   = DATA_STORAGE_DIR / 'stores' / 'stores.json'
UPLOAD_FILES_DIR   = DATA_STORAGE_DIR / 'upload_files'
VENDOR_FILES_DIR   = DATA_STORAGE_DIR / 'vendors'
TRANSFER_FILES_DIR = DATA_STORAGE_DIR / 'transfers'

CREDENTIALS_DIR    = BASE_DIR / 'config' / 'secrets'