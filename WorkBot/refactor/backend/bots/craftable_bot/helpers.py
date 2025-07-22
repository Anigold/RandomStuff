from config.secrets.env_loader import get_env_variable


def generate_craftablebot_args():
    username = get_env_variable("CRAFTABLE_USERNAME")
    password = get_env_variable("CRAFTABLE_PASSWORD")

    if not username or not password:
        raise ValueError("Missing Craftable credentials in .env. Check your configuration.")

    return username, password

def get_craftable_username_password():
    username = get_env_variable("CRAFTABLE_USERNAME")
    password = get_env_variable("CRAFTABLE_PASSWORD")

    if not username or not password:
        raise ValueError("Missing Craftable credentials in .env. Check your configuration.")

    return username, password

def convert_date_format(date_str: str, input_format: str, output_format: str) -> str:
        """
        Converts a date string from one format to another.

        Args:
            date_str (str):      The date string to be converted.
            input_format (str):  The format of the input date string (e.g., "%m/%d/%Y").
            output_format (str): The desired output format (e.g., "%Y%m%d").

        Returns:
            str: The converted date string, or an error message if invalid.
        """
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except ValueError:
            return f"Invalid date format: {date_str}. Expected format: {input_format}"