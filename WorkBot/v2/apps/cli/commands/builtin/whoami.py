from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)


class WhoAmICommand(Command):
    """
    Show the currently authenticated WorkBot user.
    """

    name = "whoami"
    description = "Show the currently authenticated user."

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
                "whoami does not accept arguments."
            )

        if not self.context.session.is_authenticated:
            return CommandResult.error(
                "You are not logged in."
            )

        try:
            user = self.context.api.me()

        except WorkBotUnauthorizedError:
            self.context.session.logout()

            return CommandResult.error(
                "Your authentication session is no longer valid. "
                "Please log in again."
            )

        except WorkBotConnectionError as exc:
            return CommandResult.error(str(exc))

        except WorkBotApiError as exc:
            return CommandResult.error(str(exc))

        return CommandResult.object(
            user,
            title="Current User",
            summary="Authenticated user loaded.",
        )