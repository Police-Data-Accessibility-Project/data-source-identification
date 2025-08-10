"""Add scheduled tasks

Revision ID: 11ece61d7ac2
Revises: 8cd5aa7670ff
Create Date: 2025-08-10 10:32:11.400714

"""
from typing import Sequence, Union

from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '11ece61d7ac2'
down_revision: Union[str, None] = '8cd5aa7670ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
            'Sync Data Sources',
            'Push to Hugging Face',
            'URL Probe',
            'Populate Backlog Snapshot',
            'Delete Old Logs',
            'Run URL Task Cycles'
        ]
    )


def downgrade() -> None:
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
            'Push to Hugging Face',
            'URL Probe'
        ]
    )
