import pytest
from aiohttp import ClientSession

from pdap_access_manager import AccessManager
from src.pdap_api.client import PDAPClient
from src.util import get_from_env


@pytest.mark.asyncio
async def test_match_agency():

    async with ClientSession() as session:
        access_manager = AccessManager(
            email=get_from_env("PDAP_PROD_EMAIL"),
            password=get_from_env("PDAP_PROD_PASSWORD"),
            api_key=get_from_env("PDAP_API_KEY", allow_none=True),
            session=session
        )
        pdap_client = PDAPClient(access_manager=access_manager)

        response = await pdap_client.match_agency(name="police")

    print(response)

@pytest.mark.asyncio
async def test_check_for_duplicate():

    async with ClientSession() as session:
        access_manager = AccessManager(
            email=get_from_env("PDAP_PROD_EMAIL"),
            password=get_from_env("PDAP_PROD_PASSWORD"),
            api_key=get_from_env("PDAP_API_KEY", allow_none=True),
            session=session
        )
        pdap_client = PDAPClient(access_manager=access_manager)

        response = await pdap_client.is_url_duplicate(url_to_check="https://example.com")

    print(response)