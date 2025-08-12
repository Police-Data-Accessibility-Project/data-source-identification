"""Refine root table logic

Revision ID: 49fd9f295b8d
Revises: 9a56916ea7d8
Create Date: 2025-08-12 08:19:08.170835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column, updated_at_column, url_id_column, created_at_column, switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '49fd9f295b8d'
down_revision: Union[str, None] = '9a56916ea7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

ROOT_URLS_TABLE_NAME = "root_urls"
ROOT_URL_CACHE_TABLE_NAME = "root_url_cache"

LINK_URLS_ROOT_URL_TABLE_NAME = "link_urls_root_url"
FLAG_ROOT_URL_TABLE_NAME = "flag_root_url"




def upgrade() -> None:
    _drop_root_url_cache()
    _drop_root_urls()
    _create_flag_root_url()
    _create_link_urls_root_url()
    _add_root_url_task_enum()


def downgrade() -> None:
    _create_root_url_cache()
    _create_root_urls()
    _drop_link_urls_root_url()
    _drop_flag_root_url()
    _remove_root_url_task_enum()

def _add_root_url_task_enum():
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
            'Run URL Task Cycles',
            'Root URL'
        ]
    )


def _remove_root_url_task_enum():
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


def _drop_root_url_cache():
    op.drop_table(ROOT_URL_CACHE_TABLE_NAME)

def _drop_root_urls():
    op.drop_table(ROOT_URLS_TABLE_NAME)

def _create_root_url_cache():
    op.create_table(
        ROOT_URL_CACHE_TABLE_NAME,
        id_column(),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('page_title', sa.String(), nullable=False),
        sa.Column('page_description', sa.String(), nullable=True),
        updated_at_column(),
        sa.UniqueConstraint('url', name='root_url_cache_uq_url')
    )

def _create_root_urls():
    op.create_table(
        ROOT_URLS_TABLE_NAME,
        id_column(),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('page_title', sa.String(), nullable=False),
        sa.Column('page_description', sa.String(), nullable=True),
        updated_at_column(),
        sa.UniqueConstraint('url', name='uq_root_url_url')
    )

def _create_link_urls_root_url():
    op.create_table(
        LINK_URLS_ROOT_URL_TABLE_NAME,
        id_column(),
        url_id_column(),
        url_id_column('root_url_id'),
        created_at_column(),
        updated_at_column(),
        sa.UniqueConstraint('url_id', 'root_url_id')
    )

def _drop_link_urls_root_url():
    op.drop_table(LINK_URLS_ROOT_URL_TABLE_NAME)

def _create_flag_root_url():
    op.create_table(
        FLAG_ROOT_URL_TABLE_NAME,
        url_id_column(),
        created_at_column(),
        sa.PrimaryKeyConstraint('url_id')
    )

def _drop_flag_root_url():
    op.drop_table(FLAG_ROOT_URL_TABLE_NAME)