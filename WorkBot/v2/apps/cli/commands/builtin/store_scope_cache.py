from __future__ import annotations

from ..command_context import CommandContext
from ...cache import SCOPE_CACHE

def get_cached_store_scopes(
    context: CommandContext,
):
    cache = context.session.cache[SCOPE_CACHE]

    if not cache.loaded:
        scopes = context.api.list_store_scopes()

        cache.replace(
            (scope.id, scope)
            for scope in scopes
        )

    return cache.all()


def refresh_store_scopes(
    context: CommandContext,
):
    scopes = context.api.list_store_scopes()

    context.session.cache[SCOPE_CACHE].replace(
        (scope.id, scope)
        for scope in scopes
    )

    return scopes