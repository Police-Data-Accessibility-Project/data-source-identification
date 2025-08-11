import pytest
from aiohttp import ClientSession

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface


@pytest.mark.asyncio
async def test_muckrock_api_interface():

    async with ClientSession() as session:
        muckrock_api_interface = MuckrockAPIInterface(session=session)

        response = await muckrock_api_interface.lookup_agency(
            muckrock_agency_id=1
        )
        print(response)
