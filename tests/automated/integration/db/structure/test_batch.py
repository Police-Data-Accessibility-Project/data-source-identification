import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql

from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.helpers.connect import get_postgres_connection_string
from src.util.helper_functions import get_enum_values
from tests.automated.integration.db.structure.testers.models.column import ColumnTester
from tests.automated.integration.db.structure.testers.table import TableTester


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
