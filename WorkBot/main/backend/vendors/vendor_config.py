import json
import importlib
from pathlib import Path
from backend.config import get_env_variable, BASE_DIR, get_full_path
import re

def load_json(file_path: Path):
    with open(file_path, "r") as f:
        return json.load(f)

VENDORS_PATH = get_full_path('vendors')

VENDORS       = load_json(VENDORS_PATH / 'vendors.json')["vendors"]
VENDOR_GROUPS = load_json(VENDORS_PATH / 'vendor_groups.json')

def get_vendor_information(vendor_name: str) -> dict:
    return VENDORS.get(vendor_name, {})

def get_vendors(group_name: str = None) -> list:
    """Returns a list of vendors, either from a group or all vendors."""
    return VENDOR_GROUPS.get(group_name, VENDORS.keys()) if group_name else VENDORS.keys()

def _sanitize_vendor_name_for_credentials(vendor_name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9]+', '_', vendor_name).upper()

def get_vendor_credentials(vendor_name: str):
    '''Returns a dictionary containing the username and password for a given vendor.'''
    sanitized_vendor_name = _sanitize_vendor_name_for_credentials(vendor_name)

    print(sanitized_vendor_name, flush=True)
    username = get_env_variable(f'{sanitized_vendor_name}_USERNAME')
    password = get_env_variable(f'{sanitized_vendor_name}_PASSWORD')

    if not username or not password:
        raise ValueError(f"Missing credentials for {vendor_name}. Check your .env file.")

    return {"username": username, "password": password}