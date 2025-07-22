import pytest
import time

from src.core.tasks.scheduled.sync.agency.dtos.parameters import AgencySyncParameters


@pytest.mark.asyncio
async def test_sync_agencies(pdap_client_dev):

    start = time.perf_counter()
    response = await pdap_client_dev.sync_agencies(
        params=AgencySyncParameters(
            page=1,
            cutoff_date=None
        )
    )
    end = time.perf_counter()
    print(response)

    duration = end - start
    print(f"Duration: {duration:.4f} seconds")