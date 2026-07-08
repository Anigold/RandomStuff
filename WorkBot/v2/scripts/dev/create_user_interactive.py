# scripts/dev/create_user_interactive.py

from __future__ import annotations

from dataclasses import replace
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
from workbot_core.utils.ids import IdGenerator


def main() -> None:
    print()
    print("WorkBot User Creator")
    print("====================")
    print()

    with create_session() as session:
        user_repository = SqlUserRepository(session)
        store_repository = SqlStoreRepository(session)
        access_repository = SqlUserStoreAccessRepository(session)

        stores = [
            store
            for store in store_repository.list_all()
            if getattr(store, "is_active", True)
        ]

        username = _prompt_required("Username")
        existing_user = user_repository.get_by_username(username)

        if existing_user:
            print()
            print(f"Existing user found: {existing_user.username} ({existing_user.id})")

            if not _prompt_yes_no("Update this user?", default=False):
                print("Cancelled.")
                return

            is_new_user = False
            user = existing_user
        else:
            is_new_user = True
            user = None

        role = _prompt_role(
            default=user.role if user else None,
        )

        password_hash: str | None = None

        if is_new_user:
            password_hash = _prompt_password_hash()
        else:
            if _prompt_yes_no("Change password?", default=False):
                password_hash = _prompt_password_hash()

        if user is None:
            user = User(
                id=IdGenerator.user_id(
                    exists=lambda candidate: (
                        user_repository.get_by_id(candidate) is not None
                    ),
                ),
                username=username,
                password_hash=password_hash or "",
                role=role,
                is_active=True,
            )
        else:
            user = replace(
                user,
                role=role,
                is_active=True,
                password_hash=password_hash
                if password_hash is not None
                else user.password_hash,
            )

        selected_store_ids = _prompt_store_access(
            stores=stores,
            role=role,
            existing_store_ids=set(
                access_repository.list_store_ids_for_user(user.id)
            )
            if not is_new_user
            else set(),
        )

        print()
        print("Review")
        print("------")
        print(f"Username: {user.username}")
        print(f"User ID:  {user.id}")
        print(f"Role:     {user.role.value}")
        print(f"Active:   {user.is_active}")
        print("Store access:")

        if selected_store_ids is None:
            print("  Keep existing store access")
        elif not selected_store_ids:
            print("  No explicit store access")
        else:
            stores_by_id = {
                store.id: store
                for store in stores
            }

            for store_id in sorted(selected_store_ids):
                store = stores_by_id.get(store_id)

                if store:
                    print(f"  - {store.name} ({store.id})")
                else:
                    print(f"  - {store_id}")

        print()

        if not _prompt_yes_no("Save this user?", default=True):
            print("Cancelled.")
            return

        user_repository.save(user)

        if selected_store_ids is not None:
            access_repository.delete_for_user(user.id)

            for store_id in sorted(selected_store_ids):
                access_repository.save(
                    UserStoreAccess(
                        id=IdGenerator.user_store_access_id(),
                        user_id=user.id,
                        store_id=store_id,
                    )
                )

        session.commit()

        print()

        if is_new_user:
            print(f"Created user: {user.username} ({user.id})")
        else:
            print(f"Updated user: {user.username} ({user.id})")

        print("Done.")


def _prompt_required(label: str) -> str:
    while True:
        value = input(f"{label}: ").strip()

        if value:
            return value

        print(f"{label} is required.")


def _prompt_yes_no(
    label: str,
    *,
    default: bool,
) -> bool:
    suffix = "Y/n" if default else "y/N"

    while True:
        value = input(f"{label} [{suffix}]: ").strip().casefold()

        if not value:
            return default

        if value in {"y", "yes"}:
            return True

        if value in {"n", "no"}:
            return False

        print("Please enter y or n.")


def _prompt_role(
    *,
    default: UserRole | str | None = None,
) -> UserRole:
    roles = list(UserRole)
    default_value = _role_value(default) if default is not None else None

    print()
    print("Available roles:")

    for index, role in enumerate(roles, start=1):
        marker = " default" if role.value == default_value else ""
        print(f"  {index}. {role.value}{marker}")

    while True:
        prompt = "Select role"

        if default_value:
            prompt += f" [{default_value}]"

        value = input(f"{prompt}: ").strip()

        if not value and default_value:
            return UserRole(default_value)

        if value.isdigit():
            index = int(value)

            if 1 <= index <= len(roles):
                return roles[index - 1]

        for role in roles:
            if value.casefold() == role.value.casefold():
                return role

        print("Please select a role by number or name.")


def _prompt_password_hash() -> str:
    while True:
        password = getpass("Password: ")
        confirm_password = getpass("Confirm password: ")

        if not password:
            print("Password is required.")
            continue

        if password != confirm_password:
            print("Passwords do not match.")
            continue

        return hash_password(password)


def _prompt_store_access(
    *,
    stores,
    role: UserRole,
    existing_store_ids: set[str],
) -> set[str] | None:
    print()
    print("Store Access")
    print("------------")

    if role == UserRole.SUPERVISOR:
        print(
            "Supervisor users can use the virtual supervisor scope "
            "if the backend scope manager allows it."
        )
        print(
            "Explicit store access is still useful if you want this user "
            "to select individual store scopes."
        )
        print()

    if role == UserRole.MANAGER:
        print(
            "Manager users usually need explicit store access rows "
            "for the stores they manage."
        )
        print()

    if role == UserRole.VIEWER:
        print(
            "Viewer users usually need explicit store access rows "
            "for the stores they can view."
        )
        print()

    if existing_store_ids:
        print("Existing explicit store access:")

        stores_by_id = {
            store.id: store
            for store in stores
        }

        for store_id in sorted(existing_store_ids):
            store = stores_by_id.get(store_id)

            if store:
                print(f"  - {store.name} ({store.id})")
            else:
                print(f"  - {store_id}")

        print()

        if _prompt_yes_no("Keep existing store access?", default=True):
            return None

    if not stores:
        print("No active stores found.")
        return set()

    print("Choose store access mode:")
    print("  1. No explicit store access")
    print("  2. All active stores")
    print("  3. Select stores manually")

    default_selection = "2" if role == UserRole.SUPERVISOR else "3"

    while True:
        value = input(f"Selection [{default_selection}]: ").strip()
        value = value or default_selection

        if value == "1":
            return set()

        if value == "2":
            return {
                store.id
                for store in stores
            }

        if value == "3":
            return _prompt_manual_store_selection(stores)

        print("Please choose 1, 2, or 3.")


def _prompt_manual_store_selection(stores) -> set[str]:
    print()
    print("Available stores:")

    for index, store in enumerate(stores, start=1):
        print(f"  {index}. {store.name} ({store.id})")

    print()
    print("Enter store numbers separated by commas.")
    print("Example: 1,3,4")
    print("Leave blank for no explicit store access.")
    print()

    while True:
        value = input("Stores: ").strip()

        if not value:
            return set()

        selected_ids: set[str] = set()
        invalid_values: list[str] = []

        for raw_part in value.split(","):
            part = raw_part.strip()

            if not part:
                continue

            if not part.isdigit():
                invalid_values.append(part)
                continue

            index = int(part)

            if index < 1 or index > len(stores):
                invalid_values.append(part)
                continue

            selected_ids.add(stores[index - 1].id)

        if invalid_values:
            print(
                "Invalid selections: "
                + ", ".join(invalid_values)
            )
            continue

        return selected_ids


def _role_value(role: UserRole | str | None) -> str:
    if role is None:
        return ""

    return str(getattr(role, "value", role))


if __name__ == "__main__":
    main()