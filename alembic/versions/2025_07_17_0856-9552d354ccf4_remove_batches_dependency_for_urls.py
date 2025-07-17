"""Remove batches dependency for urls

Revision ID: 9552d354ccf4
Revises: d6519a3ca5c9
Create Date: 2025-07-17 08:56:22.919486

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, created_at_column, updated_at_column, url_id_column, batch_id_column

# revision identifiers, used by Alembic.
revision: str = '9552d354ccf4'
down_revision: Union[str, None] = 'd6519a3ca5c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

LINK_TABLE_NAME = 'link_batch_urls'

BATCHES_COLUMN_NAME = 'batch_id'

def _create_link_table():
    op.create_table(
        LINK_TABLE_NAME,
        id_column(),
        batch_id_column(),
        url_id_column(),
        created_at_column(),
        updated_at_column(),
        sa.UniqueConstraint('url_id', name='uq_link_table_url_id')
    )

def _drop_link_table():
    op.drop_table(LINK_TABLE_NAME)

def _migrate_batch_ids_to_link_table():
    op.execute(f"""
    INSERT INTO {LINK_TABLE_NAME} (batch_id, url_id)
    SELECT batch_id, id
    FROM urls
    """)

def _migrate_link_table_to_batch_ids():
    op.execute(f"""
    UPDATE urls
    SET batch_id = (
        SELECT batch_id
        FROM {LINK_TABLE_NAME}
        WHERE url_id = urls.id
    )
    """)

def _drop_url_batches_column():
    op.drop_column('urls', BATCHES_COLUMN_NAME)

def _add_url_batches_column():
    op.add_column(
        'urls',
        batch_id_column(nullable=True)
    )

def _add_not_null_constraint():
    op.alter_column(
        'urls',
        BATCHES_COLUMN_NAME,
        nullable=False
    )


def upgrade() -> None:
    _create_link_table()
    _migrate_batch_ids_to_link_table()
    _drop_url_batches_column()


def downgrade() -> None:
    _add_url_batches_column()
    _migrate_link_table_to_batch_ids()
    _add_not_null_constraint()
    _drop_link_table()
