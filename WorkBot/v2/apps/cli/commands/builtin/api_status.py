# backend/app/cli/commands/builtin/api_status.py

from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api.client import (
    WorkBotApiError,
    WorkBotConnectionError,
)


class ApiStatusCommand(Command):
    """
    Check connectivity with the WorkBot API.
    """

    name = "api-status"
    description = "Check the WorkBot API connection."

    def arguments(self):
        return argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
        )

    def autocomplete(
        self,
        flag: str,
        text: str,
    ):
        return []

    def command(self, args):
        if args:
            return CommandResult.error(
                "api-status does not accept arguments."
            )

        try:
            result = self.context.api.health()

        except WorkBotConnectionError as exc:
            return CommandResult.error(str(exc))

        except WorkBotApiError as exc:
            return CommandResult.error(str(exc))

        return CommandResult.object(
            result,
            title="API Status",
            summary=(
                f"Connected to "
                f"{self.context.config.api_base_url}"
            ),
        )