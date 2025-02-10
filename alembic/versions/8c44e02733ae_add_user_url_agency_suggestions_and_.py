"""Add user_url_agency_suggestions and trigger

Revision ID: 8c44e02733ae
Revises: 19bf57df581a
Create Date: 2025-02-05 10:33:46.002025

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8c44e02733ae'
down_revision: Union[str, None] = '19bf57df581a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        table_name='url_agency_suggestions',
        column=Column(
            name="user_id",
            type_=Integer,
            nullable=True
        )
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION user_url_agency_suggestions_value()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.suggestion_type = 'Manual Suggestion' and NEW.user_id IS NULL THEN
                RAISE EXCEPTION 'User ID must not be null when suggestion type is "Manual Suggestion"';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        
        CREATE TRIGGER enforce_url_agency_suggestions_manual_suggestion_user_id
        BEFORE INSERT ON url_agency_suggestions
        FOR EACH ROW
        EXECUTE FUNCTION user_url_agency_suggestions_value();

        """
    )


def downgrade() -> None:
    op.drop_column(
        table_name='url_agency_suggestions',
        column_name="user_id"
    )
    op.execute(
        """
        DROP TRIGGER IF EXISTS enforce_url_agency_suggestions_manual_suggestion_user_id;
        DROP FUNCTION IF EXISTS user_url_agency_suggestions_value();
        """
    )
