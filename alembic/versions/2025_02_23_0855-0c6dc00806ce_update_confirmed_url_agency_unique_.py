"""Update confirmed_url_agency unique constraint to be only url_id

Revision ID: 0c6dc00806ce
Revises: 76f902fe18cd
Create Date: 2025-02-23 08:55:07.046607

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0c6dc00806ce'
down_revision: Union[str, None] = '76f902fe18cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint(
        constraint_name="uq_confirmed_url_agency",
        table_name="confirmed_url_agency",
    )

    op.create_unique_constraint(
        constraint_name="uq_confirmed_url_agency",
        table_name="confirmed_url_agency",
        columns=["url_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        constraint_name="uq_confirmed_url_agency",
        table_name="confirmed_url_agency",
    )

    op.create_unique_constraint(
        constraint_name="uq_confirmed_url_agency",
        table_name="confirmed_url_agency",
        columns=["url_id", "agency_id"],
    )