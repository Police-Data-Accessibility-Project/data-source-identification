import types
from unittest.mock import MagicMock, AsyncMock, call

import pytest

from collector_db.enums import TaskType
from collector_db.models import Task
from core.AsyncCore import AsyncCore
from core.DTOs.TaskOperatorRunInfo import TaskOperatorRunInfo, TaskOperatorOutcome
from core.enums import BatchStatus
from tests.helpers.DBDataCreator import DBDataCreator

@pytest.mark.asyncio
async def test_conclude_task_success(db_data_creator: DBDataCreator):
    ddc = db_data_creator

    batch_id = ddc.batch()
    url_ids = ddc.urls(batch_id=batch_id, url_count=3).url_ids
    task_id = await ddc.task()
    run_info = TaskOperatorRunInfo(
        task_id=task_id,
        linked_url_ids=url_ids,
        outcome=TaskOperatorOutcome.SUCCESS,
    )

    core = AsyncCore(
        adb_client=ddc.adb_client,
        task_manager=MagicMock(),
        collector_manager=MagicMock()
    )
    await core.conclude_task(run_info=run_info)

    task_info = await ddc.adb_client.get_task_info(task_id=task_id)

    assert task_info.task_status == BatchStatus.COMPLETE
    assert len(task_info.urls) == 3

@pytest.mark.asyncio
async def test_conclude_task_success(db_data_creator: DBDataCreator):
    ddc = db_data_creator

    batch_id = ddc.batch()
    url_ids = ddc.urls(batch_id=batch_id, url_count=3).url_ids
    task_id = await ddc.task()
    run_info = TaskOperatorRunInfo(
        task_id=task_id,
        linked_url_ids=url_ids,
        outcome=TaskOperatorOutcome.SUCCESS,
    )

    core = AsyncCore(
        adb_client=ddc.adb_client,
        task_manager=MagicMock(),
        collector_manager=MagicMock()
    )
    await core.task_manager.conclude_task(run_info=run_info)

    task_info = await ddc.adb_client.get_task_info(task_id=task_id)

    assert task_info.task_status == BatchStatus.COMPLETE
    assert len(task_info.urls) == 3

@pytest.mark.asyncio
async def test_conclude_task_error(db_data_creator: DBDataCreator):
    ddc = db_data_creator

    batch_id = ddc.batch()
    url_ids = ddc.urls(batch_id=batch_id, url_count=3).url_ids
    task_id = await ddc.task()
    run_info = TaskOperatorRunInfo(
        task_id=task_id,
        linked_url_ids=url_ids,
        outcome=TaskOperatorOutcome.ERROR,
        message="test error",
    )

    core = AsyncCore(
        adb_client=ddc.adb_client,
        task_manager=MagicMock(),
        collector_manager=MagicMock()
    )
    await core.task_manager.conclude_task(run_info=run_info)

    task_info = await ddc.adb_client.get_task_info(task_id=task_id)

    assert task_info.task_status == BatchStatus.ERROR
    assert task_info.error_info == "test error"
    assert len(task_info.urls) == 3

@pytest.mark.asyncio
async def test_run_task_prereq_not_met():
    core = AsyncCore(
        adb_client=AsyncMock(),
        task_manager=MagicMock(),
        collector_manager=MagicMock()
    )

    mock_operator = AsyncMock()
    mock_operator.meets_task_prerequisites = AsyncMock(return_value=False)
    AsyncCore.get_task_operators = AsyncMock(return_value=[mock_operator])
    await core.run_tasks()

    mock_operator.meets_task_prerequisites.assert_called_once()
    mock_operator.run_task.assert_not_called()

@pytest.mark.asyncio
async def test_run_task_prereq_met(db_data_creator: DBDataCreator):

    async def run_task(self, task_id: int) -> TaskOperatorRunInfo:
        return TaskOperatorRunInfo(
            task_id=task_id,
            outcome=TaskOperatorOutcome.SUCCESS,
            linked_url_ids=[1, 2, 3]
        )

    core = AsyncCore(
        adb_client=db_data_creator.adb_client,
        task_manager=MagicMock(),
        collector_manager=MagicMock()
    )
    core.conclude_task = AsyncMock()

    mock_operator = AsyncMock()
    mock_operator.meets_task_prerequisites = AsyncMock(
        side_effect=[True, False]
    )
    mock_operator.task_type = TaskType.HTML
    mock_operator.run_task = types.MethodType(run_task, mock_operator)

    AsyncCore.get_task_operators = AsyncMock(return_value=[mock_operator])
    await core.run_tasks()

    mock_operator.meets_task_prerequisites.assert_has_calls([call(), call()])

    results = await db_data_creator.adb_client.get_all(Task)

    assert len(results) == 1
    assert results[0].task_status == BatchStatus.IN_PROCESS.value

    core.conclude_task.assert_called_once()

@pytest.mark.asyncio
async def test_run_task_break_loop(db_data_creator: DBDataCreator):
    """
    If the task loop for a single task runs more than 20 times in a row,
    this is considered suspicious and possibly indicative of a bug.
    In this case, the task loop should be terminated
    and an alert should be sent to discord
    """

    async def run_task(self, task_id: int) -> TaskOperatorRunInfo:
        return TaskOperatorRunInfo(
            task_id=task_id,
            outcome=TaskOperatorOutcome.SUCCESS,
            linked_url_ids=[1, 2, 3]
        )

    core = AsyncCore(
        adb_client=db_data_creator.adb_client,
        task_manager=MagicMock(),
        collector_manager=MagicMock()
    )
    core.conclude_task = AsyncMock()

    mock_operator = AsyncMock()
    mock_operator.meets_task_prerequisites = AsyncMock(return_value=True)
    mock_operator.task_type = TaskType.HTML
    mock_operator.run_task = types.MethodType(run_task, mock_operator)

    AsyncCore.get_task_operators = AsyncMock(return_value=[mock_operator])
    await core.run_tasks()

    core.discord_poster.post_to_discord.assert_called_once_with(
        message="Task HTML has been run more than 20 times in a row. Task loop terminated."
    )
