from unittest.mock import AsyncMock

from src.core.core import AsyncCore
from src.core.tasks.handler import TaskHandler
from src.core.tasks.url.manager import TaskManager
from src.db.client.async_ import AsyncDatabaseClient


def setup_async_core(adb_client: AsyncDatabaseClient):
    return AsyncCore(
        adb_client=adb_client,
        task_manager=TaskManager(
            loader=AsyncMock(),
            handler=TaskHandler(
                adb_client=adb_client,
                discord_poster=AsyncMock()
            ),
        ),
        collector_manager=AsyncMock()
    )
