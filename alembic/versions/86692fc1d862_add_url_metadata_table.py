"""Add url_metadata table

Revision ID: 86692fc1d862
Revises: a4750e7ff8e7
Create Date: 2025-01-10 15:36:58.123276

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '86692fc1d862'
down_revision: Union[str, None] = 'a4750e7ff8e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define enums as reusable variables
url_attribute = postgresql.ENUM('Record Type', 'Agency', 'Relevant', name='url_attribute')
validation_status_enum = postgresql.ENUM('Pending Label Studio', 'Validated', name='validation_status')
validation_source = postgresql.ENUM('Machine Learning', 'Label Studio', 'Manual', name='validation_source')

def upgrade():
    op.alter_column(
        table_name='urls',
        column_name='url_metadata',
        new_column_name='collector_metadata'
    )


    # Create the url_metadata table
    op.create_table(
        'url_metadata',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url_id', sa.Integer(), sa.ForeignKey('urls.id', ondelete='CASCADE'), nullable=False),
        sa.Column('attribute', url_attribute, nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('validation_status', validation_status_enum, nullable=False),
        sa.Column('validation_source', validation_source, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint('url_id', 'attribute', name='uq_url_id_attribute')  # Unique constraint
    )

def downgrade():

    op.alter_column(
        table_name='urls',
        column_name='collector_metadata',
        new_column_name='url_metadata'
    )

    # Drop the table first since it depends on the enums
    op.drop_table('url_metadata')

    # Drop Enums from the database
    validation_source.drop(op.get_bind(), checkfirst=True)
    validation_status_enum.drop(op.get_bind(), checkfirst=True)
    url_attribute.drop(op.get_bind(), checkfirst=True)