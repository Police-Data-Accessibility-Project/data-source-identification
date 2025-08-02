"""Add HTML Status Info table

Revision ID: 99eceed6e614
Revises: 637de6eaa3ab
Create Date: 2025-07-31 15:36:40.966605

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, created_at_column, updated_at_column, url_id_column, switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '99eceed6e614'
down_revision: Union[str, None] = '637de6eaa3ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

WEB_STATUS_ENUM = sa.Enum(
    "not_attempted",
    "success",
    "error",
    "404_not_found",
    name="web_status"
)

TABLE_NAME = 'url_web_metadata'

def _add_url_probe_task_type_enum() -> None:
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
            'URL Probe'
        ]
    )

def _drop_url_probe_task_type_enum() -> None:
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
            'Push to Hugging Face'
        ]
    )

def _create_url_html_info_table() -> None:
    op.create_table(
        TABLE_NAME,
        id_column(),
        url_id_column(),
        sa.Column('accessed', sa.Boolean(), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('content_type', sa.Text(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        created_at_column(),
        updated_at_column(),
        sa.UniqueConstraint('url_id', name='uq_url_web_status_info_url_id'),
        sa.CheckConstraint('status_code >= 100', name='ck_url_web_status_info_status_code_min'),
        sa.CheckConstraint('status_code <= 999', name='ck_url_web_status_info_status_code_max'),
    )

def _drop_url_html_info_table() -> None:
    op.drop_table(TABLE_NAME)


def upgrade() -> None:
    _create_url_html_info_table()
    _add_url_probe_task_type_enum()


def downgrade() -> None:
    _drop_url_html_info_table()
    # Drop Enums
    WEB_STATUS_ENUM.drop(op.get_bind(), checkfirst=True)
    _drop_url_probe_task_type_enum()