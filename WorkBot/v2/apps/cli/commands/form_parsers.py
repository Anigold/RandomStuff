from __future__ import annotations

from decimal import Decimal, InvalidOperation


def parse_decimal(value: str) -> Decimal:
    """
    Parse a CLI value into a Decimal.

    Raises ValueError with a user-friendly message when invalid.
    """

    try:
        return Decimal(value)

    except InvalidOperation as exc:
        raise ValueError(
            f'Expected a number, received "{value}".'
        ) from exc


def parse_bool(value: str) -> bool:
    """
    Parse common CLI boolean representations.
    """

    normalized = value.strip().casefold()

    if normalized in {
        "true",
        "t",
        "yes",
        "y",
        "1",
        "on",
    }:
        return True

    if normalized in {
        "false",
        "f",
        "no",
        "n",
        "0",
        "off",
    }:
        return False

    raise ValueError(
        f'Expected yes/no or true/false, received "{value}".'
    )