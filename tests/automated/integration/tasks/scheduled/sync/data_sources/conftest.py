import pytest_asyncio

from src.core.tasks.scheduled.sync.data_sources.operator import SyncDataSourcesTaskOperator
from src.external.pdap.client import PDAPClient
from tests.helpers.data_creator.core import DBDataCreator


@pytest_asyncio.fixture
async def test_operator(
    db_data_creator: DBDataCreator,
    mock_pdap_client: PDAPClient
) -> SyncDataSourcesTaskOperator:
    return SyncDataSourcesTaskOperator(
        adb_client=db_data_creator.adb_client,
        pdap_client=mock_pdap_client
    )
