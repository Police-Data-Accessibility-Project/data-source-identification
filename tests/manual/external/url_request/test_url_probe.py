import pytest

from src.external.url_request.probe import URLProbeManager

URLS = [
    "https://www.google.com",
    "https://www.example.com",
    "https://www.example.org",
    "https://www.nonexistent.com",
]

@pytest.mark.asyncio
async def test_url_probe_head(test_client_session):
    manager = URLProbeManager(session=test_client_session)
    result = await manager.head(url=URLS[0])
    print(result)

@pytest.mark.asyncio
async def test_url_probe(test_client_session):
    manager = URLProbeManager(session=test_client_session)
    results = await manager.probe_urls(urls=URLS)
    print(results)