"""renamed vendor store ids to store references to reflect the vendor stored identifier rather than our internal reference

Revision ID: dda3fca2ef6d
Revises: 6917dbafc659
Create Date: 2026-06-03 08:31:45.437629

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dda3fca2ef6d"
down_revision: Union[str, Sequence[str], None] = "6917dbafc659"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


vendors_table = sa.table(
    "vendors",
    sa.column("id", sa.String()),
    sa.column("store_ids_json", sa.JSON()),
    sa.column("store_references_json", sa.JSON()),
)


def upgrade() -> None:
    op.add_column(
        "vendors",
        sa.Column(
            "store_references_json",
            sa.JSON(),
            nullable=True,
        ),
    )

    connection = op.get_bind()

    rows = connection.execute(
        sa.select(
            vendors_table.c.id,
            vendors_table.c.store_ids_json,
        )
    ).mappings()

    for row in rows:
        raw_store_ids = row["store_ids_json"] or []

        store_references = []

        if isinstance(raw_store_ids, list):
            for value in raw_store_ids:
                if isinstance(value, str):
                    store_references.append(
                        {
                            "store_id": value,
                            "vendor_store_reference": "",
                        }
                    )
                elif isinstance(value, dict):
                    store_id = value.get("store_id") or value.get("id")

                    if store_id:
                        store_references.append(
                            {
                                "store_id": str(store_id),
                                "vendor_store_reference": str(
                                    value.get("vendor_store_reference", "")
                                ),
                            }
                        )

        connection.execute(
            vendors_table.update()
            .where(vendors_table.c.id == row["id"])
            .values(store_references_json=store_references)
        )

    op.drop_column("vendors", "store_ids_json")


def downgrade() -> None:
    op.add_column(
        "vendors",
        sa.Column(
            "store_ids_json",
            sa.JSON(),
            nullable=True,
        ),
    )

    connection = op.get_bind()

    rows = connection.execute(
        sa.select(
            vendors_table.c.id,
            vendors_table.c.store_references_json,
        )
    ).mappings()

    for row in rows:
        raw_references = row["store_references_json"] or []

        store_ids = []

        if isinstance(raw_references, list):
            for value in raw_references:
                if isinstance(value, dict):
                    store_id = value.get("store_id")

                    if store_id:
                        store_ids.append(str(store_id))
                elif isinstance(value, str):
                    store_ids.append(value)

        connection.execute(
            vendors_table.update()
            .where(vendors_table.c.id == row["id"])
            .values(store_ids_json=store_ids)
        )

    op.drop_column("vendors", "store_references_json")