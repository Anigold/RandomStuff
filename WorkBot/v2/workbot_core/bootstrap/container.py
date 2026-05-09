from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Container:
    """Application dependency container.

    Add repositories, services, and use cases here as the project is implemented.
    """


def build_container() -> Container:
    return Container()
