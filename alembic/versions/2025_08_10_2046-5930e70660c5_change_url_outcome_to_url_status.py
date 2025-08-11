"""Change URL outcome to URL status

Revision ID: 5930e70660c5
Revises: 11ece61d7ac2
Create Date: 2025-08-10 20:46:58.576623

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5930e70660c5'
down_revision: Union[str, None] = '11ece61d7ac2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('urls', 'outcome', new_column_name='status')


def downgrade() -> None:
    op.alter_column('urls', 'status', new_column_name='outcome')
