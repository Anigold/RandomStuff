# backend/app/cli/commands/command_context.py

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ..api.client import WorkBotApiClient
from ..config import CliConfig
from ..session import CliSession

if TYPE_CHECKING:
    from ..cli import CLI


@dataclass(slots=True)
class CommandContext:
    cli: "CLI"
    api: WorkBotApiClient
    session: CliSession
    config: CliConfig