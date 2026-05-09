from __future__ import annotations

from pathlib import Path
from textwrap import dedent


PROJECT_ROOT = Path("workbot_project")


DIRECTORIES = [
    "data/imports",
    "data/exports",
    "data/downloads",
    "data/backups",
    "data/archive",

    "scripts",

    "alembic/versions",

    "tests/unit/domain",
    "tests/unit/application",
    "tests/unit/infrastructure",
    "tests/integration/database",
    "tests/integration/excel",
    "tests/integration/api",
    "tests/integration/cli",
    "tests/fixtures/excel",
    "tests/fixtures/json",
    "tests/fixtures/database",

    "apps/cli/commands",
    "apps/cli/rendering",

    "apps/api/routes",
    "apps/api/schemas",

    "apps/web",

    "packages/workbot_core/config",
    "packages/workbot_core/bootstrap",

    "packages/workbot_core/domain/models",
    "packages/workbot_core/domain/value_objects",
    "packages/workbot_core/domain/rules",

    "packages/workbot_core/application/interfaces",
    "packages/workbot_core/application/services",
    "packages/workbot_core/application/use_cases",
    "packages/workbot_core/application/dto",

    "packages/workbot_core/infrastructure/database/records",
    "packages/workbot_core/infrastructure/database/repositories",
    "packages/workbot_core/infrastructure/database/mappers",
    "packages/workbot_core/infrastructure/craftable",
    "packages/workbot_core/infrastructure/excel/readers",
    "packages/workbot_core/infrastructure/excel/writers",
    "packages/workbot_core/infrastructure/files",
    "packages/workbot_core/infrastructure/email/templates",
    "packages/workbot_core/infrastructure/legacy",

    "packages/workbot_core/utils",
]


PYTHON_PACKAGES = [
    "apps",
    "apps/cli",
    "apps/cli/commands",
    "apps/cli/rendering",

    "apps/api",
    "apps/api/routes",
    "apps/api/schemas",

    "packages",
    "packages/workbot_core",

    "packages/workbot_core/config",
    "packages/workbot_core/bootstrap",

    "packages/workbot_core/domain",
    "packages/workbot_core/domain/models",
    "packages/workbot_core/domain/value_objects",
    "packages/workbot_core/domain/rules",

    "packages/workbot_core/application",
    "packages/workbot_core/application/interfaces",
    "packages/workbot_core/application/services",
    "packages/workbot_core/application/use_cases",
    "packages/workbot_core/application/dto",

    "packages/workbot_core/infrastructure",
    "packages/workbot_core/infrastructure/database",
    "packages/workbot_core/infrastructure/database/records",
    "packages/workbot_core/infrastructure/database/repositories",
    "packages/workbot_core/infrastructure/database/mappers",
    "packages/workbot_core/infrastructure/craftable",
    "packages/workbot_core/infrastructure/excel",
    "packages/workbot_core/infrastructure/excel/readers",
    "packages/workbot_core/infrastructure/excel/writers",
    "packages/workbot_core/infrastructure/files",
    "packages/workbot_core/infrastructure/email",
    "packages/workbot_core/infrastructure/legacy",

    "packages/workbot_core/utils",
]


