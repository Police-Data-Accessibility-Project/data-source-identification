"""empty message

Revision ID: d11f07224d1f
Revises: 
Create Date: 2025-01-07 17:41:35.512410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd11f07224d1f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('batches',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strategy', sa.String(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(), nullable=False),
        sa.Column('total_url_count', sa.Integer(), nullable=False),
        sa.Column('original_url_count', sa.Integer(), nullable=False),
        sa.Column('duplicate_url_count', sa.Integer(), nullable=False),
        sa.Column('date_generated', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.Column('strategy_success_rate', sa.Float(), nullable=True),
        sa.Column('metadata_success_rate', sa.Float(), nullable=True),
        sa.Column('agency_match_rate', sa.Float(), nullable=True),
        sa.Column('record_type_match_rate', sa.Float(), nullable=True),
        sa.Column('record_category_match_rate', sa.Float(), nullable=True),
        sa.Column('compute_time', sa.Float(), nullable=True),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('log', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('missing',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('place_id', sa.Integer(), nullable=False),
        sa.Column('record_type', sa.String(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=True),
        sa.Column('strategy_used', sa.Text(), nullable=False),
        sa.Column('date_searched', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('urls',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('url_metadata', sa.JSON(), nullable=True),
        sa.Column('outcome', sa.String(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('url')
    )
    op.create_table('duplicates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('batch_id', sa.Integer(), nullable=False),
        sa.Column('original_url_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['batch_id'], ['batches.id'], ),
        sa.ForeignKeyConstraint(['original_url_id'], ['urls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('duplicates')
    op.drop_table('urls')
    op.drop_table('missing')
    op.drop_table('logs')
    op.drop_table('batches')
    # ### end Alembic commands ###
