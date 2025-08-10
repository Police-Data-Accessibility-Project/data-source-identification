import asyncio

import pytest

from src.core.tasks.scheduled.enums import IntervalEnum
from src.core.tasks.scheduled.impl.backlog.operator import PopulateBacklogSnapshotTaskOperator
from src.core.tasks.scheduled.manager import AsyncScheduledTaskManager
from src.core.tasks.scheduled.models.entry import ScheduledTaskEntry
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.instantiations.task.core import Task


@pytest.mark.asyncio
async def test_add_job(
    manager: AsyncScheduledTaskManager,
    adb_client_test: AsyncDatabaseClient
):
    manager._registry.start_scheduler()
    await manager._registry.add_job(
        func=manager.run_task,
        entry=ScheduledTaskEntry(
            operator=PopulateBacklogSnapshotTaskOperator(
                adb_client=adb_client_test
            ),
            interval=IntervalEnum.DAILY,
            enabled=True
        ),
        minute_lag=0
    )

    assert len(manager._registry._jobs) == 1
    # Sleep to allow task to run
    await asyncio.sleep(0.5)
    # Confirm task ran
    tasks = await adb_client_test.get_all(Task)
    assert len(tasks) == 1