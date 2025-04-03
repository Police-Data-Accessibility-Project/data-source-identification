"""Rename approving_user_url to reviewing_user_url

Revision ID: e3fe6d099583
Revises: 4c70177eba78
Create Date: 2025-04-02 20:51:10.738159

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e3fe6d099583'
down_revision: Union[str, None] = '4c70177eba78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('approving_user_url', 'reviewing_user_url')


def downgrade() -> None:
    op.rename_table('reviewing_user_url', 'approving_user_url')
