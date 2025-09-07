# backend/utils/days.py
import datetime as _dt

NAME_TO_IDX = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
}
IDX_TO_NAME = {v: k.capitalize() for k, v in NAME_TO_IDX.items()}

def iso_today() -> str:
    return _dt.date.today().isoformat()

def weekday_index_of(date_iso: str) -> int:
    return _dt.date.fromisoformat(date_iso).weekday()

def weekday_name_of(date_iso: str) -> str:
    return IDX_TO_NAME[weekday_index_of(date_iso)]
