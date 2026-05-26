from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ResolveOrderLinesResult:
    order_id: str

    processed: int = 0
    errored: int = 0
    ignored: int = 0
    skipped: int = 0

    errors: tuple[str, ...] = field(default_factory=tuple)

    @property
    def has_errors(self) -> bool:
        return bool(self.errors) or self.errored > 0


class ResolveOrderLinesResultBuilder:
    def __init__(self, *, order_id: str) -> None:
        self.order_id = order_id
        self.processed = 0
        self.errored = 0
        self.ignored = 0
        self.skipped = 0
        self.errors: list[str] = []

    def add_processed(self) -> None:
        self.processed += 1

    def add_errored(self, message: str) -> None:
        self.errored += 1
        self.errors.append(message)

    def add_ignored(self) -> None:
        self.ignored += 1

    def add_skipped(self) -> None:
        self.skipped += 1

    def build(self) -> ResolveOrderLinesResult:
        return ResolveOrderLinesResult(
            order_id=self.order_id,
            processed=self.processed,
            errored=self.errored,
            ignored=self.ignored,
            skipped=self.skipped,
            errors=tuple(self.errors),
        )