"""Remove functional duplicates and setup constraints on fragments and nbsp

Revision ID: 8cd5aa7670ff
Revises: 571ada5b81b9
Create Date: 2025-08-09 20:31:58.865231

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8cd5aa7670ff'
down_revision: Union[str, None] = '571ada5b81b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

COMPRESSED_HTML_FOREIGN_KEY_NAME = 'fk_url_compressed_html_url_id'
COMPRESSED_HTML_TABLE_NAME = 'url_compressed_html'

URL_HTML_CONTENT_FOREIGN_KEY_NAME = 'url_html_content_url_id_fkey'
URL_HTML_CONTENT_TABLE_NAME = 'url_html_content'

URL_ERROR_INFO_TABLE_NAME = 'url_error_info'
URL_ERROR_INFO_FOREIGN_KEY_NAME = 'url_error_info_url_id_fkey'

URLS_NBSP_CHECK_CONSTRAINT_NAME = 'urls_nbsp_check'
URLS_FRAGMENTS_CHECK_CONSTRAINT_NAME = 'urls_fragments_check'

AUTOMATED_URL_AGENCY_SUGGESTION_TABLE_NAME = 'automated_url_agency_suggestions'
AUTOMATED_URL_AGENCY_SUGGESTION_FOREIGN_KEY_NAME = 'automated_url_agency_suggestions_url_id_fkey'


def upgrade() -> None:
    _add_cascade_foreign_key(URL_HTML_CONTENT_TABLE_NAME, foreign_key_name=URL_HTML_CONTENT_FOREIGN_KEY_NAME)
    _add_cascade_foreign_key(COMPRESSED_HTML_TABLE_NAME, foreign_key_name=COMPRESSED_HTML_FOREIGN_KEY_NAME)
    _add_cascade_foreign_key(URL_ERROR_INFO_TABLE_NAME, foreign_key_name=URL_ERROR_INFO_FOREIGN_KEY_NAME)
    _add_cascade_foreign_key(AUTOMATED_URL_AGENCY_SUGGESTION_TABLE_NAME, foreign_key_name=AUTOMATED_URL_AGENCY_SUGGESTION_FOREIGN_KEY_NAME)
    _remove_data_source_urls()
    _reset_data_sources_sync_state()
    _add_constraint_forbidding_nbsp()
    _delete_duplicate_urls()
    _remove_fragments_from_urls()
    _add_constraint_forbidding_fragments()


def downgrade() -> None:
    _remove_constraint_forbidding_fragments()
    _remove_constraint_forbidding_nbsp()
    _remove_cascade_foreign_key(URL_ERROR_INFO_TABLE_NAME, foreign_key_name=URL_ERROR_INFO_FOREIGN_KEY_NAME)
    _remove_cascade_foreign_key(COMPRESSED_HTML_TABLE_NAME, foreign_key_name=COMPRESSED_HTML_FOREIGN_KEY_NAME)
    _remove_cascade_foreign_key(URL_HTML_CONTENT_TABLE_NAME, foreign_key_name=URL_HTML_CONTENT_FOREIGN_KEY_NAME)
    _remove_cascade_foreign_key(AUTOMATED_URL_AGENCY_SUGGESTION_TABLE_NAME, foreign_key_name=AUTOMATED_URL_AGENCY_SUGGESTION_FOREIGN_KEY_NAME)

def _delete_duplicate_urls() -> None:
    op.execute('delete from urls where id in (2341,2343,2344,2347,2348,2349,2354,2359,2361,2501,2504,2505,2506,2507)')

def _create_url_foreign_key_with_cascade(table_name: str, foreign_key_name: str) -> None:
    op.create_foreign_key(
        foreign_key_name,
        table_name,
        referent_table='urls',
        local_cols=['url_id'], remote_cols=['id'],
        ondelete='CASCADE'
    )

def _create_url_foreign_key_without_cascade(table_name: str, foreign_key_name: str) -> None:
    op.create_foreign_key(
        foreign_key_name,
        table_name,
        referent_table='urls',
        local_cols=['url_id'], remote_cols=['id']
    )

def _remove_cascade_foreign_key(table_name: str, foreign_key_name: str) -> None:
    op.drop_constraint(foreign_key_name, table_name=table_name, type_='foreignkey')
    _create_url_foreign_key_without_cascade(table_name, foreign_key_name=foreign_key_name)

def _add_cascade_foreign_key(table_name: str, foreign_key_name: str) -> None:
    op.drop_constraint(foreign_key_name, table_name=table_name, type_='foreignkey')
    _create_url_foreign_key_with_cascade(table_name, foreign_key_name=foreign_key_name)

def _remove_data_source_urls() -> None:
    op.execute("""
    delete from urls
    where source = 'data_sources_app'
    """
    )

def _reset_data_sources_sync_state() -> None:
    op.execute("""
    delete from data_sources_sync_state
    """
   )

def _add_constraint_forbidding_nbsp() -> None:
    op.create_check_constraint(
        constraint_name=URLS_NBSP_CHECK_CONSTRAINT_NAME,
        table_name='urls',
        condition="url not like '% %'"
    )

def _add_constraint_forbidding_fragments() -> None:
    op.create_check_constraint(
        constraint_name=URLS_FRAGMENTS_CHECK_CONSTRAINT_NAME,
        table_name='urls',
        condition="url not like '%#%'"
    )

def _remove_constraint_forbidding_nbsp() -> None:
    op.drop_constraint(URLS_NBSP_CHECK_CONSTRAINT_NAME, table_name='urls', type_='check')

def _remove_constraint_forbidding_fragments() -> None:
    op.drop_constraint(URLS_FRAGMENTS_CHECK_CONSTRAINT_NAME, table_name='urls', type_='check')

def _remove_fragments_from_urls() -> None:
    # Remove fragments and everything after them
    op.execute("""
    update urls
    set url = substring(url from 1 for position('#' in url) - 1)
    where url like '%#%'
    """)