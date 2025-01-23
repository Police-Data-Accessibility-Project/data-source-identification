from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.test_alembic.AlembicRunner import AlembicRunner


def get_enum_values(enum_name: str, session: Session) -> list[str]:
        return session.execute(text(f"SELECT enum_range(NULL::{enum_name})")).scalar()

def table_creation_check(
        alembic_runner: AlembicRunner,
        table_name: str,
        start_revision: str,
        end_revision: str
):
        alembic_runner.upgrade(start_revision)
        assert table_name not in alembic_runner.inspector.get_table_names()
        alembic_runner.upgrade(end_revision)
        alembic_runner.reflect()
        assert table_name in alembic_runner.inspector.get_table_names()