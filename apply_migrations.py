from alembic import command
from alembic.config import Config

from collector_db.helper_functions import get_postgres_connection_string

if __name__ == "__main__":
    print("Applying migrations...")
    alembic_config = Config("alembic.ini")
    alembic_config.set_main_option(
        "sqlalchemy.url",
        get_postgres_connection_string()
    )
    command.upgrade(alembic_config, "head")
    print("Migrations applied.")