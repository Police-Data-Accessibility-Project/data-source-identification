import pytest

from src.api.endpoints.search.dtos.response import SearchURLResponse


@pytest.mark.asyncio
async def test_search_url(api_test_helper):
    ath = api_test_helper

    # Create a batch with 1 URL
    creation_info = await ath.db_data_creator.batch_and_urls(url_count=1, with_html_content=False)

    # Search for that URL and locate it
    response: SearchURLResponse = await ath.request_validator.search_url(url=creation_info.urls[0])

    assert response.found
    assert response.url_id == creation_info.url_ids[0]

    # Search for a non-existent URL
    response: SearchURLResponse = await ath.request_validator.search_url(url="http://doesnotexist.com")

    assert not response.found
    assert response.url_id is None