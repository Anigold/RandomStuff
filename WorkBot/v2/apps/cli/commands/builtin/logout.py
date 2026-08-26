from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
)


class LogoutCommand(Command):
    """
    Log out of the current WorkBot session.
    """

    name = "logout"
    description = "Log out of WorkBot."

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
                "logout does not accept arguments."
            )

        if not self.context.session.is_authenticated:
            return CommandResult.text(
                "You are not currently logged in."
            )

        try:
            self.context.api.logout()

        except WorkBotConnectionError as exc:
            # Even if the server cannot be reached, the user explicitly
            # requested a local logout.
            self.context.session.logout()

            return CommandResult.error(
                f"{exc}\nLocal session has been cleared."
            )

        except WorkBotApiError as exc:
            self.context.session.logout()

            return CommandResult.error(
                f"{exc}\nLocal session has been cleared."
            )

        self.context.session.logout()

        return CommandResult.text(
            "Logged out successfully."
        )