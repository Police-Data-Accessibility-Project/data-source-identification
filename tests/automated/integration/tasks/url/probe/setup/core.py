from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.url.core.enums import URLSource
from src.db.models.instantiations.url.core.pydantic.insert import URLInsertModel
from src.db.models.instantiations.url.web_metadata.sqlalchemy import URLWebMetadata
from tests.automated.integration.tasks.url.probe.setup.data import SETUP_ENTRIES


async def create_urls_in_db(
    adb_client: AsyncDatabaseClient,
) -> None:
    record_types = [rt for rt in RecordType]
    urls = []
    for idx, entry in enumerate(SETUP_ENTRIES):
        url = URLInsertModel(
            url=entry.url,
            outcome=entry.url_status,
            name=f"test-url-probe-task-url-{idx}",
            record_type=record_types[idx],
            source=URLSource.COLLECTOR
        )
        urls.append(url)
    await adb_client.bulk_insert(urls)

