from unittest.mock import MagicMock

import pytest

from src.core.tasks.scheduled.huggingface.operator import PushToHuggingFaceTaskOperator
from src.external.huggingface.hub.client import HuggingFaceHubClient


@pytest.fixture
def operator(adb_client_test):
    yield PushToHuggingFaceTaskOperator(
        adb_client=adb_client_test,
        hf_client=MagicMock(spec=HuggingFaceHubClient)
    )