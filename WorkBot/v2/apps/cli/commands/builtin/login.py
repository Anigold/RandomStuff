from __future__ import annotations

import argparse

from ..command import Command
from ..command_result import CommandResult
from ..secret_prompt import SecretPromptRequest
from ...api import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
)


class LoginCommand(Command):
    """
    Authenticate with the WorkBot API.
    """

    name = "login"
    description = "Log in to WorkBot."

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
        )

        parser.add_argument(
            "--username",
            "-u",
            required=True,
            help="WorkBot username.",
        )

        return parser

    def autocomplete(
        self,
        flag: str,
        text: str,
    ):
        return []

    def command(self, args):
        parsed = self.arguments().parse_args(args)

        username = parsed.username.strip()

        if not username:
            return CommandResult.error(
                "Username cannot be empty."
            )

        if self.context.session.is_authenticated:
            return CommandResult.error(
                "You are already logged in. "
                "Log out before authenticating as another user."
            )

        return SecretPromptRequest(
            prompt="Password: ",
            handler=lambda password: self._login(
                username=username,
                password=password,
            ),
            cancel_message="Login cancelled.",
        )

    def _login(
        self,
        *,
        username: str,
        password: str,
    ) -> CommandResult:
        if not password:
            return CommandResult.error(
                "Password cannot be empty."
            )

        try:
            result = self.context.api.login(
                username=username,
                password=password,
            )

        except WorkBotUnauthorizedError:
            self.context.session.logout()

            return CommandResult.error(
                "Invalid username or password."
            )

        except WorkBotConnectionError as exc:
            self.context.session.logout()

            return CommandResult.error(str(exc))

        except WorkBotApiError as exc:
            self.context.session.logout()

            return CommandResult.error(str(exc))

        return CommandResult.object(
            result.user,
            target="both",
            title="Authenticated User",
            summary=(
                f'Logged in successfully as "{username}".'
            ),
        )