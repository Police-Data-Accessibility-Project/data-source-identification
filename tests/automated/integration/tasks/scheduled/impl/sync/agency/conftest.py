import pytest_asyncio

from src.core.tasks.scheduled.impl.sync.agency.operator import SyncAgenciesTaskOperator
from tests.automated.integration.tasks.scheduled.impl.sync.agency.helpers import update_existing_agencies_updated_at, \
    add_existing_agencies

@pytest_asyncio.fixture
async def setup(
    db_data_creator,
    mock_pdap_client
) -> SyncAgenciesTaskOperator:
    await add_existing_agencies(db_data_creator)
    await update_existing_agencies_updated_at(db_data_creator)

    return SyncAgenciesTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )


