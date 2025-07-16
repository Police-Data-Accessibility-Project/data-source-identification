import pytest


@pytest.mark.asyncio
async def test_check_for_duplicate(pdap_client):

    response = await pdap_client.is_url_duplicate(url_to_check="https://example.com")

    print(response)
