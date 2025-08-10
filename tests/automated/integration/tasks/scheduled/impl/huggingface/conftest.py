from unittest.mock import AsyncMock

import pytest

from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.external.huggingface.hub.client import HuggingFaceHubClient


@pytest.fixture
def operator(adb_client_test):
    yield PushToHuggingFaceTaskOperator(
        adb_client=adb_client_test,
        hf_client=AsyncMock(spec=HuggingFaceHubClient)
    )