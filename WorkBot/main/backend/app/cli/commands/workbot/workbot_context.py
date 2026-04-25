from typing import List

class WorkBotCommandContext:
    """Shared utilities and state for all CLI commands."""

    def __init__(self, workbot):
        self.workbot = workbot

    # ---- Convenience Helpers ----
    def get_stores(self) -> List[str]:
        """Return all known store names."""
        try:
            return [store.name for store in self.workbot.list_all_stores()]
        except Exception as e:
            print(f"[Warning] Could not load stores: {e}")
            return []

    def get_vendors(self) -> List[str]:
        """Return all known vendor names."""
        try:
            return sorted([vendor.name for vendor in self.workbot.list_all_vendors()])
        except Exception as e:
            print(f"[Warning] Could not load vendors: {e}")
            return []
        
    def get_items(self) -> List[str]:
        """Return all known item names."""
        try:
            return sorted(
                {
                    item.name.strip()
                    for item in self.workbot.list_all_items()
                    if getattr(item, "name", None) and item.name.strip()
                }
            )
        except Exception as e:
            print(f"[Warning] Could not load items: {e}")
            return []