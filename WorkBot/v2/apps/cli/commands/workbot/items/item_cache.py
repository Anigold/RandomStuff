# apps/cli/commands/workbot/items/item_cache.py

from __future__ import annotations

from apps.cli.cache import ITEM_CACHE
from apps.cli.commands.command_context import CommandContext


def get_cached_items(
    context: CommandContext,
):
    """
    Return cached items for the current scope.

    The API is queried only when the item cache has not yet been loaded
    for the current session/scope.
    """
    cache = context.session.cache[ITEM_CACHE]

    if not cache.loaded:
        return refresh_items(context)

    return cache.all()


def refresh_items(
    context: CommandContext,
):
    """
    Fetch the authoritative item collection from the API and replace
    the current item cache.
    """
    items = context.api.list_items()

    context.session.cache[ITEM_CACHE].replace(
        (item.id, item)
        for item in items
    )

    return items


def get_cached_item(
    context: CommandContext,
    item_id: str,
):
    """
    Return one item from the cache by ID.

    Loads the item collection first if necessary.
    """
    cache = context.session.cache[ITEM_CACHE]

    if not cache.loaded:
        refresh_items(context)

    return cache.get(item_id)


def cache_item(
    context: CommandContext,
    item,
) -> None:
    """
    Insert or update one known item in the cache.
    """
    context.session.cache[ITEM_CACHE].upsert(
        item.id,
        item,
    )


def remove_cached_item(
    context: CommandContext,
    item_id: str,
) -> None:
    """
    Remove one item from the local cache.

    Useful when an operation makes the cached representation stale.
    """
    context.session.cache[ITEM_CACHE].remove(
        item_id
    )

def find_cached_item_by_name(
    context: CommandContext,
    name: str,
    *,
    include_inactive: bool = False,
):
    normalized_name = name.strip().casefold()

    for item in get_cached_items(context):
        if item.name.casefold() != normalized_name:
            continue

        if not include_inactive and not item.is_active:
            continue

        return item

    return None