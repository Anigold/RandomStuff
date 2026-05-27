"""add order source import uniqueness

Revision ID: f934230e8f45
Revises: beb5a6e1ee0c
Create Date: 2026-05-27 06:43:03.485935

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f934230e8f45'
down_revision: Union[str, Sequence[str], None] = 'beb5a6e1ee0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.create_unique_constraint(
            "uq_order_source_import",
            [
                "store_id",
                "vendor_id",
                "order_date",
                "source",
                "source_reference",
            ],
        )


def downgrade() -> None:
    with op.batch_alter_table("orders") as batch_op:
        batch_op.drop_constraint(
            "uq_order_source_import",
            type_="unique",
        )