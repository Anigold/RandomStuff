from dataclasses import dataclass
from pathlib import Path

AUDIT_TYPES = {'FULL', 'PARTIAL'}

@dataclass
class AuditItem:

    item_name:   str
    count_unit:  str
    on_hand:     str[float]
    category:    str
    subcategory: str
    unit_price:  str[float]
    total_price: str[float]

    
@dataclass
class Audit:

    store: str
    date: str
    audit_type: str
    auditor: str

    items: list[AuditItem]

    def load_items_from_sheet(self, sheet_path: Path) -> None:
        ...
    
    