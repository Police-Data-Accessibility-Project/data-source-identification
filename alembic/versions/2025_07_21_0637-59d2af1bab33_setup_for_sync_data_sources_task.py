"""Setup for sync data sources task

Revision ID: 59d2af1bab33
Revises: 9552d354ccf4
Create Date: 2025-07-21 06:37:51.043504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import switch_enum_type, id_column

# revision identifiers, used by Alembic.
revision: str = '59d2af1bab33'
down_revision: Union[str, None] = '9552d354ccf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

SYNC_STATE_TABLE_NAME = "data_sources_sync_state"
URL_DATA_SOURCES_METADATA_TABLE_NAME = "url_data_sources_metadata"

def _create_data_sources_sync_state_table() -> None:
    table = op.create_table(
        SYNC_STATE_TABLE_NAME,
        id_column(),
        sa.Column('last_full_sync_at', sa.DateTime(), nullable=True),
        sa.Column('current_cutoff_date', sa.Date(), nullable=True),
        sa.Column('current_page', sa.Integer(), nullable=True),
    )
    # Add row to `data_sources_sync_state` table
    op.bulk_insert(
        table,
        [
            {
                "last_full_sync_at": None,
                "current_cutoff_date": None,
                "current_page": None
            }
        ]
    )

def _drop_data_sources_sync_state_table() -> None:
    op.drop_table(SYNC_STATE_TABLE_NAME)

def _create_data_sources_sync_task() -> None:
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
            'Sync Data Sources'
        ]
    )

def _drop_data_sources_sync_task() -> None:
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=[
            'HTML',
            'Relevancy',
            'Record Type',
            'Agency Identification',
            'Misc Metadata',
            'Submit Approved URLs',
            'Duplicate Detection',
            '404 Probe',
            'Sync Agencies',
        ]
    )


def upgrade() -> None:
    _create_data_sources_sync_state_table()
    _create_data_sources_sync_task()


def downgrade() -> None:
    _drop_data_sources_sync_task()
    _drop_data_sources_sync_state_table()
