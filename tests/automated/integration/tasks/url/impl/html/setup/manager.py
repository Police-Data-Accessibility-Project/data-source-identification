import types

from src.core.enums import RecordType
from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from src.db.models.impl.url.web_metadata.insert import URLWebMetadataPydantic
from tests.automated.integration.tasks.url.impl.html.mocks.methods import mock_parse
from tests.automated.integration.tasks.url.impl.html.mocks.url_request_interface.core import MockURLRequestInterface
from tests.automated.integration.tasks.url.impl.html.setup.data import TEST_ENTRIES
from tests.automated.integration.tasks.url.impl.html.setup.models.record import TestURLHTMLTaskSetupRecord


class TestURLHTMLTaskSetupManager:

    def __init__(self, adb_client: AsyncDatabaseClient):
        self.adb_client = adb_client


    async def setup(self) -> list[TestURLHTMLTaskSetupRecord]:

        records = await self._setup_urls()
        await self.setup_web_metadata(records)
        return records

    async def _setup_urls(self) -> list[TestURLHTMLTaskSetupRecord]:
        url_insert_models: list[URLInsertModel] = []
        for entry in TEST_ENTRIES:
            url_insert_model = URLInsertModel(
                status=entry.url_info.status,
                url=entry.url_info.url,
                name=f"Test for {entry.url_info.url}",
                record_type=RecordType.RESOURCES,
                source=URLSource.COLLECTOR
            )
            url_insert_models.append(url_insert_model)
        url_ids = await self.adb_client.bulk_insert(url_insert_models, return_ids=True)

        records = []
        for url_id, entry in zip(url_ids, TEST_ENTRIES):
            record = TestURLHTMLTaskSetupRecord(
                url_id=url_id,
                entry=entry
            )
            records.append(record)
        return records

    async def setup_web_metadata(
        self,
        records: list[TestURLHTMLTaskSetupRecord]
    ) -> None:
        models = []
        for record in records:
            entry = record.entry
            web_metadata_info = entry.web_metadata_info
            if web_metadata_info is None:
                continue
            model = URLWebMetadataPydantic(
                url_id=record.url_id,
                accessed=web_metadata_info.accessed,
                status_code=web_metadata_info.response_code.value,
                content_type=web_metadata_info.content_type,
                error_message=web_metadata_info.error_message
            )
            models.append(model)
        await self.adb_client.bulk_insert(models)

async def setup_operator() -> URLHTMLTaskOperator:
    html_parser = HTMLResponseParser()
    html_parser.parse = types.MethodType(mock_parse, html_parser)
    operator = URLHTMLTaskOperator(
        adb_client=AsyncDatabaseClient(),
        url_request_interface=MockURLRequestInterface(),
        html_parser=html_parser
    )
    return operator
