from sqlalchemy import create_engine

from src.db.models.templates import Base


def wipe_database(connection_string: str) -> None:
    """Wipe all data from database."""
    engine = create_engine(connection_string)
    with engine.connect() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())
        connection.commit()
