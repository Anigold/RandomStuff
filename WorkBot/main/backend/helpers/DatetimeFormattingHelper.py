from datetime import datetime

def string_to_datetime(date_string: str) -> datetime:
    """
    Attempts to convert an arbitrary date string into a datetime object.
    
    Supports formats like:
    - "2025-02-12"
    - "20250212"
    - "12-02-2025"
    - "Feb 12, 2025"
    - "February 12 2025"
    - "02/12/2025"
    """
    formats = [
        "%Y-%m-%d",    # 2025-02-12
        "%Y%m%d",      # 20250212
        "%d-%m-%Y",    # 12-02-2025
        "%b %d, %Y",   # Feb 12, 2025
        "%B %d %Y",    # February 12 2025
        "%m/%d/%Y",    # 02/12/2025
        "%d/%m/%Y",    # 12/02/2025 (European format)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f"Could not parse date: {date_string}")

def datetime_to_string(datetime_obj: datetime, format: str = '%Y%m%d') -> str:
     return datetime_obj.strftime(format)

def convert_date_format(date_str: str, input_format: str, output_format: str) -> str:
        """
        Converts a date string from one format to another.

        Args:
            date_str (str): The date string to be converted.
            input_format (str): The format of the input date string (e.g., "%m/%d/%Y").
            output_format (str): The desired output format (e.g., "%Y%m%d").

        Returns:
            str: The converted date string, or an error message if invalid.
        """
        try:
            date_obj = datetime.strptime(date_str, input_format)
            return date_obj.strftime(output_format)
        except ValueError:
            return f"Invalid date format: {date_str}. Expected format: {input_format}"