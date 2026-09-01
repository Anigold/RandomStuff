from __future__ import annotations

import argparse
from typing import Any

from apps.cli.commands.command import Command
from apps.cli.commands.command_result import CommandResult
from apps.cli.api.client import (
    WorkBotApiError, 
    WorkBotConnectionError, 
    WorkBotUnauthorizedError,
    ItemStoreInfoWritePayload,
)
from apps.cli.commands.form_parsers import (
    parse_bool, 
    parse_decimal,
)
from apps.cli.commands.form_prompt import (
    FormField,
    FormPromptRequest
)



class AddItemStoreInfoCommand(Command):
    """
    Add store-specific information to an item.
    """

    name = "add-item-store-info"
    description = "Add store information to an item."

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

        parser.add_argument(
            "--store",
            "-s",
            help=(
                "Store name. Required only when using "
                "Supervisor scope."
            ),
        )

        return parser

    def autocomplete(
        self,
        flag: str,
        text: str,
    ):
        if not self.context.session.is_authenticated:
            return []

        if self.context.session.active_scope_id is None:
            return []

        if flag in ("--item", "-i"):
            try:
                items = self.context.api.list_items(
                    search=text or None,
                    include_inactive=False,
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

        if flag in ("--store", "-s"):
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

                if (
                    active_scope is None
                    or not active_scope.is_supervisor
                ):
                    return []

                stores = self.context.api.list_stores(
                    search=text or None,
                    include_inactive=False,
                )

            except (
                WorkBotUnauthorizedError,
                WorkBotConnectionError,
                WorkBotApiError,
            ):
                return []

            return [
                (
                    store.name,
                    store.id,
                )
                for store in stores
            ]

        return []

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

            selected_item = self.context.api.find_item_by_name(
                parsed.item.strip(),
                include_inactive=False,
            )

            if selected_item is None:
                return CommandResult.error(
                    f'Item "{parsed.item}" was not found.'
                )

            store_id = self._resolve_store_id(
                active_scope=active_scope,
                requested_store_name=parsed.store,
            )

            if isinstance(store_id, CommandResult):
                return store_id

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
            title=f'Add Store Info: {selected_item.name}',
            cancel_message="Item store-info creation cancelled.",
            fields=[
                FormField(
                    name="count_unit",
                    prompt="Count unit",
                ),
                FormField(
                    name="par",
                    prompt="Par",
                    parser=parse_decimal,
                ),
                FormField(
                    name="is_active",
                    prompt="Active",
                    default=True,
                    parser=parse_bool,
                ),
            ],
            handler=lambda values: self._add_store_info(
                item_id=selected_item.id,
                store_id=store_id,
                values=values,
            ),
        )

    def _resolve_store_id(
        self,
        *,
        active_scope,
        requested_store_name: str | None,
    ) -> str | CommandResult:
        if active_scope.is_store:
            return active_scope.id

        if not requested_store_name:
            return CommandResult.error(
                "Supervisor scope requires --store <store name>."
            )

        store = self.context.api.find_store_by_name(
            requested_store_name.strip(),
            include_inactive=False,
        )

        if store is None:
            return CommandResult.error(
                f'Store "{requested_store_name}" was not found.'
            )

        return store.id

    def _add_store_info(
        self,
        *,
        item_id: str,
        store_id: str,
        values: dict[str, Any],
    ) -> CommandResult:
        payload = ItemStoreInfoWritePayload(
            store_id=store_id,
            count_unit=values.get("count_unit"),
            par=values.get("par"),
            is_active=values.get(
                "is_active",
                True,
            ),
        )

        try:
            result = self.context.api.add_item_store_info(
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
            result,
            title="Created Item Store Info",
            summary="Item store information added successfully.",
        )