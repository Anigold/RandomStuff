from abc import ABC, abstractmethod
from typing import List

class CommandContext:
    """Shared utilities and state for all CLI commands."""

    def __init__(self, workbot):
        self.workbot = workbot

    # ---- Convenience Helpers ----
    def get_stores(self) -> List[str]:
        """Return all known store names."""
        try:
            return [store.name for store in self.workbot.list_stores()]
        except Exception as e:
            print(f"[Warning] Could not load stores: {e}")
            return []

    def get_vendors(self) -> List[str]:
        """Return all known vendor names."""
        try:
            return sorted([vendor.name for vendor in self.workbot.list_vendors()])
        except Exception as e:
            print(f"[Warning] Could not load vendors: {e}")
            return []

class Command(ABC):

    name: str

    def __init__(self, context):
        self.context = context

    @abstractmethod
    def arguments(self):
        pass

    @abstractmethod
    def autocomplete(self, flag: str, text: str):
        pass

    @abstractmethod
    def command(self, args):
        pass

