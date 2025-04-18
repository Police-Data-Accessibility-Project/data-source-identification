import asyncio

import pytest

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_manager.DTOs.ExampleInputDTO import ExampleInputDTO
from collector_manager.enums import CollectorType, URLStatus
from core.AsyncCore import AsyncCore
from core.DTOs.CollectorStartInfo import CollectorStartInfo
from core.SourceCollectorCore import SourceCollectorCore
from core.enums import BatchStatus

@pytest.mark.asyncio
async def test_example_collector_lifecycle(
    test_core: SourceCollectorCore,
    test_async_core: AsyncCore
):
    """
    Test the flow of an example collector, which generates fake urls
    and saves them to the database
    """
    acore = test_async_core
    core = test_core
    db_client = core.db_client
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

    assert core.get_status(batch_id) == BatchStatus.IN_PROCESS
    print("Sleeping for 1.5 seconds...")
    await asyncio.sleep(1.5)
    await acore.collector_manager.logger.flush_all()
    print("Done sleeping...")
    assert core.get_status(batch_id) == BatchStatus.READY_TO_LABEL

    batch_info: BatchInfo = db_client.get_batch_by_id(batch_id)
    assert batch_info.strategy == "example"
    assert batch_info.status == BatchStatus.READY_TO_LABEL
    assert batch_info.total_url_count == 2
    assert batch_info.parameters == dto.model_dump()
    assert batch_info.compute_time > 1

    url_infos = db_client.get_urls_by_batch(batch_id)
    assert len(url_infos) == 2
    assert url_infos[0].outcome == URLStatus.PENDING
    assert url_infos[1].outcome == URLStatus.PENDING

    assert url_infos[0].url == "https://example.com"
    assert url_infos[1].url == "https://example.com/2"

@pytest.mark.asyncio
async def test_example_collector_lifecycle_multiple_batches(
        test_core: SourceCollectorCore,
        test_async_core: AsyncCore
):
    """
    Test the flow of an example collector, which generates fake urls
    and saves them to the database
    """
    acore = test_async_core
    core = test_core
    csis: list[CollectorStartInfo] = []
    for i in range(3):
        dto = ExampleInputDTO(
            example_field="example_value",
            sleep_time=1
        )
        csi: CollectorStartInfo = await acore.initiate_collector(
            collector_type=CollectorType.EXAMPLE,
            dto=dto,
            user_id=1
        )
        csis.append(csi)


    for csi in csis:
        print("Batch ID:", csi.batch_id)
        assert core.get_status(csi.batch_id) == BatchStatus.IN_PROCESS

    await asyncio.sleep(3)

    for csi in csis:
        assert core.get_status(csi.batch_id) == BatchStatus.READY_TO_LABEL
