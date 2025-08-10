from unittest.mock import AsyncMock, create_autospec

import pytest

from src.core.core import AsyncCore
from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader
from src.db.client.async_ import AsyncDatabaseClient
from src.external.huggingface.hub.client import HuggingFaceHubClient
from src.external.pdap.client import PDAPClient


@pytest.fixture(scope="session")
def loader() -> ScheduledTaskOperatorLoader:
    """Setup loader with mock dependencies"""
    return ScheduledTaskOperatorLoader(
        async_core=create_autospec(AsyncCore, instance=True),
        adb_client=AsyncMock(spec=AsyncDatabaseClient),
        pdap_client=AsyncMock(spec=PDAPClient),
        hf_client=AsyncMock(spec=HuggingFaceHubClient)
    )