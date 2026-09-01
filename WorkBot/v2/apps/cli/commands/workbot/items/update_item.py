from __future__ import annotations

import argparse
from typing import Any

from apps.cli.commands.command import Command
from apps.cli.commands.command_result import CommandResult
from apps.cli.commands.form_parsers import (
    parse_bool,
    parse_decimal,
)
from apps.cli.commands.form_prompt import (
    FormField,
    FormPromptRequest,
)
from apps.cli.api.client import (
    WorkBotApiError,
    WorkBotConnectionError,
    WorkBotUnauthorizedError,
    ItemWritePayload,
)

class UpdateItemCommand(Command):
    """
    Update an existing WorkBot item.
    """

    name = "update-item"
    description = "Update an existing item."

    def arguments(self):
        parser = argparse.ArgumentParser(
            prog=self.name,
            add_help=False,
        )

        parser.add_argument(
            "--item",
            "-i",
            required=True,
            help="Item name.",
        )

        return parser

    def autocomplete(
        self,
        flag: str,
        text: str,
    ):
        if flag not in ("--item", "-i"):
            return []

        if not self.context.session.is_authenticated:
            return []

        if self.context.session.active_scope_id is None:
            return []

        try:
            items = self.context.api.list_items(
                search=text or None,
                include_inactive=True,
            )

        except (
            WorkBotUnauthorizedError,
            WorkBotConnectionError,
            WorkBotApiError,
        ):
            return []

        return [
            (
                item.name,
                item.category or item.id,
            )
            for item in items
        ]

    def command(self, args):
        parsed = self.arguments().parse_args(args)

        if not self.context.session.is_authenticated:
            return CommandResult.error(
                "You are not logged in."
            )

        if self.context.session.active_scope_id is None:
            return CommandResult.error(
                "No store scope is selected. "
                'Use "use-scope" first.'
            )

        try:
            scopes = self.context.api.list_store_scopes()

            active_scope = next(
                (
                    scope
                    for scope in scopes
                    if scope.id
                    == self.context.session.active_scope_id
                ),
                None,
            )

            if active_scope is None:
                self.context.session.set_active_scope(None)

                return CommandResult.error(
                    "The selected scope is no longer available."
                )

            if not active_scope.is_supervisor:
                return CommandResult.error(
                    "Updating core item information "
                    "requires Supervisor scope."
                )

            selected_item = self.context.api.find_item_by_name(
                parsed.item.strip(),
                include_inactive=True,
            )

            if selected_item is None:
                return CommandResult.error(
                    f'Item "{parsed.item}" was not found.'
                )

            detail = self.context.api.get_item(
                selected_item.id
            )

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

        return FormPromptRequest(
            title=f'Update Item: {selected_item.name}',
            cancel_message="Item update cancelled.",
            fields=self._fields(detail),
            handler=lambda values: self._update_item(
                item_id=selected_item.id,
                values=values,
            ),
        )

    def _fields(
        self,
        detail: dict[str, Any],
    ) -> list[FormField]:
        return [
            FormField(
                name="name",
                prompt="Name",
                default=detail["name"],
                required=True,
            ),
            FormField(
                name="category",
                prompt="Category",
                default=detail.get("category"),
                allow_clear=True,
            ),
            FormField(
                name="subcategory",
                prompt="Subcategory",
                default=detail.get("subcategory"),
                allow_clear=True,
            ),
            FormField(
                name="count_unit_quantity",
                prompt="Count unit quantity",
                default=detail.get("count_unit_quantity"),
                parser=parse_decimal,
                allow_clear=True,
            ),
            FormField(
                name="count_unit_measure",
                prompt="Count unit measure",
                default=detail.get("count_unit_measure"),
                allow_clear=True,
            ),
            FormField(
                name="custom_each_name",
                prompt="Custom each name",
                default=detail.get("custom_each_name"),
                allow_clear=True,
            ),
            FormField(
                name="each_quantity",
                prompt="Each quantity",
                default=detail.get("each_quantity"),
                parser=parse_decimal,
                allow_clear=True,
            ),
            FormField(
                name="each_measure",
                prompt="Each measure",
                default=detail.get("each_measure"),
                allow_clear=True,
            ),
            FormField(
                name="weight_quantity",
                prompt="Weight quantity",
                default=detail.get("weight_quantity"),
                parser=parse_decimal,
                allow_clear=True,
            ),
            FormField(
                name="weight_measure",
                prompt="Weight measure",
                default=detail.get("weight_measure"),
                allow_clear=True,
            ),
            FormField(
                name="volume_quantity",
                prompt="Volume quantity",
                default=detail.get("volume_quantity"),
                parser=parse_decimal,
                allow_clear=True,
            ),
            FormField(
                name="volume_measure",
                prompt="Volume measure",
                default=detail.get("volume_measure"),
                allow_clear=True,
            ),
            FormField(
                name="is_active",
                prompt="Active",
                default=detail.get(
                    "is_active",
                    True,
                ),
                parser=parse_bool,
            ),
        ]

    def _update_item(
        self,
        *,
        item_id: str,
        values: dict[str, Any],
    ) -> CommandResult:
        try:
            payload = ItemWritePayload.from_dict(
                values
            )

            item = self.context.api.update_item(
                item_id,
                payload,
            )

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
            item,
            title="Updated Item",
            summary=(
                f'Updated item "{item.get("name", item_id)}" successfully.'
            ),
        )