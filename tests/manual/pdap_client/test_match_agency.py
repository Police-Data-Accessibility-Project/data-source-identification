import pytest


@pytest.mark.asyncio
async def test_match_agency(pdap_client):
    response = await pdap_client.match_agency(name="police")
