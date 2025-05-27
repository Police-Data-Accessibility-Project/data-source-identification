"""Add manual strategy to Batch strategy enum

Revision ID: 028565b77b9e
Revises: e285e6e7cf71
Create Date: 2025-05-03 09:56:51.134406

"""
from typing import Sequence, Union

from alembic import op

from src.util.alembic_helpers import switch_enum_type

# revision identifiers, used by Alembic.
revision: str = '028565b77b9e'
down_revision: Union[str, None] = 'e285e6e7cf71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    switch_enum_type(
        table_name="batches",
        column_name="strategy",
        enum_name="batch_strategy",
        new_enum_values=[
            "example",
            "ckan",
            "muckrock_county_search",
            "auto_googler",
            "muckrock_all_search",
            "muckrock_simple_search",
            "common_crawler",
            "manual"
        ],
    )


def downgrade() -> None:
    # Delete all batches with manual strategy
    op.execute("""
    DELETE FROM BATCHES
        WHERE STRATEGY = 'manual'
    """)

    switch_enum_type(
        table_name="batches",
        column_name="strategy",
        enum_name="batch_strategy",
        new_enum_values=[
            "example",
            "ckan",
            "muckrock_county_search",
            "auto_googler",
            "muckrock_all_search",
            "muckrock_simple_search",
            "common_crawler"
        ],
    )
