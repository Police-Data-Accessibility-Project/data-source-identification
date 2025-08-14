"""Add Internet Archive Tables

Revision ID: 2a7192657354
Revises: 49fd9f295b8d
Create Date: 2025-08-14 07:22:15.308210

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import url_id_column, created_at_column, id_column, updated_at_column

# revision identifiers, used by Alembic.
revision: str = '2a7192657354'
down_revision: Union[str, None] = '49fd9f295b8d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

IA_METADATA_TABLE_NAME = "urls_internet_archive_metadata"
IA_FLAGS_TABLE_NAME = "flag_url_checked_for_internet_archive"

def upgrade() -> None:
    _create_metadata_table()
    _create_flags_table()

def _create_metadata_table():
    op.create_table(
        IA_METADATA_TABLE_NAME,
        id_column(),
        url_id_column(),
        sa.Column('archive_url', sa.String(), nullable=False),
        sa.Column('digest', sa.String(), nullable=False),
        sa.Column('length', sa.Integer(), nullable=False),
        created_at_column(),
        updated_at_column(),
        sa.UniqueConstraint('url_id', name='uq_url_id_internet_archive_metadata')
    )

def _create_flags_table():
    op.create_table(
        IA_FLAGS_TABLE_NAME,
        url_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id')
    )

def downgrade() -> None:
    op.drop_table(IA_METADATA_TABLE_NAME)
    op.drop_table(IA_FLAGS_TABLE_NAME)
