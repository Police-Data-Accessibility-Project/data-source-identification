"""Remove agencies.ds_last_updated_at

Revision ID: 9a56916ea7d8
Revises: c14d669d7c0d
Create Date: 2025-08-11 09:31:18.268319

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a56916ea7d8'
down_revision: Union[str, None] = 'c14d669d7c0d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COLUMN_NAME = "ds_last_updated_at"
TABLE_NAME = "agencies"

def upgrade() -> None:
    op.drop_column(TABLE_NAME, COLUMN_NAME)


def downgrade() -> None:
    op.add_column(
        table_name=TABLE_NAME,
        column=sa.Column(COLUMN_NAME, sa.DateTime(), nullable=False),
    )
