from typing import Optional, Any

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import DataError

from src.db.helpers.connect import get_postgres_connection_string
from src.db.models.templates_.base import Base
from tests.automated.integration.db.structure.testers.models.column import ColumnTester
from tests.automated.integration.db.structure.types import ConstraintTester, SATypes


class TableTester:

    def __init__(
            self,
            columns: list[ColumnTester],
            table_name: str,
            engine: Optional[sa.Engine] = None,
            constraints: Optional[list[ConstraintTester]] = None,
    ):
        if engine is None:
            engine = create_engine(get_postgres_connection_string(is_async=True))
        self.columns = columns
        self.table_name = table_name
        self.constraints = constraints
        self.engine = engine

    def run_tests(self):
        pass

    def setup_row_dict(self, override: Optional[dict[str, Any]] = None):
        d = {}
        for column in self.columns:
            # For row dicts, the first value is the default
            d[column.column_name] = column.allowed_values[0]
        if override is not None:
            d.update(override)
        return d

    def run_column_test(self, column: ColumnTester):
        if len(column.allowed_values) == 1:
            return # It will be tested elsewhere
        for value in column.allowed_values:
            print(f"Testing column {column.column_name} with value {value}")
            row_dict = self.setup_row_dict(override={column.column_name: value})
            table = self.get_table_model()
            with self.engine.begin() as conn:
                # Delete existing rows
                conn.execute(table.delete())
                conn.commit()
            with self.engine.begin() as conn:
                conn.execute(table.insert(), row_dict)
                conn.commit()
                conn.close()
        self.test_invalid_values(column)

    def generate_invalid_value(self, type_: SATypes):
        match type_:
            case sa.Integer:
                return "not an integer"
            case sa.String:
                return -1
            case postgresql.ENUM:
                return "not an enum value"
            case sa.TIMESTAMP:
                return "not a timestamp"

    def test_invalid_values(self, column: ColumnTester):
        invalid_value = self.generate_invalid_value(type_=column.type_)
        row_dict = self.setup_row_dict(override={column.column_name: invalid_value})
        table = self.get_table_model()
        print(f"Testing column '{column.column_name}' with invalid value {invalid_value}")
        with pytest.raises(DataError):
            with self.engine.begin() as conn:
                conn.execute(table.delete())
                conn.commit()
            with self.engine.begin() as conn:
                conn.execute(table.insert(), row_dict)
                conn.commit()
                conn.close()


    def get_table_model(self) -> sa.Table:
        """
        Retrieve table model from metadata
        """
        return sa.Table(self.table_name, Base.metadata, autoload_with=self.engine)


    def run_column_tests(self):
        for column in self.columns:
            self.run_column_test(column)
