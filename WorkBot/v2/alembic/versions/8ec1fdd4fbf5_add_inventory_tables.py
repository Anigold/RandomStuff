"""add inventory tables

Revision ID: 8ec1fdd4fbf5
Revises: e9fa9e2a49b1
Create Date: 2026-07-09 07:39:06.553219

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ec1fdd4fbf5'
down_revision: Union[str, Sequence[str], None] = 'e9fa9e2a49b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory_counts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("store_id", sa.String(), nullable=False),
        sa.Column("count_date", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["store_id"], ["stores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_inventory_counts_store_id"),
        "inventory_counts",
        ["store_id"],
        unique=False,
    )

    op.create_table(
        "inventory_count_lines",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("inventory_count_id", sa.String(), nullable=False),
        sa.Column("item_id", sa.String(), nullable=False),
        sa.Column("quantity", sa.Numeric(), nullable=False),
        sa.Column("unit", sa.String(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["inventory_count_id"], ["inventory_counts.id"]),
        sa.ForeignKeyConstraint(["item_id"], ["items.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_inventory_count_lines_inventory_count_id"),
        "inventory_count_lines",
        ["inventory_count_id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_inventory_count_lines_item_id"),
        "inventory_count_lines",
        ["item_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_inventory_count_lines_item_id"),
        table_name="inventory_count_lines",
    )
    op.drop_index(
        op.f("ix_inventory_count_lines_inventory_count_id"),
        table_name="inventory_count_lines",
    )
    op.drop_table("inventory_count_lines")

    op.drop_index(
        op.f("ix_inventory_counts_store_id"),
        table_name="inventory_counts",
    )
    op.drop_table("inventory_counts")