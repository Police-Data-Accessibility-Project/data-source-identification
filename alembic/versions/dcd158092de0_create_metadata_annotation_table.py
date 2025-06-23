"""Create Metadata Annotation table

Revision ID: dcd158092de0
Revises: 108dac321086
Create Date: 2025-01-16 12:27:11.434219

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'dcd158092de0'
down_revision: Union[str, None] = '108dac321086'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('metadata_annotations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('metadata_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.Text(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['metadata_id'], ['url_metadata.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'metadata_id', name='metadata_annotations_uq_user_id_metadata_id')
    )


def downgrade() -> None:
    op.drop_table('metadata_annotations')
