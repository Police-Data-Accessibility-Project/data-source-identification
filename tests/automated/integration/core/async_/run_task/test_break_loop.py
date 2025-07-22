import types
from unittest.mock import AsyncMock

import pytest

from src.db.enums import TaskType
from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from tests.automated.integration.core.async_.helpers import setup_async_core
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_run_task_break_loop(db_data_creator: DBDataCreator):
    """
    If the task loop for a single task runs more than 20 times in a row,
    this is considered suspicious and possibly indicative of a bug.
    In this case, the task loop should be terminated
    and an alert should be sent to discord
    """

    async def run_task(self, task_id: int) -> URLTaskOperatorRunInfo:
        return URLTaskOperatorRunInfo(
            task_id=task_id,
            outcome=TaskOperatorOutcome.SUCCESS,
            linked_url_ids=[1, 2, 3],
            task_type=TaskType.HTML
        )

    core = setup_async_core(db_data_creator.adb_client)
    core.task_manager.conclude_task = AsyncMock()

    mock_operator = AsyncMock()
    mock_operator.meets_task_prerequisites = AsyncMock(return_value=True)
    mock_operator.task_type = TaskType.HTML
    mock_operator.run_task = types.MethodType(run_task, mock_operator)

    core.task_manager.loader.get_task_operators = AsyncMock(return_value=[mock_operator])
    await core.task_manager.trigger_task_run()

    core.task_manager.handler.discord_poster.post_to_discord.assert_called_once_with(
        message="Task HTML has been run more than 20 times in a row. Task loop terminated."
    )
