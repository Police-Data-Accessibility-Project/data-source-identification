import types
from unittest.mock import AsyncMock, call, create_autospec

import pytest

from src.core.enums import BatchStatus
from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.core.tasks.url.models.entry import URLTaskEntry
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from src.db.enums import TaskType
from src.db.models.impl.task.core import Task
from tests.automated.integration.core.async_.helpers import setup_async_core
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_run_task_prereq_met(db_data_creator: DBDataCreator):
    """
    When a task pre-requisite is met, the task should be run
    And a task entry should be created in the database
    """

    async def run_task(self, task_id: int) -> URLTaskOperatorRunInfo:
        return URLTaskOperatorRunInfo(
            task_id=task_id,
            task_type=TaskType.HTML,
            outcome=TaskOperatorOutcome.SUCCESS,
            linked_url_ids=[1, 2, 3]
        )

    core = setup_async_core(db_data_creator.adb_client)
    core.task_manager.conclude_task = AsyncMock()

    mock_operator = create_autospec(URLTaskOperatorBase, instance=True)
    mock_operator.meets_task_prerequisites = AsyncMock(
        side_effect=[True, False]
    )
    mock_operator.task_type = TaskType.HTML
    mock_operator.run_task = types.MethodType(run_task, mock_operator)
    entry = URLTaskEntry(
        operator=mock_operator,
        enabled=True
    )

    core.task_manager.loader.load_entries = AsyncMock(return_value=[entry])
    await core.run_tasks()

    # There should be two calls to meets_task_prerequisites
    mock_operator.meets_task_prerequisites.assert_has_calls([call(), call()])

    results = await db_data_creator.adb_client.get_all(Task)

    assert len(results) == 1
    assert results[0].task_status == BatchStatus.IN_PROCESS.value

    core.task_manager.conclude_task.assert_called_once()
