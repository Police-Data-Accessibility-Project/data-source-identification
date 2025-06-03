"""Remove unused batch columns

Revision ID: c1380f90f5de
Revises: 00cc949e0347
Create Date: 2025-06-03 08:14:15.583777

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1380f90f5de'
down_revision: Union[str, None] = '00cc949e0347'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "batches"
TOTAL_URL_COUNT_COLUMN = "total_url_count"
ORIGINAL_URL_COUNT_COLUMN = "original_url_count"
DUPLICATE_URL_COUNT_COLUMN = "duplicate_url_count"

def upgrade() -> None:
    for column in [
        TOTAL_URL_COUNT_COLUMN,
        ORIGINAL_URL_COUNT_COLUMN,
        DUPLICATE_URL_COUNT_COLUMN,
    ]:
        op.drop_column(TABLE_NAME, column)


def downgrade() -> None:
    for column in [
        TOTAL_URL_COUNT_COLUMN,
        ORIGINAL_URL_COUNT_COLUMN,
        DUPLICATE_URL_COUNT_COLUMN,
    ]:
        op.add_column(
            TABLE_NAME,
            sa.Column(column, sa.Integer(), nullable=False, default=0),
        )
