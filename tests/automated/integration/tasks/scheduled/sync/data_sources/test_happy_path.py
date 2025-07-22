from unittest.mock import MagicMock, call

import pytest

from src.core.tasks.scheduled.sync.data_sources.dtos.parameters import DataSourcesSyncParameters
from src.db.models.instantiations.url.core.sqlalchemy import URL
from tests.automated.integration.tasks.scheduled.sync.agency.helpers import check_sync_concluded
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.core import patch_sync_data_sources
from tests.automated.integration.tasks.scheduled.sync.data_sources.setup.info import TestDataSourcesSyncSetupInfo
from tests.helpers.asserts import assert_task_run_success


@pytest.mark.asyncio
async def test_data_sources_sync_happy_path(
    setup: TestDataSourcesSyncSetupInfo
):
    operator = setup.operator
    adb_client = operator.adb_client

    with patch_sync_data_sources([setup.first_call_response, setup.second_call_response, setup.third_call_response]):
        run_info = await operator.run_task(1)
        assert_task_run_success(run_info)
        mock_func: MagicMock = operator.pdap_client.sync_data_sources

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

        # Check six URLs in database
        urls: list[URL] = await adb_client.get_all(URL)
        assert len(urls) == 6

        checker = URLChecker()
        for url in urls:
            checker.check_url(url)
