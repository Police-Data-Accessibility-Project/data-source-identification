"""Convert url outcome to enum

Revision ID: e27c5f8409a3
Revises: db6d60feda7d
Create Date: 2025-01-12 08:11:21.160665

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e27c5f8409a3'
down_revision: Union[str, None] = 'db6d60feda7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

url_outcome_enum = postgresql.ENUM(
    'pending',
    'submitted',
    'human_labeling',
    'rejected',
    'duplicate',
    name='url_outcome'
)

def upgrade() -> None:
    url_outcome_enum.create(op.get_bind())

    op.alter_column(
        table_name='urls',
        column_name='outcome',
        existing_type=sa.String(),
        type_=url_outcome_enum,
        postgresql_using='outcome::url_outcome',
        nullable=False
    )



def downgrade() -> None:
    op.alter_column(
        table_name='urls',
        column_name='outcome',
        existing_type=url_outcome_enum,
        type_=sa.String(),
        nullable=True
    )

    url_outcome_enum.drop(op.get_bind(), checkfirst=True)
