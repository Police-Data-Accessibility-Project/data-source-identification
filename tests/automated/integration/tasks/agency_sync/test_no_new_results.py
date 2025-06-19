from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy import update

from src.core.tasks.operators.agency_sync.core import SyncAgenciesTaskOperator
from src.core.tasks.operators.agency_sync.dtos.parameters import AgencySyncParameters
from src.db.models.instantiations.agency import Agency
from src.db.models.instantiations.sync_state_agencies import AgenciesSyncState
from tests.automated.integration.tasks.agency_sync.data import THIRD_CALL_RESPONSE
from tests.automated.integration.tasks.agency_sync.existence_checker import AgencyChecker
from tests.automated.integration.tasks.agency_sync.helpers import patch_sync_agencies, check_sync_concluded
from tests.helpers.assert_functions import assert_task_run_success


@pytest.mark.asyncio
async def test_agency_sync_task_no_new_results(
    setup: SyncAgenciesTaskOperator
):
    operator = setup
    db_client = operator.adb_client

    cutoff_date = datetime(2025, 5, 1).date()

    # Add cutoff date to database
    await db_client.execute(
        update(AgenciesSyncState).values(
            current_cutoff_date=cutoff_date
        )
    )

    with patch_sync_agencies([THIRD_CALL_RESPONSE]):
        run_info = await operator.run_task(1)
        assert_task_run_success(run_info)
        mock_func: MagicMock = operator.pdap_client.sync_agencies
        mock_func.assert_called_once_with(
            params=AgencySyncParameters(
                cutoff_date=cutoff_date,
                page=1
            )
        )


    assert not await operator.meets_task_prerequisites()

    await check_sync_concluded(db_client)

    # Check two entries in database
    agencies: list[Agency] = await db_client.scalars(Agency)
    assert len(agencies) == 2

    # Neither should be updated with new values
    checker = AgencyChecker()
    for agency in agencies:
        with pytest.raises(AssertionError):
            checker.check(agency)