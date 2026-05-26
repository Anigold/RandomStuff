from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ImportResult:
    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def total_processed(self) -> int:
        return self.created + self.updated + self.skipped

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)


class ImportResultBuilder:
    def __init__(self) -> None:
        self.created = 0
        self.updated = 0
        self.skipped = 0
        self.errors: list[str] = []

    def add_created(self) -> None:
        self.created += 1

    def add_updated(self) -> None:
        self.updated += 1

    def add_skipped(self) -> None:
        self.skipped += 1

    def add_error(self, message: str) -> None:
        self.errors.append(message)

    def build(self) -> ImportResult:
        return ImportResult(
            created=self.created,
            updated=self.updated,
            skipped=self.skipped,
            errors=tuple(self.errors),
        )