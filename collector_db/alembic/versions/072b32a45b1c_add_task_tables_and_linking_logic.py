"""Add Task Tables and linking logic

Revision ID: 072b32a45b1c
Revises: dae00e5aa8dd
Create Date: 2025-01-27 15:48:02.713484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from collector_db.enums import PGEnum

# revision identifiers, used by Alembic.
revision: str = '072b32a45b1c'
down_revision: Union[str, None] = 'dae00e5aa8dd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

task_type = PGEnum(
    'HTML',
    'Relevancy',
    'Record Type',
    name='task_type',
)


def upgrade() -> None:
    op.create_table('tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_type', task_type, nullable=False),
        sa.Column(
            'task_status',
            PGEnum(
                'complete', 'error', 'in-process', 'aborted',
                name='batch_status',
                create_type=False
            ),
            nullable=False
        ),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
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
    # Change to URL Error Info requires deleting prior data
    op.execute("DELETE FROM url_error_info;")

    op.add_column('url_error_info', sa.Column('task_id', sa.Integer(), nullable=False))
    op.create_unique_constraint('uq_url_id_error', 'url_error_info', ['url_id', 'task_id'])
    op.create_foreign_key("fk_url_error_info_task", 'url_error_info', 'tasks', ['task_id'], ['id'])


def downgrade() -> None:

    op.drop_constraint("fk_url_error_info_task", 'url_error_info', type_='foreignkey')
    op.drop_constraint('uq_url_id_error', 'url_error_info', type_='unique')
    op.drop_column('url_error_info', 'task_id')
    op.drop_table('link_task_urls')
    op.drop_table('task_errors')
    op.drop_table('tasks')

    task_type.drop(op.get_bind(), checkfirst=True)
