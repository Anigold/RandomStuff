from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ====================================
# ||         DATA STORAGE           ||                 
# ====================================
DATA_STORAGE_DIR = BASE_DIR / 'data'

ORDER_FILES_DIR         = DATA_STORAGE_DIR / 'orders'
ORDER_ARCHIVE_FILES_DIR = DATA_STORAGE_DIR / 'order_archive'
CLI_HISTORY_FILE        = DATA_STORAGE_DIR / 'cli' / '.cli_history'
MASTER_LOG_FILE         = DATA_STORAGE_DIR / 'logging' / 'master.log'
DOWNLOADS_PATH          = DATA_STORAGE_DIR / 'downloads'
UPLOAD_FILES_DIR        = DATA_STORAGE_DIR / 'upload_files'
ITEMS_DATA_FILE         = DATA_STORAGE_DIR / 'items'

TRANSFER_FILES_DIR         = DATA_STORAGE_DIR / 'transfers'
TRANSFER_ARCHIVE_FILES_DIR = DATA_STORAGE_DIR / 'transfer_archive'

AUDIT_FILES_DIR         = DATA_STORAGE_DIR / 'audits'
AUDIT_ARCHIVE_FILES_DIR = DATA_STORAGE_DIR / 'audit_archive'

TODOS_DIR = DATA_STORAGE_DIR / 'todos'

DATABASE_PATH = DATA_STORAGE_DIR / 'inventory.db'

# ====================================
# ||      INFRASTRUCTURE DATA       ||
# ====================================
INFRA_FILE_STORAGE_DIR = BASE_DIR / 'backend' / 'infra' / 'config'

VENDOR_FILES_DIR = INFRA_FILE_STORAGE_DIR / 'vendors'
STORE_FILES_DIR  = INFRA_FILE_STORAGE_DIR / 'stores'

# ====================================
# ||            SECRETS             ||
# ====================================
CREDENTIALS_DIR    = BASE_DIR / 'config' / 'secrets'