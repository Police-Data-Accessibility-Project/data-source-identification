"""Create url_probed_for_404 table and adjust logic for 404 probe

Revision ID: b5f079b6b8cb
Revises: 864107b703ae
Create Date: 2025-05-13 12:34:46.846656

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = 'b5f079b6b8cb'
down_revision: Union[str, None] = '864107b703ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'url_probed_for_404',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.Column('last_probed_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
    )

    # Add unique constraint to url_id column
    op.create_unique_constraint('uq_url_probed_for_404_url_id', 'url_probed_for_404', ['url_id'])
    # Add unique constraint for url_id column in url_checked_for_duplicate table
    op.create_unique_constraint('uq_url_checked_for_duplicates_url_id', 'url_checked_for_duplicate', ['url_id'])

    # Create new `404 Not Found` URL Status
    switch_enum_type(
        table_name='urls',
        column_name='outcome',
        enum_name='url_status',
        new_enum_values=[
            'pending',
            'submitted',
            'validated',
            'duplicate',
            'rejected',
            'error',
            '404 not found',
        ],
        check_constraints_to_drop=['url_name_not_null_when_validated']
    )

    # Add '404 Probe' to TaskType Enum
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
            '404 Probe'
        ]
    )

    op.execute(
    """
    ALTER TABLE urls
        ADD CONSTRAINT url_name_not_null_when_validated
            CHECK ((name IS NOT NULL) OR (outcome <> 'validated'::url_status))
           """
    )

    # Update existing error URLs with an error message of 404 Not Found
    op.execute("""
    UPDATE urls
    SET outcome = '404 not found'
    FROM url_error_info uei
    WHERE urls.id = uei.url_id
      AND urls.outcome = 'error'
      AND uei.error LIKE '%404%';
    """)


def downgrade() -> None:
    op.drop_table('url_probed_for_404')

    # Drop unique constraint for url_id column in url_checked_for_duplicate table
    op.drop_constraint('uq_url_checked_for_duplicates_url_id', 'url_checked_for_duplicate', type_='unique')

    # Drop `404 Not Found` URL Status
    op.execute("""
    UPDATE urls
    SET outcome = 'error'
    WHERE outcome = '404 not found';
    """)

    switch_enum_type(
        table_name='urls',
        column_name='outcome',
        enum_name='url_status',
        new_enum_values=[
            'pending',
            'submitted',
            'validated',
            'duplicate',
            'rejected',
            'error',
        ],
        check_constraints_to_drop=['url_name_not_null_when_validated']
    )

    op.execute(
    """
    ALTER TABLE urls
        ADD CONSTRAINT url_name_not_null_when_validated
            CHECK ((name IS NOT NULL) OR (outcome <> 'validated'::url_status))
           """
    )

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
        ]
    )
