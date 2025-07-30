import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from src.collectors.enums import URLStatus
from src.util.helper_functions import get_enum_values
from tests.automated.integration.db.structure.testers.models.column import ColumnTester
from tests.automated.integration.db.structure.testers.table import TableTester
from tests.helpers.data_creator.core import DBDataCreator


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
