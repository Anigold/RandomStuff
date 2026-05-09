from __future__ import annotations

from functools import lru_cache

from packages.workbot_core.bootstrap.container import Container, build_container


@lru_cache(maxsize=1)
def get_container() -> Container:
    return build_container()
