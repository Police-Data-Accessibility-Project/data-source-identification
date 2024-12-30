from dataclasses import dataclass
from typing import Generator

import pytest
from starlette.testclient import TestClient

from api.main import app
from core.SourceCollectorCore import SourceCollectorCore
from tests.test_automated.api.helpers.RequestValidator import RequestValidator


@dataclass
class APITestHelper:
    request_validator: RequestValidator

@pytest.fixture
def client(db_client_test) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        core: SourceCollectorCore = c.app.state.core
        core.shutdown()
        yield c
        core.shutdown()

@pytest.fixture
def api_test_helper(client: TestClient) -> APITestHelper:
    return APITestHelper(request_validator=RequestValidator(client=client))