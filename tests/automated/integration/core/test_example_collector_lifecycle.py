import asyncio

import pytest

from db.DTOs.BatchInfo import BatchInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType, URLStatus
from core.AsyncCore import AsyncCore
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from core.SourceCollectorCore import SourceCollectorCore
from core.enums import BatchStatus
from tests.helpers.patch_functions import block_sleep


@pytest.mark.asyncio
async def test_example_collector_lifecycle(
    test_core: SourceCollectorCore,
    test_async_core: AsyncCore,
    monkeypatch
):
    """
    Test the flow of an example collector, which generates fake urls
    and saves them to the database
    """
    acore = test_async_core
    core = test_core
    db_client = core.db_client

    barrier = await block_sleep(monkeypatch)

    dto = ExampleInputDTO(
        example_field="example_value",
        sleep_time=1
    )
    csi: CollectorStartInfo = await acore.initiate_collector(
        collector_type=CollectorType.EXAMPLE,
        dto=dto,
        user_id=1
    )
    assert csi.message == "Started example collector."
    assert csi.batch_id is not None

    batch_id = csi.batch_id

    # Yield control so coroutine runs up to the barrier
    await asyncio.sleep(0)

    assert core.get_status(batch_id) == BatchStatus.IN_PROCESS
    # Release the barrier to resume execution
    barrier.release()
    await acore.collector_manager.logger.flush_all()
    assert core.get_status(batch_id) == BatchStatus.READY_TO_LABEL

    batch_info: BatchInfo = db_client.get_batch_by_id(batch_id)
    assert batch_info.strategy == "example"
    assert batch_info.status == BatchStatus.READY_TO_LABEL
    assert batch_info.total_url_count == 2
    assert batch_info.parameters == dto.model_dump()
    assert batch_info.compute_time > 0

    url_infos = db_client.get_urls_by_batch(batch_id)
    assert len(url_infos) == 2
    assert url_infos[0].outcome == URLStatus.PENDING
    assert url_infos[1].outcome == URLStatus.PENDING

    assert url_infos[0].url == "https://example.com"
    assert url_infos[1].url == "https://example.com/2"
