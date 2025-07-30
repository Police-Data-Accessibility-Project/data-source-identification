import sqlalchemy as sa

from tests.automated.integration.db.structure.testers.models.column import ColumnTester
from tests.automated.integration.db.structure.testers.table import TableTester
from tests.helpers.data_creator.core import DBDataCreator


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
