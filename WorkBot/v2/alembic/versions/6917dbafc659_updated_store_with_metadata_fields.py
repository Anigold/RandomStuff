"""updated store with metadata fields

Revision ID: 6917dbafc659
Revises: 79f2797bd94f
Create Date: 2026-06-02 08:38:59.059728

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6917dbafc659'
down_revision: Union[str, Sequence[str], None] = '79f2797bd94f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
   pass