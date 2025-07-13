# backend/config/settings.py

from secrets.env_loader import get_env_var

# Craftable Credentials
CRAFTABLE_USERNAME = get_env_var("CRAFTABLE_USERNAME")
CRAFTABLE_PASSWORD = get_env_var("CRAFTABLE_PASSWORD")

# Google OAuth or API keys
GOOGLE_CLIENT_ID     = get_env_var("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_env_var("GOOGLE_CLIENT_SECRET")

# Optional values with fallback
LOG_LEVEL = get_env_var("LOG_LEVEL", required=False) or "INFO"
