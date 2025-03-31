"""Add data source ID column to URL table

Revision ID: 33a546c93441
Revises: 5ea47dacd0ef
Create Date: 2025-03-29 17:16:11.863064

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33a546c93441'
down_revision: Union[str, None] = '5ea47dacd0ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'url',
        sa.Column('data_source_id', sa.Integer(), nullable=True)
    )
    # Add unique constraint to data_source_id column
    op.create_unique_constraint('uq_data_source_id', 'url', ['data_source_id'])


def downgrade() -> None:
    op.drop_column('url', 'data_source_id')
