"""Create BacklogSnapshot Table

Revision ID: e55e16e0738f
Revises: 028565b77b9e
Create Date: 2025-05-06 08:16:29.385305

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e55e16e0738f'
down_revision: Union[str, None] = '028565b77b9e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'backlog_snapshot',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('count_pending_total', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('backlog_snapshot')
