"""Update agencies table and add `agencies_sync_state` table

Revision ID: fb199cf58ecd
Revises: c1380f90f5de
Create Date: 2025-06-16 09:22:05.813695

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import created_at_column, updated_at_column, switch_enum_type

# revision identifiers, used by Alembic.
revision: str = 'fb199cf58ecd'
down_revision: Union[str, None] = 'c1380f90f5de'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

AGENCIES_TABLE_NAME = 'agencies'

def upgrade() -> None:
    op.add_column(
        AGENCIES_TABLE_NAME,
        created_at_column()
    )

    op.add_column(
        AGENCIES_TABLE_NAME,
        sa.Column('ds_last_updated_at', sa.DateTime(), nullable=True)
    )

    op.create_table(
        'agencies_sync_state',
        sa.Column('last_full_sync_at', sa.DateTime(), nullable=True),
        sa.Column('current_cutoff_date', sa.Date(), nullable=True),
        sa.Column('current_page', sa.Integer(), nullable=True),
    )

    # Add row to `agencies_sync_state` table
    op.execute('INSERT INTO agencies_sync_state VALUES (null, null, null)')

    # Add 'Sync Agencies' to TaskType Enum
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


def downgrade() -> None:
    for column in ['ds_last_updated_at', 'created_at']:
        op.drop_column(AGENCIES_TABLE_NAME, column)

    op.drop_table('agencies_sync_state')

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
        ]
    )
