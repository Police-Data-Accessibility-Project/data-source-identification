import pytest

from src.db.client.async_ import AsyncDatabaseClient
from src.db.dtos.url_error_info import URLErrorPydanticInfo
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_add_url_error_info(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_mapping.url_id for url_mapping in url_mappings]

    adb_client = AsyncDatabaseClient()
    task_id = await db_data_creator.task()

    error_infos = []
    for url_mapping in url_mappings:
        uei = URLErrorPydanticInfo(
            url_id=url_mapping.url_id,
            error="test error",
            task_id=task_id
        )

        error_infos.append(uei)

    await adb_client.add_url_error_infos(
        url_error_infos=error_infos
    )

    results = await adb_client.get_urls_with_errors()

    assert len(results) == 3

    for result in results:
        assert result.url_id in url_ids
        assert result.error == "test error"
