from unittest.mock import AsyncMock

import pytest

from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.core.tasks.url.loader import URLTaskOperatorLoader
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.inference.client import HuggingFaceInferenceClient
from src.external.internet_archives.client import InternetArchivesClient
from src.external.pdap.client import PDAPClient
from src.external.url_request.core import URLRequestInterface


@pytest.fixture(scope="session")
def loader() -> URLTaskOperatorLoader:
    """Setup loader with mock dependencies"""
    return URLTaskOperatorLoader(
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        url_request_interface=AsyncMock(spec=URLRequestInterface),
        html_parser=AsyncMock(spec=HTMLResponseParser),
        pdap_client=AsyncMock(spec=PDAPClient),
        muckrock_api_interface=AsyncMock(spec=MuckrockAPIInterface),
        hf_inference_client=AsyncMock(spec=HuggingFaceInferenceClient),
        ia_client=AsyncMock(spec=InternetArchivesClient)
    )