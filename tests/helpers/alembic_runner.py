from dataclasses import dataclass

from alembic import command
from alembic.config import Config
from sqlalchemy import Connection, Inspector, MetaData, inspect, text
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
        self.reflect()

    def downgrade(self, revision: str):
        command.downgrade(self.alembic_config, revision)

    def stamp(self, revision: str):
        command.stamp(self.alembic_config, revision)

    def reset_schema(self):
        self.connection.exec_driver_sql("DROP SCHEMA public CASCADE;")
        self.connection.exec_driver_sql("CREATE SCHEMA public;")
        self.connection.commit()

    def table_exists(self, table_name: str) -> bool:
        return table_name in self.inspector.get_table_names()

    def tables_exist(self, table_names: list[str]) -> bool:
        return all(table_name in self.inspector.get_table_names() for table_name in table_names)

    def execute(self, sql: str):
        result = self.connection.execute(text(sql))
        if result.cursor is not None:
            results = result.fetchall()
            self.connection.commit()
            return results
