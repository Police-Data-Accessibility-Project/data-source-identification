import pytest_asyncio

from src.core.tasks.url.operators.probe.core import URLProbeTaskOperator
from src.external.url_request.core import URLRequestInterface
from tests.automated.integration.tasks.url.probe.constants import PATCH_ROOT
from tests.automated.integration.tasks.url.probe.setup.mocks.probe_manager import MockURLProbeManager


@pytest_asyncio.fixture
async def operator(adb_client_test, monkeypatch):
    monkeypatch.setattr(PATCH_ROOT, MockURLProbeManager)
    yield URLProbeTaskOperator(
        adb_client=adb_client_test,
        url_request_interface=URLRequestInterface()
    )
