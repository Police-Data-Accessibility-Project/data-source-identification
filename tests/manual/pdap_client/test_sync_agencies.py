import pytest
import time

@pytest.mark.asyncio
async def test_sync_agencies(pdap_client_dev):

    start = time.perf_counter()
    response = await pdap_client_dev.sync_agencies(
        page=1,
        update_at=None
    )
    end = time.perf_counter()
    print(response)

    duration = end - start
    print(f"Duration: {duration:.4f} seconds")