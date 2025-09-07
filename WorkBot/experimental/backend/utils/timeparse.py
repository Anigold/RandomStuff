import re
from datetime import datetime

# Accepts "3 PM", "3:00 pm", "15:00", "15", "10:30 AM"
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
