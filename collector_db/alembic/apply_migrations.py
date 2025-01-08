from alembic import command
from alembic.config import Config

if __name__ == "__main__":
    print("Applying migrations...")
    alembic_config = Config("alembic.ini")
    command.upgrade(alembic_config, "head")
    print("Migrations applied.")