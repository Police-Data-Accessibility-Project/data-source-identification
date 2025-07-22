import pytest
from sqlalchemy import select

from src.core.tasks.scheduled.sync.agency.operator import SyncAgenciesTaskOperator
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.models.instantiations.agency.sqlalchemy import Agency
from src.db.models.instantiations.sync_state.agencies import AgenciesSyncState
from tests.automated.integration.tasks.scheduled.sync.agency.data import FIRST_CALL_RESPONSE, \
    THIRD_CALL_RESPONSE, SECOND_CALL_RESPONSE
from tests.automated.integration.tasks.scheduled.sync.agency.existence_checker import AgencyChecker
from tests.automated.integration.tasks.scheduled.sync.agency.helpers import patch_sync_agencies, check_sync_concluded


@pytest.mark.asyncio
async def test_agency_sync_interruption(
    setup: SyncAgenciesTaskOperator
):
    """
    Simulate interruption that causes it to stop on the second iteration.
    Should be able to resume where it left off.
    """
    operator = setup
    db_client = operator.adb_client



    with patch_sync_agencies(
        [FIRST_CALL_RESPONSE, ValueError("test error")]
    ):
        run_info = await operator.run_task(1)
        assert run_info.outcome == TaskOperatorOutcome.ERROR, run_info.message


    # Get current updated_ats from database for the 5 recently updated
    query = (
        select(
            Agency.updated_at
        ).order_by(
            Agency.updated_at.desc()
        ).limit(5)
    )
    updated_ats = await db_client.scalars(query)
    # Assert all have same value
    assert all(
        updated_at == updated_ats[0]
        for updated_at in updated_ats
    )
    initial_updated_at = updated_ats[0]

    # Check sync state results
    sync_state_results = await db_client.scalar(
        select(
            AgenciesSyncState
        )
    )
    assert sync_state_results.current_page == 2
    assert sync_state_results.last_full_sync_at is None
    assert sync_state_results.current_cutoff_date is None

    with patch_sync_agencies([SECOND_CALL_RESPONSE, THIRD_CALL_RESPONSE]):
        await operator.run_task(2)

    await check_sync_concluded(db_client)

    # Check six entries in database
    agencies: list[Agency] = await db_client.scalars((
        select(
            Agency
        ).order_by(
            Agency.updated_at
        )
    ))
    assert len(agencies) == 6

    checker = AgencyChecker()
    for agency in agencies:
        checker.check(agency)

    # Check newly updated agency has distinct updated_at value
    assert agencies[-1].updated_at != initial_updated_at
    # Check other agencies have same updated_at value
    assert all(
        agency.updated_at == initial_updated_at
        for agency in agencies[:-1]
    )