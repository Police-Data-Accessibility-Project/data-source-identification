from dataclasses import dataclass

from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, Inspector, MetaData, inspect
from sqlalchemy.orm import scoped_session


@dataclass
class AlembicRunner:
    connection: Connection
    alembic_config: Config
    inspector: Inspector
    metadata: MetaData
    session: scoped_session

    def reflect(self):
        self.metadata.clear()
        self.metadata.reflect(bind=self.connection)
        self.inspector = inspect(self.connection)

    def upgrade(self, revision: str):
        command.upgrade(self.alembic_config, revision)

    def downgrade(self, revision: str):
        print("Downgrading...")
        command.downgrade(self.alembic_config, revision)

    def stamp(self, revision: str):
        command.stamp(self.alembic_config, revision)

    def reset_schema(self):
        self.connection.exec_driver_sql("DROP SCHEMA public CASCADE;")
        self.connection.exec_driver_sql("CREATE SCHEMA public;")
        self.connection.commit()
