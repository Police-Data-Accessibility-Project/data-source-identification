import pytest

from src.core.tasks.scheduled.manager import AsyncScheduledTaskManager


@pytest.mark.asyncio
async def test_add_scheduled_tasks(manager: AsyncScheduledTaskManager):
    await manager.setup()

    assert len(manager._registry._jobs) == 1

