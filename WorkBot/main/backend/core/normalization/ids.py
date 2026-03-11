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
        "vendor": "ven",
        "item": "itm",
        "store": "str",
        "order": "ord",
        "audit": "aud",
        "transfer": "trn",
    }

    '''GENERATORS'''
    @classmethod
    def generate(
        cls,
        entity_type: str,
        *,
        length: int = DEFAULT_LENGTH,
    ) -> str:
        """
        Generate a prefixed random ID for a known entity type.

        Example:
            ven_A7K29QX46B
            itm_T9M2L8P1G7
        """
        prefix = cls._prefix_for(entity_type)
        token  = cls._random_token(length)
        return f"{prefix}_{token}"

    @classmethod
    def generate_unique(
        cls,
        entity_type: str,
        *,
        exists: Callable[[str], bool],
        length: int = DEFAULT_LENGTH,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> str:
        """
        Generate a unique ID by retrying until `exists(id_)` returns False.

        Args:
            entity_type: The logical entity type, e.g. "item", "vendor".
            exists: Callable that returns True if the ID already exists.
            length: Random token length, excluding prefix.
            max_attempts: Max retry attempts before failing.

        Raises:
            IdGenerationError: If a unique ID could not be generated.
        """
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")

        for _ in range(max_attempts):
            candidate = cls.generate(entity_type, length=length)
            if not exists(candidate):
                return candidate

        raise IdGenerationError(
            f"Failed to generate a unique ID for entity_type='{entity_type}' "
            f"after {max_attempts} attempts."
        )

    '''DOMAIN ID CONVENIENCE GENERATORS'''
    @classmethod
    def vendor_id(cls, *, length: int = DEFAULT_LENGTH) -> str:
        return cls.generate("vendor", length=length)

    @classmethod
    def item_id(cls, *, length: int = DEFAULT_LENGTH) -> str:
        return cls.generate("item", length=length)

    @classmethod
    def store_id(cls, *, length: int = DEFAULT_LENGTH) -> str:
        return cls.generate("store", length=length)

    @classmethod
    def order_id(cls, *, length: int = DEFAULT_LENGTH) -> str:
        return cls.generate("order", length=length)

    @classmethod
    def audit_id(cls, *, length: int = DEFAULT_LENGTH) -> str:
        return cls.generate("audit", length=length)

    @classmethod
    def transfer_id(cls, *, length: int = DEFAULT_LENGTH) -> str:
        return cls.generate("transfer", length=length)

    @classmethod
    def unique_vendor_id(
        cls,
        *,
        exists: Callable[[str], bool],
        length: int = DEFAULT_LENGTH,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> str:
        return cls.generate_unique(
            "vendor",
            exists=exists,
            length=length,
            max_attempts=max_attempts,
        )

    @classmethod
    def unique_item_id(
        cls,
        *,
        exists: Callable[[str], bool],
        length: int = DEFAULT_LENGTH,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> str:
        return cls.generate_unique(
            "item",
            exists=exists,
            length=length,
            max_attempts=max_attempts,
        )

    @classmethod
    def unique_store_id(
        cls,
        *,
        exists: Callable[[str], bool],
        length: int = DEFAULT_LENGTH,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> str:
        return cls.generate_unique(
            "store",
            exists=exists,
            length=length,
            max_attempts=max_attempts,
        )

    @classmethod
    def unique_order_id(
        cls,
        *,
        exists: Callable[[str], bool],
        length: int = DEFAULT_LENGTH,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> str:
        return cls.generate_unique(
            "order",
            exists=exists,
            length=length,
            max_attempts=max_attempts,
        )

    @classmethod
    def unique_audit_id(
        cls,
        *,
        exists: Callable[[str], bool],
        length: int = DEFAULT_LENGTH,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> str:
        return cls.generate_unique(
            "audit",
            exists=exists,
            length=length,
            max_attempts=max_attempts,
        )

    @classmethod
    def unique_transfer_id(
        cls,
        *,
        exists: Callable[[str], bool],
        length: int = DEFAULT_LENGTH,
        max_attempts: int = MAX_GENERATION_ATTEMPTS,
    ) -> str:
        return cls.generate_unique(
            "transfer",
            exists=exists,
            length=length,
            max_attempts=max_attempts,
        )

    '''UTILS'''
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
    def _random_token(length: int) -> str:
        if length < 6:
            raise ValueError("ID length must be at least 6")
        return "".join(secrets.choice(ALPHABET) for _ in range(length))