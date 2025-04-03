"""Remove relevant column from urls

Revision ID: 45271f8fe75d
Revises: e3fe6d099583
Create Date: 2025-04-02 21:14:29.778488

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45271f8fe75d'
down_revision: Union[str, None] = 'e3fe6d099583'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('urls', 'relevant')



def downgrade() -> None:
    op.add_column('urls', sa.Column('relevant', sa.BOOLEAN(), nullable=True))
