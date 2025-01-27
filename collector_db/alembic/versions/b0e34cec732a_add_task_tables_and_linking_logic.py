"""Add Task Tables and linking logic

Revision ID: b0e34cec732a
Revises: dae00e5aa8dd
Create Date: 2025-01-27 13:22:49.620212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b0e34cec732a'
down_revision: Union[str, None] = 'dae00e5aa8dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_type', sa.String(), nullable=False),
        sa.Column('task_id', sa.String(), nullable=False),
        sa.Column('task_status', sa.String(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_type', 'task_id', name='uq_task_type_task_id')
    )
    op.create_table('task_errors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('error', sa.Text(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('link_task_urls',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('task_id', 'url_id'),
        sa.UniqueConstraint('task_id', 'url_id', name='uq_task_id_url_id')
    )


def downgrade() -> None:
    op.drop_table('link_task_urls')
    op.drop_table('task_errors')
    op.drop_table('tasks')