EMPTY_FILES = [
    ".env.example",

    "data/.gitkeep",
    "data/imports/.gitkeep",
    "data/exports/.gitkeep",
    "data/downloads/.gitkeep",
    "data/backups/.gitkeep",
    "data/archive/.gitkeep",

    "scripts/migrate_json_to_db.py",
    "scripts/seed_dev_data.py",
    "scripts/reset_dev_db.py",
    "scripts/inspect_db.py",

    "alembic/script.py.mako",
    "alembic/versions/.gitkeep",

    "tests/unit/domain/.gitkeep",
    "tests/unit/application/.gitkeep",
    "tests/unit/infrastructure/.gitkeep",
    "tests/integration/database/.gitkeep",
    "tests/integration/excel/.gitkeep",
    "tests/integration/api/.gitkeep",
    "tests/integration/cli/.gitkeep",
    "tests/fixtures/excel/.gitkeep",
    "tests/fixtures/json/.gitkeep",
    "tests/fixtures/database/.gitkeep",

    "apps/cli/parser.py",
    "apps/cli/command_registry.py",
    "apps/cli/command_result.py",
    "apps/cli/commands/items.py",
    "apps/cli/commands/vendors.py",
    "apps/cli/commands/stores.py",
    "apps/cli/commands/orders.py",
    "apps/cli/commands/audits.py",
    "apps/cli/commands/transfers.py",
    "apps/cli/commands/purchase_logs.py",
    "apps/cli/commands/system.py",
    "apps/cli/rendering/console_renderer.py",
    "apps/cli/rendering/table_renderer.py",
    "apps/cli/rendering/side_panel_renderer.py",
    "apps/cli/rendering/formatters.py",

    "apps/api/error_handlers.py",
    "apps/api/routes/health.py",
    "apps/api/routes/items.py",
    "apps/api/routes/vendors.py",
    "apps/api/routes/stores.py",
    "apps/api/routes/orders.py",
    "apps/api/routes/audits.py",
    "apps/api/routes/transfers.py",
    "apps/api/routes/purchase_logs.py",
    "apps/api/routes/files.py",
    "apps/api/schemas/item_schema.py",
    "apps/api/schemas/vendor_schema.py",
    "apps/api/schemas/store_schema.py",
    "apps/api/schemas/order_schema.py",
    "apps/api/schemas/audit_schema.py",
    "apps/api/schemas/transfer_schema.py",
    "apps/api/schemas/purchase_log_schema.py",
    "apps/api/schemas/file_schema.py",
    "apps/api/schemas/result_schema.py",

    "packages/workbot_core/config/logging.py",

    "packages/workbot_core/bootstrap/repositories.py",
    "packages/workbot_core/bootstrap/services.py",
    "packages/workbot_core/bootstrap/use_cases.py",

    "packages/workbot_core/domain/models/store.py",
    "packages/workbot_core/domain/models/vendor.py",
    "packages/workbot_core/domain/models/item.py",
    "packages/workbot_core/domain/models/item_store_info.py",
    "packages/workbot_core/domain/models/item_vendor_info.py",
    "packages/workbot_core/domain/models/order.py",
    "packages/workbot_core/domain/models/order_line.py",
    "packages/workbot_core/domain/models/audit.py",
    "packages/workbot_core/domain/models/audit_line.py",
    "packages/workbot_core/domain/models/transfer.py",
    "packages/workbot_core/domain/models/transfer_line.py",
    "packages/workbot_core/domain/models/purchase_log.py",
    "packages/workbot_core/domain/models/purchase_log_line.py",

    "packages/workbot_core/domain/value_objects/money.py",
    "packages/workbot_core/domain/value_objects/quantity.py",
    "packages/workbot_core/domain/value_objects/date_range.py",
    "packages/workbot_core/domain/value_objects/identifiers.py",

    "packages/workbot_core/domain/rules/item_matching.py",
    "packages/workbot_core/domain/rules/vendor_matching.py",
    "packages/workbot_core/domain/rules/order_rules.py",
    "packages/workbot_core/domain/rules/purchase_price_rules.py",

    "packages/workbot_core/application/interfaces/repositories.py",
    "packages/workbot_core/application/interfaces/readers.py",
    "packages/workbot_core/application/interfaces/writers.py",
    "packages/workbot_core/application/interfaces/automation.py",
    "packages/workbot_core/application/interfaces/files.py",
    "packages/workbot_core/application/interfaces/email.py",

    "packages/workbot_core/application/services/item_service.py",
    "packages/workbot_core/application/services/vendor_service.py",
    "packages/workbot_core/application/services/store_service.py",
    "packages/workbot_core/application/services/order_service.py",
    "packages/workbot_core/application/services/audit_service.py",
    "packages/workbot_core/application/services/transfer_service.py",

    "packages/workbot_core/application/use_cases/import_purchase_log.py",
    "packages/workbot_core/application/use_cases/download_orders.py",
    "packages/workbot_core/application/use_cases/generate_vendor_upload_file.py",
    "packages/workbot_core/application/use_cases/generate_vendor_order_emails.py",
    "packages/workbot_core/application/use_cases/download_audits.py",
    "packages/workbot_core/application/use_cases/input_transfers.py",
    "packages/workbot_core/application/use_cases/manage_items.py",
    "packages/workbot_core/application/use_cases/manage_vendors.py",
    "packages/workbot_core/application/use_cases/manage_stores.py",
    "packages/workbot_core/application/use_cases/migrate_existing_data.py",

    "packages/workbot_core/application/dto/purchase_log_row.py",
    "packages/workbot_core/application/dto/craftable_order_row.py",
    "packages/workbot_core/application/dto/craftable_audit_row.py",
    "packages/workbot_core/application/dto/vendor_upload_row.py",
    "packages/workbot_core/application/dto/import_result.py",
    "packages/workbot_core/application/dto/generated_file.py",
    "packages/workbot_core/application/dto/operation_result.py",

    "packages/workbot_core/application/transactions.py",

    "packages/workbot_core/infrastructure/database/base.py",
    "packages/workbot_core/infrastructure/database/session.py",
    "packages/workbot_core/infrastructure/database/unit_of_work.py",

    "packages/workbot_core/infrastructure/database/records/store_record.py",
    "packages/workbot_core/infrastructure/database/records/vendor_record.py",
    "packages/workbot_core/infrastructure/database/records/item_record.py",
    "packages/workbot_core/infrastructure/database/records/item_store_info_record.py",
    "packages/workbot_core/infrastructure/database/records/item_vendor_info_record.py",
    "packages/workbot_core/infrastructure/database/records/order_record.py",
    "packages/workbot_core/infrastructure/database/records/order_line_record.py",
    "packages/workbot_core/infrastructure/database/records/audit_record.py",
    "packages/workbot_core/infrastructure/database/records/audit_line_record.py",
    "packages/workbot_core/infrastructure/database/records/transfer_record.py",
    "packages/workbot_core/infrastructure/database/records/transfer_line_record.py",
    "packages/workbot_core/infrastructure/database/records/purchase_log_record.py",
    "packages/workbot_core/infrastructure/database/records/purchase_log_line_record.py",

    "packages/workbot_core/infrastructure/database/repositories/store_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/vendor_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/item_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/item_store_info_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/item_vendor_info_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/order_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/audit_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/transfer_repository.py",
    "packages/workbot_core/infrastructure/database/repositories/purchase_log_repository.py",

    "packages/workbot_core/infrastructure/database/mappers/store_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/vendor_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/item_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/item_store_info_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/item_vendor_info_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/order_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/audit_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/transfer_mapper.py",
    "packages/workbot_core/infrastructure/database/mappers/purchase_log_mapper.py",

    "packages/workbot_core/infrastructure/craftable/craftable_bot.py",
    "packages/workbot_core/infrastructure/craftable/craftable_client.py",
    "packages/workbot_core/infrastructure/craftable/selenium_driver_factory.py",
    "packages/workbot_core/infrastructure/craftable/craftable_table_reader.py",
    "packages/workbot_core/infrastructure/craftable/craftable_order_reader.py",
    "packages/workbot_core/infrastructure/craftable/craftable_audit_reader.py",
    "packages/workbot_core/infrastructure/craftable/craftable_transfer_writer.py",

    "packages/workbot_core/infrastructure/excel/workbook_loader.py",
    "packages/workbot_core/infrastructure/excel/excel_reader.py",
    "packages/workbot_core/infrastructure/excel/excel_writer.py",
    "packages/workbot_core/infrastructure/excel/readers/purchase_log_reader.py",
    "packages/workbot_core/infrastructure/excel/readers/order_download_reader.py",
    "packages/workbot_core/infrastructure/excel/readers/audit_download_reader.py",
    "packages/workbot_core/infrastructure/excel/readers/transfer_input_reader.py",
    "packages/workbot_core/infrastructure/excel/writers/vendor_upload_writer.py",
    "packages/workbot_core/infrastructure/excel/writers/vendor_email_attachment_writer.py",
    "packages/workbot_core/infrastructure/excel/writers/audit_export_writer.py",
    "packages/workbot_core/infrastructure/excel/writers/transfer_export_writer.py",

    "packages/workbot_core/infrastructure/files/file_manager.py",
    "packages/workbot_core/infrastructure/files/file_namer.py",
    "packages/workbot_core/infrastructure/files/path_resolver.py",
    "packages/workbot_core/infrastructure/files/archive_service.py",
    "packages/workbot_core/infrastructure/files/download_monitor.py",

    "packages/workbot_core/infrastructure/email/email_client.py",
    "packages/workbot_core/infrastructure/email/email_message_builder.py",
    "packages/workbot_core/infrastructure/email/attachment_builder.py",
    "packages/workbot_core/infrastructure/email/templates/vendor_order_email.txt",
    "packages/workbot_core/infrastructure/email/templates/transfer_notice_email.txt",
    "packages/workbot_core/infrastructure/email/templates/audit_notice_email.txt",

    "packages/workbot_core/infrastructure/legacy/json_loaders.py",
    "packages/workbot_core/infrastructure/legacy/legacy_item_serializer.py",
    "packages/workbot_core/infrastructure/legacy/legacy_vendor_serializer.py",
    "packages/workbot_core/infrastructure/legacy/legacy_store_serializer.py",
    "packages/workbot_core/infrastructure/legacy/legacy_order_serializer.py",

    "packages/workbot_core/utils/dates.py",
    "packages/workbot_core/utils/strings.py",
    "packages/workbot_core/utils/ids.py",
    "packages/workbot_core/utils/validation.py",
    "packages/workbot_core/utils/exceptions.py",
]


