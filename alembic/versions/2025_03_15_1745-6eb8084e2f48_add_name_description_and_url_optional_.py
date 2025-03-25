"""Add name, description, and url optional data source metadata

Revision ID: 6eb8084e2f48
Revises: 69f7cc4f56d4
Create Date: 2025-03-15 17:45:46.619721

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '6eb8084e2f48'
down_revision: Union[str, None] = '69f7cc4f56d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add name and description columns to URL table
    op.add_column('urls', sa.Column('name', sa.String(), nullable=True))
    op.add_column('urls', sa.Column('description', sa.String(), nullable=True))

    # Create URL_optional_data_source_metadata
    op.create_table(
        'url_optional_data_source_metadata',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.Column('record_formats', sa.ARRAY(sa.String()), nullable=True),
        sa.Column('data_portal_type', sa.String(), nullable=True),
        sa.Column('supplying_entity', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Add 'Misc Metadata' to TaskType enum
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=['HTML', 'Relevancy', 'Record Type', 'Agency Identification', 'Misc Metadata']
    )


def downgrade() -> None:
    # Remove name and description columns from URL table
    op.drop_column('urls', 'name')
    op.drop_column('urls', 'description')

    # Drop URL_optional_data_source_metadata
    op.drop_table('url_optional_data_source_metadata')

    # Remove 'Misc Metadata' from TaskType enum
    switch_enum_type(
        table_name='tasks',
        column_name='task_type',
        enum_name='task_type',
        new_enum_values=['HTML', 'Relevancy', 'Record Type', 'Agency Identification']
    )
