from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .command_result import CommandResult


@dataclass(slots=True)
class ConfirmationPromptRequest:
    """
    Request for the CLI to ask the user for confirmation
    before completing an action.
    """

    prompt: str

    handler: Callable[
        [bool],
        CommandResult,
    ]

    default: bool = False

    cancel_message: str = "Operation cancelled."