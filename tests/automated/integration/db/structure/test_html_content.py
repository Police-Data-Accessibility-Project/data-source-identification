import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from src.db.dtos.url.insert import InsertURLsInfo
from src.db.enums import URLHTMLContentType
from src.util.helper_functions import get_enum_values
from tests.automated.integration.db.structure.testers.models.column import ColumnTester
from tests.automated.integration.db.structure.testers.table import TableTester
from tests.helpers.data_creator.core import DBDataCreator


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
