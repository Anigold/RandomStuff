from typing import Dict

from backend.core.interfaces.formatter import BaseFormatter
from .excel_format import ExcelFormatter
from .csv_format import CsvFormatter
from .json_format import JSONFormatter

from .vendor_formats import * 

from .craftable.audit_format import CraftableAuditFormatter

_FORMATTERS: Dict[str, BaseFormatter] = {

    'xlsx':               ExcelFormatter,
    'csv':                CsvFormatter,
    'json':               JSONFormatter,
    'sysco':              SyscoFormatter,
    'hill & markes':      HillNMarkesFormatter,
    'unfi':               UNFIFormatter, 
    'performance food':   PerformanceFoodFormatter,
    'us foods':           USFoodsFormatter,
    'audit':              CraftableAuditFormatter,
    'alberts organics':   AlbertsOrganicsFormatter,
}

def get_formatter(fmt: str) -> BaseFormatter:
    '''Retrieve a formatter by name, raises KeyError if not found.'''
    fmt = _sanitized_format_name(fmt)
    return _FORMATTERS[fmt]()

def _sanitized_format_name(format_name: str) -> str:
    return format_name.strip().lower().replace("'", '')