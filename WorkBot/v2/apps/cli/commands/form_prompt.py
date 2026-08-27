from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from .command_result import CommandResult


FormParser = Callable[[str], Any]
FormValidator = Callable[[Any], str | None]


@dataclass(slots=True)
class FormField:
    """
    Describes one field in an interactive CLI form.
    """

    name: str
    prompt: str

    default: Any = None
    required: bool = False

    parser: FormParser | None = None
    validator: FormValidator | None = None

    allow_clear: bool = False
    clear_token: str = "<clear>"

    help_text: str = ""


@dataclass(slots=True)
class FormPromptRequest:
    """
    Request for the CLI to collect a sequence of form fields.

    The CLI is responsible for prompting one field at a time,
    parsing the entered values, and calling the handler when
    the form is complete.
    """

    fields: list[FormField]

    handler: Callable[
        [dict[str, Any]],
        CommandResult,
    ]

    title: str = "Form"

    cancel_message: str = "Form cancelled."

    metadata: dict[str, Any] = field(
        default_factory=dict
    )