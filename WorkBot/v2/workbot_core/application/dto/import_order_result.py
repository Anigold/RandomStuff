from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ImportOrderResult:
    order_id: str | None = None
    created: bool = False
    errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors)