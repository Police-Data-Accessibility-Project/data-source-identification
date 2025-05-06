"""Create URL Annotation Flags View

Revision ID: f25852e17c04
Revises: e55e16e0738f
Create Date: 2025-05-06 09:19:54.000410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f25852e17c04'
down_revision: Union[str, None] = 'e55e16e0738f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    CREATE VIEW url_annotation_flags AS
        SELECT
        u.id,
        u.outcome,
        CASE WHEN arts.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_auto_record_type_suggestion,
        CASE WHEN ars.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_auto_relevant_suggestion,
        CASE WHEN auas.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_auto_agency_suggestion,
        CASE WHEN urts.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_user_record_type_suggestion,
        CASE WHEN urs.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_user_relevant_suggestion,
        CASE WHEN uuas.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS has_user_agency_suggestion,
        CASE WHEN ruu.url_id IS NOT NULL THEN TRUE ELSE FALSE END AS was_reviewed
    FROM urls u
             LEFT JOIN public.auto_record_type_suggestions arts ON u.id = arts.url_id
             LEFT JOIN public.auto_relevant_suggestions ars ON u.id = ars.url_id
             LEFT JOIN public.automated_url_agency_suggestions auas ON u.id = auas.url_id
             LEFT JOIN public.user_record_type_suggestions urts ON u.id = urts.url_id
             LEFT JOIN public.user_relevant_suggestions urs ON u.id = urs.url_id
             LEFT JOIN public.user_url_agency_suggestions uuas ON u.id = uuas.url_id
             LEFT JOIN public.reviewing_user_url ruu ON u.id = ruu.url_id;

    """)


def downgrade() -> None:
    op.execute("DROP VIEW url_annotation_flags;")
