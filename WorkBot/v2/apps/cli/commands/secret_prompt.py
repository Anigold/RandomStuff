from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .command_result import CommandResult


@dataclass(slots=True)
class SecretPromptRequest:
    """
    Request for the CLI to temporarily collect secret input.

    Secret input is:
    - masked on screen
    - not written to command history
    - not echoed to the console
    """

    prompt: str
    handler: Callable[[str], CommandResult]
    cancel_message: str = "Input cancelled."