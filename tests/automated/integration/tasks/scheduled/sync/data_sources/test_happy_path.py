from unittest.mock import MagicMock, call

import pytest

from src.core.tasks.scheduled.sync.data_sources.dtos.parameters import DataSourcesSyncParameters
from src.core.tasks.scheduled.sync.data_sources.operator import SyncDataSourcesTaskOperator
from tests.automated.integration.tasks.scheduled.sync.data_sources.check import check_sync_concluded
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.core import patch_sync_data_sources
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.data import ENTRIES
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.enums import SyncResponseOrder
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.manager.core import \
    DataSourcesSyncTestSetupManager
from tests.helpers.asserts import assert_task_run_success


@pytest.mark.asyncio
async def test_data_sources_sync_happy_path(
    test_operator: SyncDataSourcesTaskOperator
):
    adb_client = test_operator.adb_client

    manager = DataSourcesSyncTestSetupManager(
        adb_client=adb_client,
        entries=ENTRIES
    )
    await manager.setup()

    with patch_sync_data_sources(
        await manager.get_data_sources_sync_responses([order for order in SyncResponseOrder])
    ):
        run_info = await test_operator.run_task(1)
        assert_task_run_success(run_info)
        mock_func: MagicMock = test_operator.pdap_client.sync_data_sources

        mock_func.assert_has_calls(
            [
                call(
                    DataSourcesSyncParameters(
                        cutoff_date=None,
                        page=1
                    )
                ),
                call(
                    DataSourcesSyncParameters(
                        cutoff_date=None,
                        page=2
                    )
                ),
                call(
                    DataSourcesSyncParameters(
                        cutoff_date=None,
                        page=3
                    )
                )
            ]
        )
        await check_sync_concluded(adb_client, check_updated_at=False)

        # TODO: Fill in additional components

    # Check results according to expectations.
    await manager.check_results()


