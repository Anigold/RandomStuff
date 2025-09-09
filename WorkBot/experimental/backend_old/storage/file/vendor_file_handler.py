from .file_handler import FileHandler
from config.paths import VENDOR_FILES_DIR, VENDORS_FILE
from pathlib import Path
from backend.models.vendor import VendorInfo, ContactInfo, OrderingInfo, ScheduleEntry
from typing import List, Optional
from backend.utils.timeparse import normalize_time_str

import yaml

class VendorFileHandler(FileHandler):

    VENDOR_FILES_DIR = Path(VENDOR_FILES_DIR)
    VENDORS_FILE = Path(VENDORS_FILE)

    def __init__(self, vendors_file: Path | None = None) -> None:
        super().__init__(VENDOR_FILES_DIR)
        self.vendors_file = vendors_file or VENDORS_FILE


    def load_all(self) -> dict[str, VendorInfo]:
        file_path = self.VENDORS_FILE

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)

        vendor_entries = raw_data.get('vendors', {})
        catalog = {}

        for name, entry in vendor_entries.items():
            try:
                # Parse internal contacts
                contacts = [ContactInfo(**c) for c in entry.get('internal_contacts', [])]

                # Parse schedule
                schedule_entries = entry.get('ordering', {}).get('schedule', [])
                schedule = [ScheduleEntry(**s) for s in schedule_entries]

                # Parse ordering info
                ordering = OrderingInfo(
                    method=entry.get('ordering', {}).get('method', []),
                    email=entry.get('ordering', {}).get('email', ''),
                    portal_url=entry.get('ordering', {}).get('portal_url', ''),
                    phone_number=entry.get('ordering', {}).get('phone_number', ''),
                    schedule=schedule
                )

                # Assemble final VendorInfo object
                catalog[name] = VendorInfo(
                    name=name,
                    order_format='',  # Not present in YAML
                    special_notes=entry.get('special_notes', ''),
                    min_order_value=entry.get('min_order_value', 0),
                    min_order_cases=entry.get('min_order_cases', 0),
                    internal_contacts=contacts,
                    ordering=ordering,
                    store_ids=entry.get('store_ids', {})
                )
            except Exception as e:
                print(f'Failed to load vendor "{name}": {e}', flush=True)

        return catalog
    
    def vendors_with_order_day(self, weekday_name: str) -> List[dict]:
        """
        Uses your typed load_all() to return a list of:
        { 'name': <vendor>, 'stores': [..], 'cutoff_time': 'HH:MM' | None }
        If multiple schedules match the same weekday, we pick the earliest cutoff.
        """
        catalog = self.load_all()  # dict[str, VendorInfo]
        target = (weekday_name or "").strip().lower()
        out: List[dict] = []

        for vname, vinfo in catalog.items():
            times: list[str] = []
            for s in (vinfo.ordering.schedule or []):
                if ((s.order_day or "").strip().lower() == target):
                    t = normalize_time_str(getattr(s, "cutoff_time", None))
                    times.append(t or "")

            if not times:
                continue

            non_empty = [t for t in times if t]
            cutoff: Optional[str] = (sorted(non_empty)[0] if non_empty else None)

            stores = list((vinfo.store_ids or {}).keys())
            out.append({"name": vname, "stores": stores, "cutoff_time": cutoff})

        return out
