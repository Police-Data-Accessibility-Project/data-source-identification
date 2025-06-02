import pytest

from src.core.tasks.operators.url_html.scraper.root_url_cache.core import RootURLCache
from src.core.tasks.operators.url_html.scraper.root_url_cache.dtos.response import RootURLCacheResponseInfo


async def mock_get_request(url: str) -> RootURLCacheResponseInfo:
    return RootURLCacheResponseInfo(text="<html><head><title>Test Title</title></head></html>")

@pytest.mark.asyncio
async def test_root_url_cache_happy_path(wipe_database):
    cache = RootURLCache()
    cache.get_request = mock_get_request
    title = await cache.get_title("https://example.com")
    assert title == "Test Title"

    # Check that entry is in database
    d = await cache.adb_client.load_root_url_cache()
    assert d["https://example.com"] == "Test Title"