from dataclasses import dataclass
from pathlib import Path

AUDIT_TYPES = {'FULL', 'PARTIAL'}

@dataclass
class AuditItem:

    item_name:   str
    count_unit:  str
    on_hand:     str

    
@dataclass
class Audit:

    store: str
    date: str
    audit_type: str
    auditor: str

    items: list[AuditItem]

    