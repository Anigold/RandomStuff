from datetime import datetime
import re

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
        
def string_to_datetime(date_string: str) -> datetime:
    '''
    Attempts to convert an arbitrary date string into a datetime object.
    
    Supports formats like:
    - '2025-02-12'
    - '20250212'
    - '12-02-2025'
    - 'Feb 12, 2025'
    - 'February 12 2025'
    - '02/12/2025'
    '''
    formats = [
        '%Y-%m-%d',    # 2025-02-12
        '%Y%m%d',      # 20250212
        '%d-%m-%Y',    # 12-02-2025
        '%b %d, %Y',   # Feb 12, 2025
        '%B %d %Y',    # February 12 2025
        '%m/%d/%Y',    # 02/12/2025
        '%d/%m/%Y',    # 12/02/2025 (European format)
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue

    raise ValueError(f'Could not parse date: {date_string}')

def datetime_to_string(datetime_obj: datetime, format: str = '%Y%m%d') -> str:
     return datetime_obj.strftime(format)

NAME_TO_IDX = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
IDX_TO_NAME = {v: k.capitalize() for k, v in NAME_TO_IDX.items()}

def iso_today() -> str:
    return datetime.date.today().isoformat()

def weekday_index_of(date_iso: str) -> int:
    return datetime.date.fromisoformat(date_iso).weekday()

def weekday_name_of(date_iso: str) -> str:
    return IDX_TO_NAME[weekday_index_of(date_iso)]

_TIME_RE = re.compile(r"^\s*(\d{1,2})(?::(\d{2}))?\s*(AM|PM|am|pm)?\s*$")

def normalize_time_str(s: str | None) -> str | None:
    if not s:
        return None
    s = s.strip()
    m = _TIME_RE.match(s)
    if not m:
        # try flexible datetime parsing fallbacks
        for fmt in ("%I:%M %p", "%I %p", "%H:%M", "%H"):
            try:
                t = datetime.strptime(s, fmt).time()
                return f"{t.hour:02d}:{t.minute:02d}"
            except ValueError:
                pass
        return None

    hour   = int(m.group(1))
    minute = int(m.group(2)) if m.group(2) is not None else 0
    am_pm   = m.group(3).lower() if m.group(3) else None

    if am_pm == "pm" and hour != 12:
        hour += 12
    if am_pm == "am" and hour == 12:
        hour = 0

    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None

    return f"{hour:02d}:{minute:02d}"
