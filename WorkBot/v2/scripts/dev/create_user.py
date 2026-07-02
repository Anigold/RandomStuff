from __future__ import annotations

import getpass
from datetime import UTC, datetime

from apps.api.auth.passwords import hash_password
from workbot_core.domain.models.user import User, UserRole, UserStoreAccess
from workbot_core.infrastructure.database.repositories.store_repository import (
    SqlStoreRepository,
)
from workbot_core.infrastructure.database.repositories.user_repository import (
    SqlUserRepository,
    SqlUserStoreAccessRepository,
)
from workbot_core.infrastructure.database.session import create_session
from workbot_core.utils.ids import IdGenerator


def main() -> None:
    print("Create WorkBot user")
    print("-------------------")

    username = input("Username: ").strip()

    if not username:
        raise SystemExit("Username is required.")

    role_value = input("Role [supervisor/manager/viewer]: ").strip().lower()

    try:
        role = UserRole(role_value)
    except ValueError as exc:
        raise SystemExit(
            "Role must be one of: supervisor, manager, viewer."
        ) from exc

    password = getpass.getpass("Password: ")
    password_confirm = getpass.getpass("Confirm password: ")

    if not password:
        raise SystemExit("Password is required.")

    if password != password_confirm:
        raise SystemExit("Passwords do not match.")

    now = datetime.now(UTC)

    user = User(
        id=IdGenerator.user_id(),
        username=username,
        password_hash=hash_password(password),
        role=role,
        is_active=True,
        created_at=now,
        updated_at=now,
    )

    with create_session() as session:
        users = SqlUserRepository(session)
        stores = SqlStoreRepository(session)
        user_store_accesses = SqlUserStoreAccessRepository(session)

        existing_user = users.get_by_username(username)

        if existing_user is not None:
            raise SystemExit(f"User already exists: {username}")

        users.save(user)

        if role != UserRole.SUPERVISOR:
            print()
            print("Available stores:")
            for store in stores.list_active():
                print(f"- {store.name}")

            store_names_raw = input(
                "Store names this user can access, comma-separated: "
            ).strip()

            if not store_names_raw:
                raise SystemExit(
                    "At least one store is required for manager/viewer users."
                )

            store_names = [
                value.strip()
                for value in store_names_raw.split(",")
                if value.strip()
            ]

            for store_name in store_names:
                store = stores.get_by_name(store_name)

                if store is None:
                    raise SystemExit(f"Store not found: {store_name}")

                user_store_accesses.save(
                    UserStoreAccess(
                        id=IdGenerator.user_store_access_id(),
                        user_id=user.id,
                        store_id=store.id,
                        created_at=now,
                        updated_at=now,
                    )
                )

        all_stores = stores.list_active()
        for store in all_stores:
            user_store_accesses.save(
                UserStoreAccess(
                    id=IdGenerator.user_store_access_id(),
                    user_id=user.id,
                    store_id=store.id,
                    created_at=now,
                    updated_at=now,
                    )
                )
        session.commit()

    print(f"Created {role.value} user: {username}")


if __name__ == "__main__":
    main()