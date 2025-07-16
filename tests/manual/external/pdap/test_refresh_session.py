import pytest


@pytest.mark.asyncio
async def test_refresh_session(access_manager):
    old_access_token = await access_manager.access_token
    old_refresh_token = await access_manager.refresh_token
    await access_manager.refresh_access_token()
    new_access_token = await access_manager.access_token
    new_refresh_token = await access_manager.refresh_token
    assert old_access_token != new_access_token
    assert old_refresh_token != new_refresh_token
