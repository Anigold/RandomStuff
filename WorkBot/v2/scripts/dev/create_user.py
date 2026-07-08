# scripts/dev/create_user.py

from __future__ import annotations

import argparse
from getpass import getpass

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


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create or update a WorkBot user and assign store access.",
    )

    parser.add_argument("--username", required=True)
    parser.add_argument("--email", default=None)
    parser.add_argument("--display-name", default=None)

    parser.add_argument(
        "--role",
        required=True,
        choices=[role.value for role in UserRole],
        help="User role.",
    )

    parser.add_argument(
        "--password",
        default=None,
        help="Plaintext password. If omitted, you will be prompted.",
    )

    parser.add_argument(
        "--store-id",
        action="append",
        default=[],
        help=(
            "Store ID to assign. Can be used multiple times. "
            "Example: --store-id sto_abc --store-id sto_xyz"
        ),
    )

    parser.add_argument(
        "--all-stores",
        action="store_true",
        help="Assign explicit access to all active stores.",
    )

    parser.add_argument(
        "--clear-existing-store-access",
        action="store_true",
        help="Remove existing store access rows before assigning new ones.",
    )

    args = parser.parse_args()

    password = args.password
    if not password:
        password = getpass("Password: ")

    if not password:
        raise SystemExit("Password is required.")

    with create_session() as session:
        user_repository = SqlUserRepository(session)
        store_repository = SqlStoreRepository(session)
        access_repository = SqlUserStoreAccessRepository(session)

        role = UserRole(args.role)

        existing_user = user_repository.get_by_username(args.username)

        if existing_user is None:
            user = User(
                id=User.new_id(),
                username=args.username,
                password_hash=hash_password(password),
                role=role,
                email=args.email,
                display_name=args.display_name,
                is_active=True,
            )

            user_repository.save(user)
            print(f"Created user: {user.username} ({user.id})")

        else:
            user = existing_user

            user.password_hash = hash_password(password)
            user.role = role

            if args.email is not None:
                user.email = args.email

            if args.display_name is not None:
                user.display_name = args.display_name

            user.is_active = True

            user_repository.save(user)
            print(f"Updated user: {user.username} ({user.id})")

        if args.clear_existing_store_access:
            access_repository.delete_for_user(user.id)
            print("Cleared existing store access.")

        store_ids = set(args.store_id)

        if args.all_stores:
            store_ids.update(
                store.id
                for store in store_repository.list_all()
                if getattr(store, "is_active", True)
            )

        if store_ids:
            valid_store_ids = {
                store.id
                for store in store_repository.list_all()
            }

            unknown_store_ids = store_ids - valid_store_ids

            if unknown_store_ids:
                raise SystemExit(
                    "Unknown store IDs: "
                    + ", ".join(sorted(unknown_store_ids))
                )

            existing_store_ids = set(
                access_repository.list_store_ids_for_user(user.id)
            )

            for store_id in sorted(store_ids):
                if store_id in existing_store_ids:
                    continue

                access_repository.save(
                    UserStoreAccess(
                        id=UserStoreAccess.new_id(),
                        user_id=user.id,
                        store_id=store_id,
                    )
                )

                print(f"Assigned store access: {store_id}")

        session.commit()

    print("Done.")


if __name__ == "__main__":
    main()