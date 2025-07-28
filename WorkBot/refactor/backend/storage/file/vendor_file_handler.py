from .file_handler import FileHandler
from config.paths import VENDOR_FILES_DIR
from pathlib import Path
from backend.models.vendor import VendorInfo, ContactInfo, OrderingInfo, ScheduleEntry
import yaml

class VendorFileHandler(FileHandler):

    VENDOR_FILES_DIR = Path(VENDOR_FILES_DIR)

    def __init__(self):
        super().__init__(VENDOR_FILES_DIR)


    def load_all(self) -> dict[str, VendorInfo]:
        file_path = self.VENDOR_FILES_DIR / "vendors.yaml"

        with open(file_path, 'r', encoding='utf-8') as f:
            raw_data = yaml.safe_load(f)

        vendor_entries = raw_data.get("vendors", {})
        catalog = {}

        for name, entry in vendor_entries.items():
            try:
                # Parse internal contacts
                contacts = [ContactInfo(**c) for c in entry.get("internal_contacts", [])]

                # Parse schedule
                schedule_entries = entry.get("ordering", {}).get("schedule", [])
                schedule = [ScheduleEntry(**s) for s in schedule_entries]

                # Parse ordering info
                ordering = OrderingInfo(
                    method=entry.get("ordering", {}).get("method", []),
                    email=entry.get("ordering", {}).get("email", ""),
                    portal_url=entry.get("ordering", {}).get("portal_url", ""),
                    phone_number=entry.get("ordering", {}).get("phone_number", ""),
                    schedule=schedule
                )

                # Assemble final VendorInfo object
                catalog[name] = VendorInfo(
                    name=name,
                    order_format="",  # Not present in YAML
                    special_notes=entry.get("special_notes", ""),
                    min_order_value=entry.get("min_order_value", 0),
                    min_order_cases=entry.get("min_order_cases", 0),
                    internal_contacts=contacts,
                    ordering=ordering,
                    store_ids=entry.get("store_ids", {})
                )
            except Exception as e:
                print(f"Failed to load vendor '{name}': {e}", flush=True)

        return catalog
