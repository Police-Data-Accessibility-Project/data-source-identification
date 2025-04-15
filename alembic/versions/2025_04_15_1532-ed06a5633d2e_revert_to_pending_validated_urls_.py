"""Revert to pending validated URLs without name and add constraint

Revision ID: ed06a5633d2e
Revises: b363794fa4e9
Create Date: 2025-04-15 15:32:26.465488

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ed06a5633d2e'
down_revision: Union[str, None] = 'b363794fa4e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.execute(
        """
        UPDATE public.urls
        SET OUTCOME = 'pending'
        WHERE OUTCOME = 'validated' AND NAME IS NULL    
        """
    )

    op.create_check_constraint(
        'url_name_not_null_when_validated',
        'urls',
        "NAME IS NOT NULL OR OUTCOME != 'validated'"
    )


def downgrade() -> None:
    op.drop_constraint(
        'url_name_not_null_when_validated',
        'urls',
        type_='check'
    )
