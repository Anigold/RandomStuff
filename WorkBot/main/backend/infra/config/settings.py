from .secrets.env_loader import get_env_variable

# Craftable Credentials
CRAFTABLE_USERNAME = get_env_variable('CRAFTABLE_USERNAME')
CRAFTABLE_PASSWORD = get_env_variable('CRAFTABLE_PASSWORD')

# Google OAuth or API keys
GOOGLE_CLIENT_ID     = get_env_variable('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = get_env_variable('GOOGLE_CLIENT_SECRET')

# Emailer Settings
EMAIL_PROVIDER = get_env_variable('WORKBOT_EMAIL_PROVIDER', 'outlook').lower()

# Optional values with fallback
LOG_LEVEL = get_env_variable('LOG_LEVEL') or 'INFO'

DEFAULT_TRANSFER_ORIGIN = 'Bakery'