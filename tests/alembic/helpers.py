from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.helpers.alembic_runner import AlembicRunner


def get_enum_values(enum_name: str, session: Session) -> list[str]:
        return session.execute(text(f"SELECT enum_range(NULL::{enum_name})")).scalar()

def table_creation_check(
        alembic_runner: AlembicRunner,
        tables: list[str],
        end_revision: str,
        start_revision: str | None = None,
) -> None:
        if start_revision is not None:
                alembic_runner.upgrade(start_revision)
        for table_name in tables:
                assert table_name not in alembic_runner.inspector.get_table_names()
        alembic_runner.upgrade(end_revision)
        alembic_runner.reflect()
        for table_name in tables:
                assert table_name in alembic_runner.inspector.get_table_names()

def columns_in_table(
        alembic_runner: AlembicRunner,
        table_name: str,
        columns_to_check: list[str],
) -> bool:
        current_columns = [col["name"] for col in alembic_runner.inspector.get_columns(table_name)]
        return all(column in current_columns for column in columns_to_check)
