import pytest

from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType


@pytest.mark.asyncio
async def test_task_enums(adb_client_test: AsyncDatabaseClient) -> None:

    for task_type in TaskType:
        if task_type == TaskType.IDLE:
            continue
        await adb_client_test.initiate_task(task_type=task_type)