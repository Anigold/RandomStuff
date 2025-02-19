from backend.helpers.selenium_helpers import create_driver, create_options
from backend.config import get_env_variable


def generate_craftablebot_args(downloads_path):
    """Generates and returns arguments needed to initialize CraftableBot."""
    
    # Generate a new Selenium driver
    driver = create_driver(create_options(downloads_path))

    # Fetch Craftable credentials securely
    username = get_env_variable("CRAFTABLE_USERNAME")
    password = get_env_variable("CRAFTABLE_PASSWORD")

    if not username or not password:
        raise ValueError("⚠️ Missing Craftable credentials in .env. Check your configuration.")

    return driver, username, password