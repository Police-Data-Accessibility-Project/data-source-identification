"""Refine root table logic

Revision ID: 49fd9f295b8d
Revises: 9a56916ea7d8
Create Date: 2025-08-12 08:19:08.170835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '49fd9f295b8d'
down_revision: Union[str, None] = '9a56916ea7d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
