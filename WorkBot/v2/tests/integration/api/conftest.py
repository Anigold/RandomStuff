from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.auth.dependencies import get_current_user
from apps.api.dependencies import get_db_session
from apps.api.main import app
from tests.helpers.auth_helpers import make_supervisor_user
from workbot_core.domain.models.user import User
from workbot_core.infrastructure.database.base import Base
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserStoreAccessRepository,
)


@dataclass(frozen=True)
class ApiTestContext:
    client: TestClient
    session_factory: sessionmaker[Session]


@pytest.fixture
def api_context(tmp_path: Path) -> Generator[ApiTestContext, None, None]:
    database_path = tmp_path / "test_api.db"
    database_url = f"sqlite:///{database_path}"

    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
    )

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    def override_get_db_session() -> Generator[Session, None, None]:
        session = session_factory()

        try:
            yield session
        finally:
            session.close()

    supervisor = make_supervisor_user()

    app.dependency_overrides[get_db_session] = override_get_db_session
    app.dependency_overrides[get_current_user] = lambda: supervisor

    with TestClient(app) as test_client:
        yield ApiTestContext(
            client=test_client,
            session_factory=session_factory,
        )

    app.dependency_overrides.clear()
    engine.dispose()


@pytest.fixture
def client(api_context: ApiTestContext) -> TestClient:
    return api_context.client


def authenticate_as(user: User) -> None:
    app.dependency_overrides[get_current_user] = lambda: user


def grant_store_access(
    api_context: ApiTestContext,
    *,
    access,
) -> None:
    with api_context.session_factory() as session:
        SqlUserStoreAccessRepository(session).save(access)
        session.commit()