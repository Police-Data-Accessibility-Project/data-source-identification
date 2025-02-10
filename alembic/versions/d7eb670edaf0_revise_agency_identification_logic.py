"""Revise agency identification logic

Revision ID: d7eb670edaf0
Revises: 8c44e02733ae
Create Date: 2025-02-07 13:10:41.181578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from collector_db.enums import PGEnum

# revision identifiers, used by Alembic.
revision: str = 'd7eb670edaf0'
down_revision: Union[str, None] = '8c44e02733ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

suggestion_type_enum = PGEnum(
    'Auto Suggestion',
    'Manual Suggestion',
    'Unknown',
    'New Agency',
    'Confirmed', name='url_agency_suggestion_type'
)

def upgrade():
    # Create agencies table
    op.create_table(
        "agencies",
        sa.Column("agency_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=True),
        sa.Column("county", sa.String(), nullable=True),
        sa.Column("locality", sa.String(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )

    # Create confirmed_url_agency table
    op.create_table(
        "confirmed_url_agency",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agency_id", sa.Integer(), sa.ForeignKey("agencies.agency_id"), nullable=False),
        sa.Column("url_id", sa.Integer(), sa.ForeignKey("urls.id"), nullable=False),
    )
    op.create_unique_constraint(
        "uq_confirmed_url_agency", "confirmed_url_agency", ["agency_id", "url_id"]
    )

    # Create automated_url_agency_suggestions table
    op.create_table(
        "automated_url_agency_suggestions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agency_id", sa.Integer(), sa.ForeignKey("agencies.agency_id"), nullable=True),
        sa.Column("url_id", sa.Integer(), sa.ForeignKey("urls.id"), nullable=False),
        sa.Column("is_unknown", sa.Boolean(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_automated_url_agency_suggestions", "automated_url_agency_suggestions", ["agency_id", "url_id"]
    )
    op.execute("""
    CREATE OR REPLACE FUNCTION enforce_no_agency_id_if_unknown()
    RETURNS TRIGGER AS $$
    BEGIN
        IF NEW.is_unknown = TRUE AND NEW.agency_id IS NOT NULL THEN
            RAISE EXCEPTION 'agency_id must be null when is_unknown is TRUE';
        END IF;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER enforce_no_agency_id_if_unknown
    BEFORE INSERT ON automated_url_agency_suggestions
    FOR EACH ROW
    EXECUTE FUNCTION enforce_no_agency_id_if_unknown();
    """)
    # Create user_url_agency_suggestions table
    op.create_table(
        "user_url_agency_suggestions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("agency_id", sa.Integer(), sa.ForeignKey("agencies.agency_id"), nullable=True),
        sa.Column("url_id", sa.Integer(), sa.ForeignKey("urls.id"), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("is_new", sa.Boolean(), nullable=True),
    )
    op.create_unique_constraint(
        "uq_user_url_agency_suggestions", "user_url_agency_suggestions", ["agency_id", "url_id", "user_id"]
    )
    op.execute("""
        CREATE OR REPLACE FUNCTION enforce_no_agency_id_if_new()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.is_new = TRUE AND NEW.agency_id IS NOT NULL THEN
                RAISE EXCEPTION 'agency_id must be null when is_new is TRUE';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER enforce_no_agency_id_if_new
        BEFORE INSERT ON user_url_agency_suggestions
        FOR EACH ROW
        EXECUTE FUNCTION enforce_no_agency_id_if_new();
    """)




    op.drop_table('url_agency_suggestions')
    suggestion_type_enum.drop(op.get_bind(), checkfirst=True)



def downgrade():
    # Drop constraints first
    op.drop_constraint("uq_confirmed_url_agency", "confirmed_url_agency", type_="unique")
    op.drop_constraint("uq_automated_url_agency_suggestions", "automated_url_agency_suggestions", type_="unique")
    op.drop_constraint("uq_user_url_agency_suggestions", "user_url_agency_suggestions", type_="unique")

    # Drop tables
    op.drop_table("user_url_agency_suggestions")
    op.drop_table("automated_url_agency_suggestions")
    op.drop_table("confirmed_url_agency")
    op.drop_table("agencies")

    op.create_table('url_agency_suggestions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('url_id', sa.Integer(), nullable=False),
        sa.Column('suggestion_type', suggestion_type_enum, nullable=False),
        sa.Column('agency_id', sa.Integer(), nullable=True),
        sa.Column('agency_name', sa.String(), nullable=True),
        sa.Column('state', sa.String(), nullable=True),
        sa.Column('county', sa.String(), nullable=True),
        sa.Column('locality', sa.String(), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['url_id'], ['urls.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.execute("""
    DROP TRIGGER IF EXISTS enforce_no_agency_id_if_unknown ON automated_url_agency_suggestions;
    """)
    op.execute("""
    DROP FUNCTION IF EXISTS enforce_no_agency_id_if_unknown; 
    """)
    op.execute("DROP TRIGGER enforce_no_agency_id_if_new ON user_url_agency_suggestions")
    op.execute("DROP FUNCTION enforce_no_agency_id_if_new()")

