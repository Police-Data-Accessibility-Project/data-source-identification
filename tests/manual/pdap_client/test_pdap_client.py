import pytest
from aiohttp import ClientSession

from pdap_api_client.AccessManager import AccessManager
from pdap_api_client.PDAPClient import PDAPClient
from util.helper_functions import get_from_env


@pytest.mark.asyncio
async def test_match_agency():

    async with ClientSession() as session:
        access_manager = AccessManager(
            email=get_from_env("PDAP_EMAIL"),
            password=get_from_env("PDAP_PASSWORD"),
            api_key=get_from_env("PDAP_API_KEY", allow_none=True),
            session=session
        )
        pdap_client = PDAPClient(access_manager=access_manager)

        response = await pdap_client.match_agency(name="police")

    print(response)
