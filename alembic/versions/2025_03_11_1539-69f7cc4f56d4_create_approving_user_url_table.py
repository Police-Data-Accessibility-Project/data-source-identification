"""Create approving_user_url table

Revision ID: 69f7cc4f56d4
Revises: 33421c0590bb
Create Date: 2025-03-11 15:39:27.563567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69f7cc4f56d4'
down_revision: Union[str, None] = '33421c0590bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'approving_user_url',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id'], ),
        sa.UniqueConstraint('url_id', name='approving_user_url_uq_user_id_url_id')
    )


def downgrade() -> None:
    op.drop_table('approving_user_url')