FILE_CONTENTS = {
    "README.md": """
        # WorkBot

        WorkBot is a database-backed operations automation app for inventory,
        ordering, audits, transfers, Craftable workflows, Excel exports, and
        vendor communications.

        ## Structure

        - `apps/cli`: command-line interface
        - `apps/api`: FastAPI backend
        - `apps/web`: reserved for future web frontend
        - `packages/workbot_core`: shared domain, application, and infrastructure code
    """,

    "pyproject.toml": """
        [project]
        name = "workbot"
        version = "0.1.0"
        description = "WorkBot operations automation platform"
        requires-python = ">=3.11"
        dependencies = [
            "fastapi",
            "uvicorn[standard]",
            "sqlalchemy",
            "alembic",
            "pydantic",
            "pydantic-settings",
            "openpyxl",
            "selenium",
        ]

        [project.optional-dependencies]
        dev = [
            "pytest",
            "ruff",
            "mypy",
        ]

        [project.scripts]
        workbot = "apps.cli.main:main"
        workbot-api = "apps.api.main:main"

        [tool.ruff]
        line-length = 100

        [tool.mypy]
        python_version = "3.11"
        strict = true
    """,

    "alembic.ini": """
        [alembic]
        script_location = alembic
        prepend_sys_path = .
        sqlalchemy.url = sqlite:///data/workbot.db

        [loggers]
        keys = root,sqlalchemy,alembic

        [handlers]
        keys = console

        [formatters]
        keys = generic

        [logger_root]
        level = WARN
        handlers = console

        [logger_sqlalchemy]
        level = WARN
        handlers =
        qualname = sqlalchemy.engine

        [logger_alembic]
        level = INFO
        handlers =
        qualname = alembic

        [handler_console]
        class = StreamHandler
        args = (sys.stderr,)
        level = NOTSET
        formatter = generic

        [formatter_generic]
        format = %(levelname)-5.5s [%(name)s] %(message)s
        datefmt = %H:%M:%S
    """,

    "alembic/env.py": """
        from __future__ import annotations

        from logging.config import fileConfig

        from alembic import context
        from sqlalchemy import engine_from_config, pool

        from packages.workbot_core.infrastructure.database.base import Base

        config = context.config

        if config.config_file_name is not None:
            fileConfig(config.config_file_name)

        target_metadata = Base.metadata


        def run_migrations_offline() -> None:
            url = config.get_main_option("sqlalchemy.url")
            context.configure(
                url=url,
                target_metadata=target_metadata,
                literal_binds=True,
                dialect_opts={"paramstyle": "named"},
            )

            with context.begin_transaction():
                context.run_migrations()


        def run_migrations_online() -> None:
            connectable = engine_from_config(
                config.get_section(config.config_ini_section, {}),
                prefix="sqlalchemy.",
                poolclass=pool.NullPool,
            )

            with connectable.connect() as connection:
                context.configure(connection=connection, target_metadata=target_metadata)

                with context.begin_transaction():
                    context.run_migrations()


        if context.is_offline_mode():
            run_migrations_offline()
        else:
            run_migrations_online()
    """,

    "apps/cli/main.py": """
        from __future__ import annotations

        from apps.cli.app import run_cli


        def main() -> None:
            run_cli()


        if __name__ == "__main__":
            main()
    """,

    "apps/cli/app.py": """
        from __future__ import annotations


        def run_cli() -> None:
            print("WorkBot CLI")
            print("TODO: wire command registry and application container.")
    """,

    "apps/api/main.py": """
        from __future__ import annotations

        import uvicorn
        from fastapi import FastAPI

        from apps.api.routes import health


        def create_app() -> FastAPI:
            app = FastAPI(title="WorkBot API", version="0.1.0")
            app.include_router(health.router)
            return app


        app = create_app()


        def main() -> None:
            uvicorn.run("apps.api.main:app", host="127.0.0.1", port=8000, reload=True)


        if __name__ == "__main__":
            main()
    """,

    "apps/api/dependencies.py": """
        from __future__ import annotations

        from functools import lru_cache

        from packages.workbot_core.bootstrap.container import Container, build_container


        @lru_cache(maxsize=1)
        def get_container() -> Container:
            return build_container()
    """,

    "apps/api/routes/health.py": """
        from __future__ import annotations

        from fastapi import APIRouter

        router = APIRouter(prefix="/health", tags=["health"])


        @router.get("")
        def health_check() -> dict[str, str]:
            return {"status": "ok"}
    """,

    "apps/web/README.md": """
        # WorkBot Web

        Reserved for a future web frontend.

        Suggested future stack:

        - React
        - Vite
        - TypeScript
        - API client targeting `apps/api`
    """,

    "packages/workbot_core/config/settings.py": """
        from __future__ import annotations

        from pydantic_settings import BaseSettings, SettingsConfigDict


        class Settings(BaseSettings):
            database_url: str = "sqlite:///data/workbot.db"

            model_config = SettingsConfigDict(
                env_file=".env",
                env_file_encoding="utf-8",
                extra="ignore",
            )


        settings = Settings()
    """,

    "packages/workbot_core/config/paths.py": """
        from __future__ import annotations

        from pathlib import Path


        PROJECT_ROOT = Path(__file__).resolve().parents[3]
        DATA_DIR = PROJECT_ROOT / "data"

        IMPORTS_DIR = DATA_DIR / "imports"
        EXPORTS_DIR = DATA_DIR / "exports"
        DOWNLOADS_DIR = DATA_DIR / "downloads"
        BACKUPS_DIR = DATA_DIR / "backups"
        ARCHIVE_DIR = DATA_DIR / "archive"
    """,

    "packages/workbot_core/bootstrap/container.py": """
        from __future__ import annotations

        from dataclasses import dataclass


        @dataclass(slots=True)
        class Container:
            \"\"\"Application dependency container.

            Add repositories, services, and use cases here as the project is implemented.
            \"\"\"


        def build_container() -> Container:
            return Container()
    """,

    "packages/workbot_core/infrastructure/database/base.py": """
        from __future__ import annotations

        from sqlalchemy.orm import DeclarativeBase


        class Base(DeclarativeBase):
            pass
    """,

    "packages/workbot_core/infrastructure/database/session.py": """
        from __future__ import annotations

        from collections.abc import Iterator

        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session, sessionmaker

        from packages.workbot_core.config.settings import settings


        engine = create_engine(settings.database_url, echo=False, future=True)

        SessionFactory = sessionmaker(
            bind=engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )


        def get_session() -> Iterator[Session]:
            session = SessionFactory()
            try:
                yield session
            finally:
                session.close()
    """,

    "packages/workbot_core/utils/exceptions.py": """
        from __future__ import annotations


        class WorkBotError(Exception):
            \"\"\"Base exception for WorkBot.\"\"\"


        class ConfigurationError(WorkBotError):
            \"\"\"Raised when application configuration is invalid.\"\"\"


        class RepositoryError(WorkBotError):
            \"\"\"Raised when persistence operations fail.\"\"\"
    """,
}


