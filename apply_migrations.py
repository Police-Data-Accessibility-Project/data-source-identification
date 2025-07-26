from alembic import command
from alembic.config import Config

from src.db.helpers.connect import get_postgres_connection_string


def apply_migrations():
    print("Applying migrations...")
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url",
        get_postgres_connection_string()
    )
    command.upgrade(alembic_config, "head")
    print("Migrations applied.")

if __name__ == "__main__":
    apply_migrations()