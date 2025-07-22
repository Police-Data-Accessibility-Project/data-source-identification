from contextlib import contextmanager
from datetime import timedelta
from unittest.mock import patch

from sqlalchemy import select, func, TIMESTAMP, cast

from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.agency import Agency
from src.db.models.instantiations.sync_state_agencies import AgenciesSyncState
from src.external.pdap.client import PDAPClient
from tests.automated.integration.tasks.scheduled.agency_sync.data import PREEXISTING_AGENCIES


async def check_sync_concluded(
    db_client: AsyncDatabaseClient,
    check_updated_at: bool = True
):
    current_db_datetime = await db_client.scalar(
        select(
            cast(func.now(), TIMESTAMP)
        )
    )

    sync_state_results = await db_client.scalar(
        select(
            AgenciesSyncState
        )
    )
    assert sync_state_results.current_page is None
    assert sync_state_results.last_full_sync_at > current_db_datetime - timedelta(minutes=5)
    assert sync_state_results.current_cutoff_date > (current_db_datetime - timedelta(days=2)).date()

    if not check_updated_at:
        return

    updated_ats = await db_client.scalars(
        select(
            Agency.updated_at
        )
    )
    assert all(
        updated_at > current_db_datetime - timedelta(minutes=5)
        for updated_at in updated_ats
    )


async def update_existing_agencies_updated_at(db_data_creator):
    update_mappings = []
    for preexisting_agency in PREEXISTING_AGENCIES:
        update_mapping = {
            "agency_id": preexisting_agency.agency_id,
            "updated_at": preexisting_agency.updated_at
        }
        update_mappings.append(update_mapping)
    await db_data_creator.adb_client.bulk_update(
        model=Agency,
        mappings=update_mappings,
    )


async def add_existing_agencies(db_data_creator):
    agencies_to_add = []
    for preexisting_agency in PREEXISTING_AGENCIES:
        agency_to_add = Agency(
            name=preexisting_agency.display_name,
            state=preexisting_agency.state_name,
            county=preexisting_agency.county_name,
            locality=preexisting_agency.locality_name,
            agency_id=preexisting_agency.agency_id,
        )
        agencies_to_add.append(agency_to_add)
    await db_data_creator.adb_client.add_all(agencies_to_add)

@contextmanager
def patch_sync_agencies(side_effects: list):
    with patch.object(
        PDAPClient,
        "sync_agencies",
        side_effect=side_effects
    ):
        yield