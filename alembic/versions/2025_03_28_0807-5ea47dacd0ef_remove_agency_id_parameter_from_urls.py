"""Remove agency_id parameter from URLs

Revision ID: 5ea47dacd0ef
Revises: 6eb8084e2f48
Create Date: 2025-03-28 08:07:24.442764

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ea47dacd0ef'
down_revision: Union[str, None] = '6eb8084e2f48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Remove agency ID column from URLs
    op.drop_column(
        'urls',
        'agency_id'
    )

    op.create_table(
        'confirmed_url_agency',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('url_id', sa.Integer(), sa.ForeignKey('urls.id', ondelete='CASCADE'), nullable=False),
        sa.Column(
            'agency_id',
            sa.Integer(),
            sa.ForeignKey('agencies.agency_id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.TIMESTAMP(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.UniqueConstraint(
            'url_id', 'agency_id',
            name="uq_confirmed_url_agency"
        )
    )


def downgrade() -> None:
    op.add_column(
        'urls',
        sa.Column(
            'agency_id',
            sa.Integer(),
            sa.ForeignKey('agencies.agency_id', ondelete='NO ACTION'),
            nullable=True
        )
    )

    op.drop_table('confirmed_url_agency')