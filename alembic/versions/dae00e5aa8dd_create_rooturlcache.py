"""Create RootURLCache

Revision ID: dae00e5aa8dd
Revises: dcd158092de0
Create Date: 2025-01-19 10:40:19.650982

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'dae00e5aa8dd'
down_revision: Union[str, None] = 'dcd158092de0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('root_url_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('page_title', sa.String(), nullable=False),
        sa.Column('page_description', sa.String(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url', name='root_url_cache_uq_url')
    )


def downgrade() -> None:
    op.drop_table('root_url_cache')
