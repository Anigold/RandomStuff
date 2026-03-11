from backend.infra.config.secrets.env_loader import get_env_variable
from datetime import datetime

def generate_craftablebot_args():
    username = get_env_variable('CRAFTABLE_USERNAME')
    password = get_env_variable('CRAFTABLE_PASSWORD')

    if not username or not password:
        raise ValueError('Missing Craftable credentials in .env. Check your configuration.')

    return username, password

def get_craftable_username_password():
    username = get_env_variable('CRAFTABLE_USERNAME')
    password = get_env_variable('CRAFTABLE_PASSWORD')

    if not username or not password:
        raise ValueError('Missing Craftable credentials in .env. Check your configuration.')

    return username, password

def convert_date_format(date_str: str, input_format: str, output_format: str) -> str:
        '''
        Converts a date string from one format to another.

        Args:
            date_str (str):      The date string to be converted.
            input_format (str):  The format of the input date string (e.g., '%m/%d/%Y').
            output_format (str): The desired output format (e.g., '%Y%m%d').

        Returns:
            str: The converted date string, or an error message if invalid.
        '''
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except ValueError:
            return f'Invalid date format: {date_str}. Expected format: {input_format}'
        
from functools import wraps

def with_session(login=False):
    """Decorator ensuring login/session state before action."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(self, *args, **kwargs):
            if login and not getattr(self, "is_logged_in", False):
                self.login()
            try:
                return fn(self, *args, **kwargs)
            finally:
                if getattr(self, "auto_close", False):
                    self.close()
        return wrapper
    return decorator







