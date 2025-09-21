# from .csv_format import CSVFormat
# from .excel_format import ExcelFormat

# FORMATS = {
#     'csv': CSVFormat(),
#     'excel': ExcelFormat(),
#     'xlsx': ExcelFormat(),
# }

# def get_format(name: str):
#     fmt = FORMATS.get(name.lower())
#     if not fmt:
#         raise ValueError(f'Unsupported format: {name}')
#     return fmt
from typing import Dict, Type

from .base_format import BaseFormatter
from .excel_format import ExcelFormatter
from .csv_format import CsvFormatter

# Global registry of available formatters
FORMATTERS: Dict[str, BaseFormatter] = {}

def register_formatter(formatter: BaseFormatter) -> None:
    """Register a formatter by its format_name() key."""
    FORMATTERS[formatter.format_name()] = formatter

def get_formatter(fmt: str) -> BaseFormatter:
    """Retrieve a formatter by name, raises KeyError if not found."""
    return FORMATTERS[fmt]

# Pre-register built-in formatters
register_formatter(ExcelFormatter())
register_formatter(CsvFormatter())
