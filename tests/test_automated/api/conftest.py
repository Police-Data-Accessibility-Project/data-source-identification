from dataclasses import dataclass
from typing import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.params import Security
from fastapi.security import HTTPAuthorizationCredentials
from starlette.testclient import TestClient

from api.main import app
from core.SourceCollectorCore import SourceCollectorCore
from helpers.DBDataCreator import DBDataCreator
from security_manager.SecurityManager import get_access_info, AccessInfo, Permissions
from tests.test_automated.api.helpers.RequestValidator import RequestValidator


@dataclass
class APITestHelper:
    request_validator: RequestValidator
    core: SourceCollectorCore
    db_data_creator: DBDataCreator



def override_access_info(token) -> AccessInfo:
    return AccessInfo(user_id=1, permissions=[Permissions.SOURCE_COLLECTOR])

@pytest.fixture
def client(db_client_test) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        app.dependency_overrides[get_access_info] = override_access_info
        core: SourceCollectorCore = c.app.state.core
        core.shutdown()
        yield c
        core.shutdown()

@pytest.fixture
def api_test_helper(client: TestClient, db_data_creator) -> APITestHelper:
    return APITestHelper(
        request_validator=RequestValidator(client=client),
        core=client.app.state.core,
        db_data_creator=db_data_creator
    )