def normalize_content(content: str) -> str:
    return dedent(content).strip() + "\n"


def create_directories(root: Path) -> None:
    for directory in DIRECTORIES:
        path = root / directory
        path.mkdir(parents=True, exist_ok=True)


def create_python_packages(root: Path) -> None:
    for package in PYTHON_PACKAGES:
        init_file = root / package / "__init__.py"
        init_file.parent.mkdir(parents=True, exist_ok=True)
        init_file.touch(exist_ok=True)


def create_empty_files(root: Path) -> None:
    for file_path in EMPTY_FILES:
        path = root / file_path
        path.parent.mkdir(parents=True, exist_ok=True)

        if not path.exists():
            path.write_text("", encoding="utf-8")


def create_content_files(root: Path) -> None:
    for file_path, content in FILE_CONTENTS.items():
        path = root / file_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(normalize_content(content), encoding="utf-8")


def main() -> None:
    PROJECT_ROOT.mkdir(parents=True, exist_ok=True)

    create_directories(PROJECT_ROOT)
    create_python_packages(PROJECT_ROOT)
    create_empty_files(PROJECT_ROOT)
    create_content_files(PROJECT_ROOT)

    print(f"Created WorkBot project structure at: {PROJECT_ROOT.resolve()}")


if __name__ == "__main__":
    main()