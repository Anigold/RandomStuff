import json
import importlib
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR / "config_data"

VENDORS_PATH = BASE_DIR / 'vendors'
STORES_PATH = BASE_DIR / 'stores'

load_dotenv()

# Load JSON files dynamically
def load_json(file_name):
    with open(CONFIG_PATH / file_name, "r") as f:
        return json.load(f)

VENDORS       = load_json("vendors.json")["vendors"]
VENDOR_GROUPS = load_json('vendor_groups.json')

def get_vendor_bot(vendor_name: str):
    """Returns an instance of the correct bot for a given vendor."""
    vendor_info = VENDORS.get(vendor_name)
    if not vendor_info:
        raise ValueError(f"No vendor bot found for {vendor_name}")

    try:
        module = importlib.import_module(vendor_info["module_path"])
        bot_class = getattr(module, vendor_info["bot_class"])
        return bot_class
    except (ImportError, AttributeError) as e:
        raise ImportError(f"Could not load {vendor_info['bot_class']} for {vendor_name}: {e}")

def get_order_format(vendor_name):
    return VENDORS.get(vendor_name, {}).get("order_format", "CSV")

def vendor_requires_credentials(vendor_name):
    return VENDORS.get(vendor_name, {}).get("requires_credentials", False)

def vendor_uses_selenium(vendor_name):
    return VENDORS.get(vendor_name, {}).get("uses_selenium", False)

def get_min_order_value(vendor_name):
    return VENDORS.get(vendor_name, {}).get("min_order_value", 0)

def get_vendor_notes(vendor_name):
    return VENDORS.get(vendor_name, {}).get("special_notes", "")

def get_vendor_contacts(vendor_name):
    return VENDORS.get(vendor_name, {}).get('inside_contacts', '')

def get_special_notes(vendor_name):
    return VENDORS.get(vendor_name, {}).get('special_notes', '')

def get_vendor_information(vendor_name: str, requested_info: str):

    information = {
        "uses_selenium": vendor_uses_selenium,
        "requires_credentials": vendor_requires_credentials,
        "order_format": get_order_format,
        "min_order_value": get_min_order_value,
        "special_notes": get_special_notes,
        "internal_contacts": get_vendor_contacts
    }

    information_request_callback = information.get(requested_info)
    if not information_request_callback:
        raise ValueError(f"{requested_info} not valid request.")
    
    return information_request_callback(vendor_name)

def get_vendors(group_name: str = None) -> list:
    """Returns a list of vendors, either from a group or all vendors."""
    return VENDOR_GROUPS.get(group_name, VENDORS.keys()) if group_name else VENDORS.keys()
