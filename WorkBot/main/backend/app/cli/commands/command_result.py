from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal


DisplayTarget = Literal[
    "console",
    "side",
    "both",
    "none",
]

PayloadKind = Literal[
    "empty",
    "text",
    "list",
    "table",
    "object",
    "error",
]


@dataclass(slots=True)
class CommandResult:
    """
    Neutral result object returned by CLI commands.

    The CLI renderer decides how this is displayed.
    """

    # What type of payload this is
    kind: PayloadKind = "empty"

    # Actual returned data
    payload: Any = None

    # Where it should be displayed
    target: DisplayTarget = "console"

    # Title used for side panel rendering
    title: str = "Details"

    # Short message typically shown in console
    summary: str = ""

    # Replace or append side panel
    replace_side_panel: bool = True

    # Extra optional metadata for renderers
    metadata: dict[str, Any] = field(default_factory=dict)

    # ----------------------------------------------------
    # Convenience constructors
    # ----------------------------------------------------

    @classmethod
    def text(
        cls,
        text: str,
        *,
        target: DisplayTarget = "console",
        title: str = "Details",
        summary: str = "",
    ) -> "CommandResult":
        return cls(
            kind="text",
            payload=text,
            target=target,
            title=title,
            summary=summary,
        )

    @classmethod
    def error(
        cls,
        message: str,
    ) -> "CommandResult":
        return cls(
            kind="error",
            payload=message,
            target="console",
        )

    @classmethod
    def list(
        cls,
        items: list[Any],
        *,
        target: DisplayTarget = "side",
        title: str = "Results",
        summary: str = "",
    ) -> "CommandResult":
        return cls(
            kind="list",
            payload=items,
            target=target,
            title=title,
            summary=summary,
        )

    @classmethod
    def table(
        cls,
        *,
        columns: list[str],
        rows: list[list[Any]],
        target: DisplayTarget = "side",
        title: str = "Table",
        summary: str = "",
    ) -> "CommandResult":
        return cls(
            kind="table",
            payload={
                "columns": columns,
                "rows": rows,
            },
            target=target,
            title=title,
            summary=summary,
        )

    @classmethod
    def object(
        cls,
        obj: Any,
        *,
        target: DisplayTarget = "side",
        title: str = "Details",
        summary: str = "",
    ) -> "CommandResult":
        return cls(
            kind="object",
            payload=obj,
            target=target,
            title=title,
            summary=summary,
        )