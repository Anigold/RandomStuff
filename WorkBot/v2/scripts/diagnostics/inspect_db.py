from __future__ import annotations

from sqlalchemy import inspect

from workbot_core.infrastructure.database.session import engine

def main() -> None:
    inspector = inspect(engine)

    table_names = inspector.get_table_names()

    if not table_names:
        print("No database tables found.")
        return

    print("Database tables:")

    for table_name in table_names:
        print(f"  - {table_name}")

        columns = inspector.get_columns(table_name)
        for column in columns:
            column_name = column["name"]
            column_type = column["type"]
            nullable = column["nullable"]
            print(f"      {column_name}: {column_type}, nullable={nullable}")


if __name__ == "__main__":
    main()