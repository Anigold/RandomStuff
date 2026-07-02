from __future__ import annotations

from collections.abc import Generator

from sqlalchemy.orm import Session

from workbot_core.infrastructure.database.session import create_session
from workbot_core.config.settings import Settings, settings

def get_db_session() -> Generator[Session, None, None]:
    with create_session() as session:
        yield session


def get_settings() -> Settings:
    return settings