from datetime import datetime
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from src.core.tasks.scheduled.sync.agency.dtos.parameters import AgencySyncParameters
from src.core.tasks.scheduled.sync.agency.operator import SyncAgenciesTaskOperator
from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.db.models.instantiations.sync_state.agencies import AgenciesSyncState
from tests.automated.integration.tasks.scheduled.sync.agency.data import THIRD_CALL_RESPONSE
from tests.automated.integration.tasks.scheduled.sync.agency.existence_checker import AgencyChecker
from tests.automated.integration.tasks.scheduled.sync.agency.helpers import patch_sync_agencies, check_sync_concluded
from tests.helpers.asserts import assert_task_run_success


@pytest.mark.asyncio
async def test_agency_sync_task_no_new_results(
    setup: SyncAgenciesTaskOperator
):
    operator = setup
    db_client = operator.adb_client

    cutoff_date = datetime(2025, 5, 1).date()

    # Add cutoff date to database
    await db_client.add(
        AgenciesSyncState(
            current_cutoff_date=cutoff_date
        )
    )

    with patch_sync_agencies([THIRD_CALL_RESPONSE]):
        run_info = await operator.run_task(1)
        assert_task_run_success(run_info)
        mock_func: AsyncMock = operator.pdap_client.sync_agencies
        mock_func.assert_called_once_with(
            AgencySyncParameters(
                cutoff_date=cutoff_date,
                page=1
            )
        )

    await check_sync_concluded(db_client, check_updated_at=False)

    # Check two entries in database
    agencies: list[Agency] = await db_client.scalars(select(Agency))
    assert len(agencies) == 2

    # Neither should be updated with new values
    checker = AgencyChecker()
    for agency in agencies:
        with pytest.raises(AssertionError):
            checker.check(agency)