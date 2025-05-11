"""Set default created_at for backlog_snapshot

Revision ID: 9d4002437ebe
Revises: 6f2007bbcce3
Create Date: 2025-05-11 10:54:22.797147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d4002437ebe'
down_revision: Union[str, None] = '6f2007bbcce3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        table_name='backlog_snapshot',
        column_name='created_at',
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=sa.text('now()')
    )


def downgrade() -> None:
    op.alter_column(
        table_name='backlog_snapshots',
        column_name='created_at',
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None
    )
