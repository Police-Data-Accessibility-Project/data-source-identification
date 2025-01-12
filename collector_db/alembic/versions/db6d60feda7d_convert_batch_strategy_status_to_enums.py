"""Convert batch strategy, status to enums

Revision ID: db6d60feda7d
Revises: 86692fc1d862
Create Date: 2025-01-11 07:54:51.506803

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'db6d60feda7d'
down_revision: Union[str, None] = '86692fc1d862'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

batch_strategy_enum = postgresql.ENUM(
            'example',
            'ckan',
            "muckrock_county_search",
            "auto_googler",
            "muckrock_all_search",
            "muckrock_simple_search",
            "common_crawler",
            name='batch_strategy'
)

batch_status_enum = postgresql.ENUM(
            "complete",
            "error",
            "in-process",
            "aborted",
            name='batch_status')

def upgrade() -> None:
    batch_strategy_enum.create(op.get_bind())
    batch_status_enum.create(op.get_bind())

    op.alter_column(
        table_name='batches',
        column_name='strategy',
        existing_type=sa.String(),
        type_=batch_strategy_enum,
        postgresql_using='strategy::batch_strategy',
    )

    op.alter_column(
        table_name='batches',
        column_name='status',
        existing_type=sa.String(),
        type_=batch_status_enum,
        postgresql_using='status::batch_status',
    )


def downgrade() -> None:
    op.alter_column(
        table_name='batches',
        column_name='strategy',
        existing_type=batch_strategy_enum,
        type_=sa.String(),
    )

    op.alter_column(
        table_name='batches',
        column_name='status',
        existing_type=batch_status_enum,
        type_=sa.String(),
    )

    batch_status_enum.drop(op.get_bind(), checkfirst=True)
    batch_strategy_enum.drop(op.get_bind(), checkfirst=True)
