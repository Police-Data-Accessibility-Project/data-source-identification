import pytest

from src.external.url_request.probe.core import URLProbeManager

URLS = [
    "https://albanyoregon.gov/police/crime/statistics-crime-analysis",
    "https://www.example.com",
    "https://www.example.org",
    "https://www.nonexistent.com",
]


@pytest.mark.asyncio
async def test_url_probe(test_client_session):
    manager = URLProbeManager(session=test_client_session)
    results = await manager.probe_urls(urls=URLS)
    print(results)

@pytest.mark.asyncio
async def test_url_probe(test_client_session):
    manager = URLProbeManager(session=test_client_session)
    results = await manager._probe(url=URLS[0])
    print(results)