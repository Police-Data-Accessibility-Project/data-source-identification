"""Add link_urls_redirect_url table

Revision ID: 571ada5b81b9
Revises: 99eceed6e614
Create Date: 2025-08-03 18:00:06.345733

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, created_at_column, updated_at_column

# revision identifiers, used by Alembic.
revision: str = '571ada5b81b9'
down_revision: Union[str, None] = '99eceed6e614'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

URLS_TABLE = 'urls'
LINK_URLS_REDIRECT_URL_TABLE = 'link_urls_redirect_url'

SOURCE_ENUM = sa.Enum(
    'collector',
    'data_sources_app',
    'redirect',
    'root_url',
    'manual',
    name='url_source'
)

def upgrade() -> None:
    _create_link_urls_redirect_url_table()
    _add_source_column_to_urls_table()



def downgrade() -> None:
    _drop_link_urls_redirect_url_table()
    _drop_source_column_from_urls_table()


def _create_link_urls_redirect_url_table():
    op.create_table(
        LINK_URLS_REDIRECT_URL_TABLE,
        id_column(),
        sa.Column('source_url_id', sa.Integer(), nullable=False),
        sa.Column('destination_url_id', sa.Integer(), nullable=False),
        created_at_column(),
        updated_at_column(),
        sa.ForeignKeyConstraint(['source_url_id'], [URLS_TABLE + '.id'], ),
        sa.ForeignKeyConstraint(['destination_url_id'], [URLS_TABLE + '.id'], ),
        sa.UniqueConstraint(
            'source_url_id',
            'destination_url_id',
            name='link_urls_redirect_url_uq_source_url_id_destination_url_id'
        ),
    )


def _add_source_column_to_urls_table():
    # Create enum
    SOURCE_ENUM.create(op.get_bind(), checkfirst=True)
    op.add_column(
        URLS_TABLE,
        sa.Column(
            'source',
            SOURCE_ENUM,
            nullable=True,
            comment='The source of the URL.'
        )
    )
    # Add sources to existing URLs
    op.execute(
        f"""UPDATE {URLS_TABLE}
        SET source = 'collector'::url_source
        """
    )
    op.execute(
        f"""UPDATE {URLS_TABLE}
        SET source = 'data_sources_app'::url_source
        FROM url_data_sources WHERE url_data_sources.url_id = {URLS_TABLE}.id
        AND url_data_sources.data_source_id IS NOT NULL;
        """
    )
    op.execute(
        f"""UPDATE {URLS_TABLE}
        SET source = 'collector'::url_source
        FROM link_batch_urls WHERE link_batch_urls.url_id = {URLS_TABLE}.id
        AND link_batch_urls.batch_id IS NOT NULL;
        """
    )

    # Make source required
    op.alter_column(
        URLS_TABLE,
        'source',
        nullable=False
    )


def _drop_link_urls_redirect_url_table():
    op.drop_table(LINK_URLS_REDIRECT_URL_TABLE)


def _drop_source_column_from_urls_table():
    op.drop_column(URLS_TABLE, 'source')
    # Drop enum
    SOURCE_ENUM.drop(op.get_bind(), checkfirst=True)
