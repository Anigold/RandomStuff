from backend.domain.models import Vendor
from typing import Dict


_VENDORS: Dict[str, Vendor] = {}

def register_vendor(formatter: BaseFormatter) -> None:
    '''Register a formatter by its format_name() key.'''
    _FORMATTERS[formatter.format_name()] = formatter

def get_formatter(fmt: str) -> BaseFormatter:
    '''Retrieve a formatter by name, raises KeyError if not found.'''
    return _FORMATTERS[fmt]