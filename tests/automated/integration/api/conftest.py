import asyncio
from dataclasses import dataclass
from typing import Generator
from unittest.mock import MagicMock, AsyncMock

import pytest
import pytest_asyncio
from starlette.testclient import TestClient

from api.main import app
from core.AsyncCore import AsyncCore
from api.routes.review import requires_final_review_permission
from core.DTOs.GetBatchStatusResponse import GetBatchStatusResponse
from core.SourceCollectorCore import SourceCollectorCore
from core.enums import BatchStatus
from security_manager.SecurityManager import get_access_info, AccessInfo, Permissions, require_permission
from tests.helpers.DBDataCreator import DBDataCreator
from tests.automated.integration.api.helpers.RequestValidator import RequestValidator


@dataclass
class APITestHelper:
    request_validator: RequestValidator
    core: SourceCollectorCore
    async_core: AsyncCore
    db_data_creator: DBDataCreator

    def adb_client(self):
        return self.db_data_creator.adb_client

    async def wait_for_all_batches_to_complete(self):
        for i in range(20):
            data: GetBatchStatusResponse = self.request_validator.get_batch_statuses(
                status=BatchStatus.IN_PROCESS
            )
            if len(data.results) == 0:
                return
            print("Waiting...")
            await asyncio.sleep(0.1)
        raise ValueError("Batches did not complete in expected time")

MOCK_USER_ID = 1

def disable_task_trigger(ath: APITestHelper) -> None:
    ath.async_core.collector_manager.post_collection_function_trigger = AsyncMock()



async def fail_task_trigger() -> None:
    raise Exception(
        "Task Trigger is set to fail in tests by default, to catch unintentional calls."
        "If this is not intended, either replace with a Mock or the expected task function."
    )

def override_access_info() -> AccessInfo:
    return AccessInfo(
        user_id=MOCK_USER_ID,
        permissions=[
            Permissions.SOURCE_COLLECTOR,
            Permissions.SOURCE_COLLECTOR_FINAL_REVIEW
        ]
    )

@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    # Mock environment
    with TestClient(app) as c:
        app.dependency_overrides[get_access_info] = override_access_info
        app.dependency_overrides[requires_final_review_permission] = override_access_info
        async_core: AsyncCore = c.app.state.async_core

        # Interfaces to the web should be mocked
        task_manager = async_core.task_manager
        task_manager.url_request_interface = AsyncMock()
        task_manager.discord_poster = AsyncMock()
        # Disable Logger
        task_manager.logger.disabled = True
        # Set trigger to fail immediately if called, to force it to be manually specified in tests
        task_manager.task_trigger._func = fail_task_trigger
        yield c

    # Reset environment variables back to original state


@pytest_asyncio.fixture
async def api_test_helper(client: TestClient, db_data_creator, monkeypatch) -> APITestHelper:
    yield APITestHelper(
        request_validator=RequestValidator(client=client),
        core=client.app.state.core,
        async_core=client.app.state.async_core,
        db_data_creator=db_data_creator,
    )
    await client.app.state.async_core.collector_manager.logger.clear_log_queue()
