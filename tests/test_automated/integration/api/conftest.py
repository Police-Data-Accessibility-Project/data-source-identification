import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Generator
from unittest.mock import MagicMock, AsyncMock

import pytest
from starlette.testclient import TestClient

from api.main import app
from core.AsyncCore import AsyncCore
from core.SourceCollectorCore import SourceCollectorCore
from security_manager.SecurityManager import get_access_info, AccessInfo, Permissions
from tests.helpers.DBDataCreator import DBDataCreator
from tests.test_automated.integration.api.helpers.RequestValidator import RequestValidator


@dataclass
class APITestHelper:
    request_validator: RequestValidator
    core: SourceCollectorCore
    async_core: AsyncCore
    db_data_creator: DBDataCreator
    mock_huggingface_interface: MagicMock
    mock_label_studio_interface: MagicMock

    def adb_client(self):
        return self.db_data_creator.adb_client

MOCK_USER_ID = 1

def disable_task_trigger(ath: APITestHelper) -> None:
    ath.async_core.collector_manager.post_collection_function_trigger = AsyncMock()



async def fail_task_trigger() -> None:
    raise Exception(
        "Task Trigger is set to fail in tests by default, to catch unintentional calls."
        "If this is not intended, either replace with a Mock or the expected task function."
    )

def override_access_info() -> AccessInfo:
    return AccessInfo(user_id=MOCK_USER_ID, permissions=[Permissions.SOURCE_COLLECTOR])

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    # Mock envioronment
    _original_env = dict(os.environ)
    os.environ["DISCORD_WEBHOOK_URL"] = "https://discord.com"
    with TestClient(app) as c:
        app.dependency_overrides[get_access_info] = override_access_info
        core: SourceCollectorCore = c.app.state.core
        async_core: AsyncCore = c.app.state.async_core

        # Interfaces to the web should be mocked
        task_manager = async_core.task_manager
        task_manager.huggingface_interface = AsyncMock()
        task_manager.url_request_interface = AsyncMock()
        task_manager.discord_poster = AsyncMock()
        # Disable Logger
        task_manager.logger.disabled = True
        # Set trigger to fail immediately if called, to force it to be manually specified in tests
        task_manager.task_trigger._func = fail_task_trigger
        # core.shutdown()
        yield c
        core.shutdown()
    # Reset environment variables back to original state
    os.environ.clear()
    os.environ.update(_original_env)


@pytest.fixture
def api_test_helper(client: TestClient, db_data_creator, monkeypatch) -> APITestHelper:
    return APITestHelper(
        request_validator=RequestValidator(client=client),
        core=client.app.state.core,
        async_core=client.app.state.async_core,
        db_data_creator=db_data_creator,
        mock_huggingface_interface=MagicMock(),
        mock_label_studio_interface=MagicMock()
    )
