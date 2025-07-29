import types

import pytest

from src.db.enums import TaskType
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.core.tasks.url.operators.base import URLTaskOperatorBase
from tests.helpers.data_creator.core import DBDataCreator

class ExampleTaskOperator(URLTaskOperatorBase):

    @property
    def task_type(self) -> TaskType:
        # Use TaskType.HTML so we don't have to add a test enum value to the db
        return TaskType.HTML

    def inner_task_logic(self):
        raise NotImplementedError

    async def meets_task_prerequisites(self):
        return True

@pytest.mark.asyncio
async def test_example_task_success(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(
        batch_id=batch_id,
        url_count=3
    ).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]

    async def mock_inner_task_logic(self):
        # Add link to 3 urls
        self.linked_url_ids = url_ids

    operator = ExampleTaskOperator(adb_client=db_data_creator.adb_client)
    operator.inner_task_logic = types.MethodType(mock_inner_task_logic, operator)

    run_info = await operator.run_task(1)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS
    assert run_info.linked_url_ids == url_ids


@pytest.mark.asyncio
async def test_example_task_failure(db_data_creator: DBDataCreator):
    operator = ExampleTaskOperator(adb_client=db_data_creator.adb_client)

    def mock_inner_task_logic(self):
        raise ValueError("test error")

    operator.inner_task_logic = types.MethodType(mock_inner_task_logic, operator)
    run_info = await operator.run_task(1)
    assert run_info.outcome == TaskOperatorOutcome.ERROR



