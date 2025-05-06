"""Create url_data_sources table

Revision ID: 6f2007bbcce3
Revises: f25852e17c04
Create Date: 2025-05-06 11:15:24.485465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '6f2007bbcce3'
down_revision: Union[str, None] = 'f25852e17c04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create url_data_sources_table table
    op.create_table(
        'url_data_sources',
        sa.Column(
            'id',
            sa.Integer(),
            primary_key=True
        ),
        sa.Column(
            'url_id',
            sa.Integer(),
            sa.ForeignKey(
                'urls.id',
                ondelete='CASCADE'
            ),
            nullable=False
        ),
        sa.Column(
            'data_source_id',
            sa.Integer(),
            nullable=False
        ),
        sa.Column(
            'created_at',
            sa.TIMESTAMP(),
            nullable=False,
            server_default=sa.text('now()')
        ),
        sa.UniqueConstraint('url_id', name='uq_url_id'),
        sa.UniqueConstraint('data_source_id', name='uq_data_source_id')
    )

    # Migrate existing urls with a data source ID
    op.execute("""
        INSERT INTO url_data_sources 
        (url_id, data_source_id) 
        SELECT id, data_source_id 
        FROM urls 
        WHERE data_source_id IS NOT NULL
    """)

    # Drop existing data source ID column from urls table
    op.drop_column('urls', 'data_source_id')

    # Add trigger to ensure linked URL has status of submitted
    op.execute("""
        CREATE FUNCTION check_url_is_submitted() RETURNS trigger AS $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM urls WHERE id = NEW.url_id AND outcome != 'submitted'
            ) THEN
                RAISE EXCEPTION 'URL status is not submitted ';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER check_url_is_submitted
        BEFORE INSERT OR UPDATE ON url_data_sources
        FOR EACH ROW
        EXECUTE FUNCTION check_url_is_submitted();
    """)

    op.execute("""
        CREATE FUNCTION prevent_status_change_if_data_source_exists() RETURNS trigger AS $$
        BEGIN
            IF OLD.outcome = 'submitted' AND NEW.outcome IS DISTINCT FROM OLD.status THEN
                IF EXISTS (
                    SELECT 1 FROM url_data_sources WHERE url_id = OLD.id
                ) THEN
                    RAISE EXCEPTION 'Cannot change status from submitted: related child records exist.';
                END IF;
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER check_status_change
        BEFORE UPDATE ON urls
        FOR EACH ROW
        EXECUTE FUNCTION prevent_status_change_if_data_source_exists();
    """)


def downgrade() -> None:
    # Drop new trigger and function on URLS
    op.execute("""
        DROP TRIGGER IF EXISTS check_url_is_submitted ON urls;
        DROP FUNCTION IF EXISTS check_url_is_submitted;
        DROP TRIGGER IF EXISTS check_status_change ON urls;
        DROP FUNCTION IF EXISTS prevent_status_change_if_data_source_exists;
    """)

    op.drop_table('url_data_sources')

    op.add_column(
        'urls',
        sa.Column(
            'data_source_id',
            sa.Integer(),
            nullable=True
        )
    )


