from unittest.mock import create_autospec

import pytest
from discord_poster import DiscordPoster

from src.core.tasks.handler import TaskHandler
from src.core.tasks.scheduled.enums import IntervalEnum
from src.core.tasks.scheduled.impl.backlog.operator import PopulateBacklogSnapshotTaskOperator
from src.core.tasks.scheduled.loader import ScheduledTaskOperatorLoader
from src.core.tasks.scheduled.manager import AsyncScheduledTaskManager
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.core.tasks.scheduled.registry.core import ScheduledJobRegistry
from src.db.client.async_ import AsyncDatabaseClient


@pytest.fixture
def manager(adb_client_test: AsyncDatabaseClient) -> AsyncScheduledTaskManager:
    mock_discord_poster = create_autospec(DiscordPoster, instance=True)

    task_handler = TaskHandler(
        adb_client=adb_client_test,
        discord_poster=mock_discord_poster
    )
    mock_loader = create_autospec(
        ScheduledTaskOperatorLoader,
        instance=True
    )
    mock_loader.load_entries.return_value = [
        ScheduledTaskEntry(
            operator=PopulateBacklogSnapshotTaskOperator(adb_client=adb_client_test),
            interval=IntervalEnum.DAILY,
            enabled=True
        )
    ]
    registry = ScheduledJobRegistry()

    return AsyncScheduledTaskManager(
        handler=task_handler,
        loader=mock_loader,
        registry=registry
    )
