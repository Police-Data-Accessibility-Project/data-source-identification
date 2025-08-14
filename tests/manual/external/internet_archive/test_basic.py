import pytest
from aiohttp import ClientSession

from src.external.internet_archive.client import InternetArchiveClient
from src.external.internet_archive.models.capture import IACapture

# BASE_URL = "nola.gov/getattachment/NOPD/Policies/Chapter-12-1-Department-Operations-Manual-EFFECTIVE-1-14-18.pdf/"
BASE_URL = "example.com"
# BASE_URL = "hk45jk"

@pytest.mark.asyncio
async def test_basic():
    """Test basic requests to the Internet Archive."""

    async with ClientSession() as session:
        client = InternetArchiveClient(session)
        response = await client.search_for_url_snapshot(BASE_URL)
        print(response)