from unittest.mock import AsyncMock

import pytest

from tests.automated.integration.core.async_.helpers import setup_async_core


@pytest.mark.asyncio
async def test_run_task_prereq_not_met():
    """
    When a task pre-requisite is not met, the task should not be run
    """
    core = setup_async_core(AsyncMock())

    mock_operator = AsyncMock()
    mock_operator.meets_task_prerequisites = AsyncMock(return_value=False)
    core.task_manager.loader.get_task_operators = AsyncMock(return_value=[mock_operator])
    await core.run_tasks()

    mock_operator.meets_task_prerequisites.assert_called_once()
    mock_operator.run_task.assert_not_called()
