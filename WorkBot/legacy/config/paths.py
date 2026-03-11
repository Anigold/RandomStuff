from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

BACKEND_DIR = BASE_DIR / 'backend'

# COMMON DIRECTORIES
CONFIG_DIR         = BASE_DIR / 'config'
LOGGER_DIR         = BACKEND_DIR / 'logger'
ORDERING_DIR       = BACKEND_DIR / 'ordering'
ORDER_FILES_DIR    = ORDERING_DIR / 'OrderFiles'
PRICING_DIR        = BACKEND_DIR / 'pricing'
VENDORS_DIR        = BACKEND_DIR / 'vendors'
STORES_DIR         = BACKEND_DIR / 'stores'
TRANSFERRING_DIR   = BACKEND_DIR / 'transferring'
TRANSFER_FILES_DIR = TRANSFERRING_DIR / 'TransferFiles'
DOWNLOADS_DIR      = BACKEND_DIR / 'downloads'
CREDENTIALS_DIR    = BACKEND_DIR / 'credentials'
ITEMS_DIR          = BACKEND_DIR / 'items'

# CONSTANT FILE PATHS
CLI_HISTORY_FILE = BASE_DIR / 'cli' / '.cli_history'
MASTER_LOG_FILE  = BASE_DIR / 'logs' / 'master.log'
STORES_DATA_FILE = STORES_DIR / 'stores.json'
ITEMS_DATA_FILE  = ITEMS_DIR / 'items.json'

