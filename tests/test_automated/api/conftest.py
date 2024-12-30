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
        yield c
        core: SourceCollectorCore = c.app.state.core
        core.collector_manager.shutdown_all_collectors()
        core.collector_manager.logger.shutdown()

@pytest.fixture
def api_test_helper(client: TestClient) -> APITestHelper:
    return APITestHelper(request_validator=RequestValidator(client=client))