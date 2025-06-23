from unittest.mock import MagicMock, call

import pytest
from sqlalchemy import select

from src.core.tasks.scheduled.operators.agency_sync.core import SyncAgenciesTaskOperator
from src.core.tasks.scheduled.operators.agency_sync.dtos.parameters import AgencySyncParameters
from src.db.models.instantiations.agency import Agency
from tests.automated.integration.tasks.agency_sync.data import AGENCIES_SYNC_RESPONSES
from tests.automated.integration.tasks.agency_sync.existence_checker import AgencyChecker
from tests.automated.integration.tasks.agency_sync.helpers import check_sync_concluded, patch_sync_agencies
from tests.helpers.assert_functions import assert_task_run_success


@pytest.mark.asyncio
async def test_agency_sync_happy_path(
    setup: SyncAgenciesTaskOperator
):
    operator = setup
    db_client = operator.adb_client

    with patch_sync_agencies(AGENCIES_SYNC_RESPONSES):
        run_info = await operator.run_task(1)
        assert_task_run_success(run_info)
        mock_func: MagicMock = operator.pdap_client.sync_agencies

        mock_func.assert_has_calls(
            [
                call(
                    AgencySyncParameters(
                    cutoff_date=None,
                    page=1
                    )
                ),
                call(
                    AgencySyncParameters(
                        cutoff_date=None,
                        page=2
                    )
                ),
                call(
                    AgencySyncParameters(
                        cutoff_date=None,
                        page=3
                    )
                )
            ]
        )

    await check_sync_concluded(db_client)

    # Check six entries in database
    agencies: list[Agency] = await db_client.scalars(select(Agency))
    assert len(agencies) == 6

    checker = AgencyChecker()
    for agency in agencies:
        checker.check(agency)