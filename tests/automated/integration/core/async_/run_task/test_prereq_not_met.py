from unittest.mock import AsyncMock, create_autospec

import pytest

from src.core.tasks.url.models.entry import URLTaskEntry
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from tests.automated.integration.core.async_.helpers import setup_async_core


@pytest.mark.asyncio
async def test_run_task_prereq_not_met():
    """
    When a task pre-requisite is not met, the task should not be run
    """
    core = setup_async_core(AsyncMock())

    mock_operator = create_autospec(URLTaskOperatorBase, instance=True)
    mock_operator.meets_task_prerequisites = AsyncMock(return_value=False)
    entry = URLTaskEntry(operator=mock_operator, enabled=True)
    core.task_manager.loader.load_entries = AsyncMock(return_value=[entry])
    await core.run_tasks()

    mock_operator.meets_task_prerequisites.assert_called_once()
    mock_operator.run_task.assert_not_called()
