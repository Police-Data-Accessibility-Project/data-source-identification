import pytest_asyncio

from src.core.tasks.scheduled.sync.data_sources.operator import SyncDataSourcesTaskOperator


@pytest_asyncio.fixture
async def setup(
    db_data_creator,
    mock_pdap_client
) -> SyncDataSourcesTaskOperator:
    raise NotImplementedError