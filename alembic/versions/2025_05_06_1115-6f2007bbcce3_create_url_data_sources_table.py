"""Create url_data_sources table

Revision ID: 6f2007bbcce3
Revises: f25852e17c04
Create Date: 2025-05-06 11:15:24.485465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6f2007bbcce3'
down_revision: Union[str, None] = 'f25852e17c04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create url_data_sources_table table
    op.create_table(
        'url_data_sources',
        sa.Column(
            'id',
            sa.Integer(),
            primary_key=True
        ),
        sa.Column(
            'url_id',
            sa.Integer(),
            sa.ForeignKey(
                'urls.id',
                ondelete='CASCADE'
            ),
            nullable=False
        ),
        sa.Column(
            'data_source_id',
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text('now()')
        ),
        sa.UniqueConstraint('url_id', name='uq_url_data_sources_url_id'),
        sa.UniqueConstraint('data_source_id', name='uq_url_data_sources_data_source_id')
    )

    # Migrate existing urls with a data source ID
    op.execute("""
        INSERT INTO url_data_sources 
        (url_id, data_source_id) 
        SELECT id, data_source_id 
        FROM urls 
        WHERE data_source_id IS NOT NULL
    """)

    # Drop existing data source ID column from urls table
    op.drop_column('urls', 'data_source_id')


def downgrade() -> None:

    op.drop_table('url_data_sources')

    op.add_column(
        'urls',
        sa.Column(
            'data_source_id',
            sa.Integer(),
            nullable=True
        )
    )


