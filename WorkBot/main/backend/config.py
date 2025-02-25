import os
from dotenv import load_dotenv
from pathlib import Path



BASE_DIR = Path(__file__).parent

# Load environment variables
load_dotenv(dotenv_path=BASE_DIR.parent / '.env')

# Relative Paths
# Probably change this, but for now I want a centralized directory
PATHS = {
    "downloads": "downloads",
    "orders": "orders/OrderFiles",
    "pricing": "pricing",
    "transfers": "transferring",
    "logs": "logs",
    "schedules": "Schedules",
    'vendors': 'vendors',
}

LOG_FILES = {
    "app": "logs/app.log",
    "craftable_bot": "logs/craftable_bot.log",
    'master': 'logs/master.log'
}

def get_env_variable(var_name: str, default=None):
    """Fetches an environment variable, returns default if not found."""
    return os.getenv(var_name, default)

def get_full_path(path_key: str) -> Path:
    """Returns the absolute path for a given key from PATHS dictionary."""
    return BASE_DIR / PATHS.get(path_key, "")
