import pytest
from sqlalchemy import select

from src.core.tasks.scheduled.impl.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.models.instantiations.state.sync.data_sources import DataSourcesSyncState
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.check import check_sync_concluded
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.core import patch_sync_data_sources
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.data import ENTRIES
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.enums import SyncResponseOrder
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.manager.core import \
    DataSourcesSyncTestSetupManager



@pytest.mark.asyncio
async def test_data_sources_sync_interruption(
    test_operator: SyncDataSourcesTaskOperator
):
    adb_client = test_operator.adb_client

    manager = DataSourcesSyncTestSetupManager(
        adb_client=adb_client,
        entries=ENTRIES
    )
    await manager.setup()

    first_response = await manager.get_data_sources_sync_responses(
        [SyncResponseOrder.FIRST]
    )

    with patch_sync_data_sources(
        side_effects=
            first_response +
            [ValueError("test error")]
    ):
        run_info = await test_operator.run_task(1)
        assert run_info.outcome == TaskOperatorOutcome.ERROR, run_info.message

    await manager.check_via_sync_response_order(SyncResponseOrder.FIRST)

    # Second response should not be processed
    with pytest.raises(AssertionError):
        await manager.check_via_sync_response_order(SyncResponseOrder.SECOND)

    # Check sync state results
    sync_state_results = await adb_client.scalar(
        select(
            DataSourcesSyncState
        )
    )
    assert sync_state_results.current_page == 2
    assert sync_state_results.last_full_sync_at is None
    assert sync_state_results.current_cutoff_date is None

    second_response = await manager.get_data_sources_sync_responses(
        [SyncResponseOrder.SECOND, SyncResponseOrder.THIRD]
    )
    with patch_sync_data_sources(second_response):
        await test_operator.run_task(2)

    await check_sync_concluded(adb_client)

    await manager.check_via_sync_response_order(SyncResponseOrder.SECOND)
    await manager.check_via_sync_response_order(SyncResponseOrder.THIRD)