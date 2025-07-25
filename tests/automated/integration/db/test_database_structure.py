"""
Database Structure tests, in this instance
Test the integrity of the database schema and that it behaves as expected.

This includes testing that:
* Enum columns allow only allowed values (and throw errors on others)
* Column types are correct
"""

from dataclasses import dataclass
from typing import TypeAlias, Optional, Any

import pytest
import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import DataError

from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.db.dtos.url.insert import InsertURLsInfo
from src.db.enums import URLHTMLContentType
from src.db.helpers import get_postgres_connection_string
from src.db.models.instantiations.agency import Agency
from src.collectors.enums import CollectorType, URLStatus
from src.core.enums import BatchStatus, SuggestionType
from src.db.models.templates import Base
from src.util.helper_functions import get_enum_values
from tests.helpers.db_data_creator import DBDataCreator

SATypes: TypeAlias = sa.Integer or sa.String or postgresql.ENUM or sa.TIMESTAMP or sa.Text

@dataclass
class ColumnTester:
    column_name: str
    type_: SATypes
    allowed_values: list

@dataclass
class UniqueConstraintTester:
    columns: list[str]

@dataclass
class ForeignKeyTester:
    column_name: str
    valid_id: int
    invalid_id: int

ConstraintTester: TypeAlias = UniqueConstraintTester or ForeignKeyTester

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


def test_batch(wiped_database):
    engine = create_engine(get_postgres_connection_string())
    table_tester = TableTester(
        table_name="batches",
        columns=[
            ColumnTester(
                column_name="strategy",
                type_=postgresql.ENUM,
                allowed_values=get_enum_values(CollectorType),
            ),
            ColumnTester(
                column_name="user_id",
                type_=sa.Integer,
                allowed_values=[1],
            ),
            ColumnTester(
                column_name="status",
                type_=postgresql.ENUM,
                allowed_values=get_enum_values(BatchStatus),
            ),
            ColumnTester(
                column_name="total_url_count",
                type_=sa.Integer,
                allowed_values=[1],
            ),
            ColumnTester(
                column_name="original_url_count",
                type_=sa.Integer,
                allowed_values=[1],
            ),
            ColumnTester(
                column_name="duplicate_url_count",
                type_=sa.Integer,
                allowed_values=[1],
            ),
            ColumnTester(
                column_name="strategy_success_rate",
                type_=sa.Float,
                allowed_values=[1.0],
            ),
            ColumnTester(
                column_name="metadata_success_rate",
                type_=sa.Float,
                allowed_values=[1.0],
            ),
            ColumnTester(
                column_name="agency_match_rate",
                type_=sa.Float,
                allowed_values=[1.0],
            ),
            ColumnTester(
                column_name="record_type_match_rate",
                type_=sa.Float,
                allowed_values=[1.0],
            ),
            ColumnTester(
                column_name="record_category_match_rate",
                type_=sa.Float,
                allowed_values=[1.0],
            ),
            ColumnTester(
                column_name="compute_time",
                type_=sa.Float,
                allowed_values=[1.0],
            ),
            ColumnTester(
                column_name="parameters",
                type_=sa.JSON,
                allowed_values=[{}]
            )

        ],
        engine=engine
    )

    table_tester.run_column_tests()

def test_url(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    table_tester = TableTester(
        table_name="urls",
        columns=[
            ColumnTester(
                column_name="batch_id",
                type_=sa.Integer,
                allowed_values=[batch_id],
            ),
            ColumnTester(
                column_name="url",
                type_=sa.String,
                allowed_values=["https://example.com"],
            ),
            ColumnTester(
                column_name="collector_metadata",
                type_=sa.JSON,
                allowed_values=[{}]
            ),
            ColumnTester(
                column_name="outcome",
                type_=postgresql.ENUM,
                allowed_values=get_enum_values(URLStatus)
            ),
            ColumnTester(
                column_name="name",
                type_=sa.String,
                allowed_values=['test'],
            )
        ],
        engine=db_data_creator.db_client.engine
    )

    table_tester.run_column_tests()

def test_html_content(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    iui: InsertURLsInfo = db_data_creator.urls(batch_id=batch_id, url_count=1)

    table_tester = TableTester(
        table_name="url_html_content",
        columns=[
            ColumnTester(
                column_name="url_id",
                type_=sa.Integer,
                allowed_values=[iui.url_mappings[0].url_id]
            ),
            ColumnTester(
                column_name="content_type",
                type_=postgresql.ENUM,
                allowed_values=get_enum_values(URLHTMLContentType)
            ),
            ColumnTester(
                column_name="content",
                type_=sa.Text,
                allowed_values=["Text"]
            )
        ],
        engine=db_data_creator.db_client.engine
    )

    table_tester.run_column_tests()

def test_root_url(db_data_creator: DBDataCreator):

    table_tester = TableTester(
        table_name="root_urls",
        columns=[
            ColumnTester(
                column_name="url",
                type_=sa.String,
                allowed_values=["https://example.com"]
            ),
            ColumnTester(
                column_name="page_title",
                type_=sa.String,
                allowed_values=["Text"]
            ),
            ColumnTester(
                column_name="page_description",
                type_=sa.String,
                allowed_values=["Text"]
            )
        ],
        engine=db_data_creator.db_client.engine
    )

    table_tester.run_column_tests()


@pytest.mark.asyncio
async def test_upsert_new_agencies(db_data_creator: DBDataCreator):
    """
    Check that if the agency doesn't exist, it is added
    But if the agency does exist, it is updated with new information
    """

    suggestions = []
    for i in range(3):
        suggestion = URLAgencySuggestionInfo(
            url_id=1,
            suggestion_type=SuggestionType.AUTO_SUGGESTION,
            pdap_agency_id=i,
            agency_name=f"Test Agency {i}",
            state=f"Test State {i}",
            county=f"Test County {i}",
            locality=f"Test Locality {i}",
            user_id=1
        )
        suggestions.append(suggestion)

    adb_client = db_data_creator.adb_client
    await adb_client.upsert_new_agencies(suggestions)

    update_suggestion = URLAgencySuggestionInfo(
        url_id=1,
        suggestion_type=SuggestionType.AUTO_SUGGESTION,
        pdap_agency_id=0,
        agency_name="Updated Test Agency",
        state="Updated Test State",
        county="Updated Test County",
        locality="Updated Test Locality",
        user_id=1
    )

    await adb_client.upsert_new_agencies([update_suggestion])

    rows = await adb_client.get_all(Agency)

    assert len(rows) == 3

    d = {}
    for row in rows:
        d[row.agency_id] = row.name

    assert d[0] == "Updated Test Agency"
    assert d[1] == "Test Agency 1"
    assert d[2] == "Test Agency 2"
