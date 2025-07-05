"""Add url_compressed_html table

Revision ID: 4b0f43f61598
Revises: fb199cf58ecd
Create Date: 2025-07-05 08:01:58.124060

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import created_at_column, updated_at_column, id_column

# revision identifiers, used by Alembic.
revision: str = '4b0f43f61598'
down_revision: Union[str, None] = 'fb199cf58ecd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = 'url_compressed_html'

def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        id_column(),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.Column('compressed_html', sa.LargeBinary(), nullable=False),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id'], name='fk_url_compressed_html_url_id'),
        sa.UniqueConstraint('url_id', name='uq_url_compressed_html_url_id')
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)
