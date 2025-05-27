import pytest
from aiohttp import ClientSession

from pdap_access_manager import AccessManager
from src.util import get_from_env


@pytest.mark.asyncio
async def test_refresh_session():
    async with ClientSession() as session:
        access_manager = AccessManager(
            email=get_from_env("PDAP_PROD_EMAIL"),
            password=get_from_env("PDAP_PROD_PASSWORD"),
            api_key=get_from_env("PDAP_API_KEY", allow_none=True),
            session=session
        )
        old_access_token = await access_manager.access_token
        old_refresh_token = await access_manager.refresh_token
        await access_manager.refresh_access_token()
        new_access_token = await access_manager.access_token
        new_refresh_token = await access_manager.refresh_token
        assert old_access_token != new_access_token
        assert old_refresh_token != new_refresh_token
