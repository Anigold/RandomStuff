# backend/config/secrets.py

import os
from dotenv import load_dotenv

def get_env_variable(var_name: str, default=None):
    '''Fetches an environment variable, returns default if not found.'''
    return os.getenv(var_name, default)

load_dotenv()

class Secrets:
    """
    Dynamically loads all uppercase .env variables as attributes.
    Optional: restrict to a prefix like SECRET_ or CRAFTABLE_.
    """
    def __init__(self, prefix: str = ""):
        for key, value in os.environ.items():
            if key.isupper() and key.startswith(prefix):
                setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        secrets = {k: v for k, v in self.__dict__.items()}
        return f"<Secrets {secrets}>"

