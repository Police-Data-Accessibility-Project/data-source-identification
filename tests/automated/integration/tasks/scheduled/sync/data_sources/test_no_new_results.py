from datetime import datetime
from unittest.mock import MagicMock

import pytest

from src.core.tasks.scheduled.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.core.tasks.scheduled.sync.data_sources.params import DataSourcesSyncParameters
from src.db.models.instantiations.state.sync.data_sources import DataSourcesSyncState
from tests.automated.integration.tasks.scheduled.sync.data_sources.check import check_sync_concluded
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.core import patch_sync_data_sources
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.data import ENTRIES
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.enums import SyncResponseOrder
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.manager.core import \
    DataSourcesSyncTestSetupManager
from tests.helpers.asserts import assert_task_run_success


@pytest.mark.asyncio
async def test_data_sources_sync_no_new_results(
    test_operator: SyncDataSourcesTaskOperator
):
    adb_client = test_operator.adb_client

    cutoff_date = datetime(2025, 5, 1).date()

    manager = DataSourcesSyncTestSetupManager(
        adb_client=adb_client,
        entries=ENTRIES
    )
    await manager.setup()

    first_response = await manager.get_data_sources_sync_responses(
        [SyncResponseOrder.THIRD]
    )

    # Add cutoff date to database
    await adb_client.add(
        DataSourcesSyncState(
            current_cutoff_date=cutoff_date
        )
    )

    with patch_sync_data_sources(first_response):
        run_info = await test_operator.run_task(1)
        assert_task_run_success(run_info)
        mock_func: MagicMock = test_operator.pdap_client.sync_data_sources

        mock_func.assert_called_once_with(
            DataSourcesSyncParameters(
                cutoff_date=cutoff_date,
                page=1
            )
        )
        await check_sync_concluded(adb_client, check_updated_at=False)

    # Check no syncs occurred
    for sync_response_order in [SyncResponseOrder.FIRST, SyncResponseOrder.SECOND]:
        with pytest.raises(AssertionError):
            await manager.check_via_sync_response_order(sync_response_order)
