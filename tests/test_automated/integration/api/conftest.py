from dataclasses import dataclass
from typing import Generator
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient

from api.main import app
from core.SourceCollectorCore import SourceCollectorCore
from tests.helpers.DBDataCreator import DBDataCreator
from security_manager.SecurityManager import get_access_info, AccessInfo, Permissions
from tests.test_automated.integration.api.helpers.RequestValidator import RequestValidator


@dataclass
class APITestHelper:
    request_validator: RequestValidator
    core: SourceCollectorCore
    db_data_creator: DBDataCreator
    mock_huggingface_interface: MagicMock
    mock_label_studio_interface: MagicMock

MOCK_USER_ID = 1


def override_access_info() -> AccessInfo:
    return AccessInfo(user_id=MOCK_USER_ID, permissions=[Permissions.SOURCE_COLLECTOR])

@pytest.fixture
def client(db_client_test) -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        app.dependency_overrides[get_access_info] = override_access_info
        core: SourceCollectorCore = c.app.state.core
        # core.shutdown()
        yield c
        core.shutdown()

@pytest.fixture
def api_test_helper(client: TestClient, db_data_creator, monkeypatch) -> APITestHelper:

    return APITestHelper(
        request_validator=RequestValidator(client=client),
        core=client.app.state.core,
        db_data_creator=db_data_creator,
        mock_huggingface_interface=MagicMock(),
        mock_label_studio_interface=MagicMock()
    )