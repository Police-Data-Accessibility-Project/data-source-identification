import pytest

from collector_db.DTOs.URLWithHTML import URLWithHTML
from hugging_face.HuggingFaceInterface import HuggingFaceInterface

@pytest.mark.asyncio
async def test_get_url_relevancy():
    hfi = HuggingFaceInterface()
    def package_url(url: str) -> URLWithHTML:
        return URLWithHTML(url=url, url_id=1, html_infos=[])

    result = await hfi.get_url_relevancy_async([
        package_url("https://coloradosprings.gov/police-department/article/news/i-25-traffic-safety-deployment-after-stop"),
        package_url("https://example.com"),
        package_url("https://police.com")
    ])
    print(result)


