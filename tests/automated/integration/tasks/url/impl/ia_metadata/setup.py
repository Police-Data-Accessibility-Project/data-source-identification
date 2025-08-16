from unittest.mock import AsyncMock

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.pydantic.insert import URLInsertModel
from tests.automated.integration.tasks.url.impl.ia_metadata.constants import TEST_URL_1, TEST_URL_2


async def add_urls(dbc: AsyncDatabaseClient) -> list[int]:
    """Adds two URLs to the database."""
    insert_models: list[URLInsertModel] = [
        URLInsertModel(
            url=TEST_URL_1,
            source=URLSource.COLLECTOR
        ),
        URLInsertModel(
            url=TEST_URL_2,
            source=URLSource.COLLECTOR
        )
    ]
    return await dbc.bulk_insert(insert_models, return_ids=True)

async def add_mock_response(mock_ia_client: AsyncMock, results: list) -> None:
    """
    Modifies:
        mock_ia_client.search_for_url_snapshot
    """
    mock_ia_client.search_for_url_snapshot.side_effect = results