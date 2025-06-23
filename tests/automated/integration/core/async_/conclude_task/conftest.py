import pytest_asyncio

from tests.automated.integration.core.async_.conclude_task.setup_info import TestAsyncCoreSetupInfo


@pytest_asyncio.fixture
async def setup(db_data_creator) -> TestAsyncCoreSetupInfo:
    ddc = db_data_creator

    batch_id = ddc.batch()
    url_ids = ddc.urls(batch_id=batch_id, url_count=3).url_ids
    task_id = await ddc.task()

    return TestAsyncCoreSetupInfo(
        batch_id=batch_id,
        task_id=task_id,
        url_ids=url_ids
    )