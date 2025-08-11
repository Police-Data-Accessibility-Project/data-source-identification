import pytest

from src.external.url_request.probe.core import URLProbeManager

URLS = [
'https://www.opendataphilly.org/dataset?q=crime+map&sort=score+desc%2C+metadata_modified+desc'
    # "https://tableau.alleghenycounty.us/t/PublicSite/views/PublicBudgetDashboard_17283931835700/OperatingOverview?%3Aembed=y&%3AisGuestRedirectFromVizportal=y"
    # "data.austintexas.gov/resource/sc6h-qr9f.json"
    # "https://albanyoregon.gov/police/crime/statistics-crime-analysis",
    # "https://www.example.com",
    # "https://www.example.org",
    # "https://www.nonexistent.com",
]


@pytest.mark.asyncio
async def test_url_probe(test_client_session):
    manager = URLProbeManager(session=test_client_session)
    results = await manager.probe_urls(urls=URLS)
    print(results)
