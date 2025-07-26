"""Setup for upload to huggingface task

Revision ID: 637de6eaa3ab
Revises: 59d2af1bab33
Create Date: 2025-07-26 08:30:37.940091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from src.util.alembic_helpers import id_column

# revision identifiers, used by Alembic.
revision: str = '637de6eaa3ab'
down_revision: Union[str, None] = '59d2af1bab33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TABLE_NAME = "huggingface_upload_state"


def upgrade() -> None:
    op.create_table(
        TABLE_NAME,
        id_column(),
        sa.Column(
            "last_upload_at",
            sa.DateTime(),
            nullable=False
        ),
    )


def downgrade() -> None:
    op.drop_table(TABLE_NAME)