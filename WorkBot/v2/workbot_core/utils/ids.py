from __future__ import annotations

import secrets
import string
from typing import Callable, Final


ALPHABET: Final[str] = string.ascii_uppercase + string.digits
DEFAULT_LENGTH: Final[int] = 10
MAX_GENERATION_ATTEMPTS: Final[int] = 25


class IdGenerationError(RuntimeError):
    """Raised when a unique ID could not be generated."""


class IdGenerator:
    
    _PREFIXES: Final[dict[str, str]] = {
        "vendor":            "ven",
        "item":              "itm",
        "store":             "str",
        "order":             "ord",
        "order_line":        "orl",
        "item_vendor_info":  "ivi",
        "item_store_info":   "isi",
        "audit":             "aud",
        "audit_line":        "aul",
        "transfer":          "trn",
        "transfer_line":     "trl",
        "purchase_log":      "plg",
        "purchase_log_line": "pll",
        "user":              "usr",
        "user_store_access": "usa",
        "inventory_count": "inc",
        "inventory_count_line": "icl",
    }

    @classmethod
    def generate(
        cls,
        entity_type: str,
        *,
        length: int = DEFAULT_LENGTH,
        exists: Callable[[str], bool] | None = None,
    ) -> str:
        prefix = cls._prefix_for(entity_type)

        for _ in range(MAX_GENERATION_ATTEMPTS):
            candidate = f"{prefix}_{cls._random_suffix(length)}"

            if exists is None or not exists(candidate):
                return candidate

        raise IdGenerationError(
            f"Could not generate unique ID for entity type '{entity_type}' "
            f"after {MAX_GENERATION_ATTEMPTS} attempts."
        )

    @classmethod
    def item_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("item", exists=exists)

    @classmethod
    def vendor_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("vendor", exists=exists)

    @classmethod
    def store_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("store", exists=exists)

    @classmethod
    def order_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("order", exists=exists)

    @classmethod
    def order_line_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("order_line", exists=exists)

    @classmethod
    def item_vendor_info_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("item_vendor_info", exists=exists)

    @classmethod
    def item_store_info_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("item_store_info", exists=exists)

    @classmethod
    def audit_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("audit", exists=exists)

    @classmethod
    def transfer_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("transfer", exists=exists)

    @classmethod
    def user_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("user", exists=exists)
    
    @classmethod
    def user_store_access_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("user_store_access", exists=exists)

    @classmethod
    def inventory_count_id(cls, *, exists: Callable[[str], bool] | None = None) -> str:
        return cls.generate("inventory_count", exists=exists)

    @classmethod
    def inventory_count_line_id(
        cls,
        *,
        exists: Callable[[str], bool] | None = None,
    ) -> str:
        return cls.generate("inventory_count_line", exists=exists)
    
    @classmethod
    def _prefix_for(cls, entity_type: str) -> str:
        try:
            return cls._PREFIXES[entity_type]
        except KeyError as exc:
            valid = ", ".join(sorted(cls._PREFIXES))
            raise ValueError(
                f"Unknown entity type '{entity_type}'. Valid types: {valid}"
            ) from exc

    @staticmethod
    def _random_suffix(length: int) -> str:
        if length <= 0:
            raise ValueError("ID suffix length must be greater than zero.")

        return "".join(secrets.choice(ALPHABET) for _ in range(length))