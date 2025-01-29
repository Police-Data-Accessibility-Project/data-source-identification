import types

import pytest

from collector_db.enums import TaskType
from core.classes.TaskOperatorBase import TaskOperatorBase
from core.enums import BatchStatus
from tests.helpers.DBDataCreator import DBDataCreator

class ExampleTaskOperator(TaskOperatorBase):

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
        await self.adb_client.link_urls_to_task(task_id=self.task_id, url_ids=url_ids)
        self.tasks_linked = True

    operator = ExampleTaskOperator(adb_client=db_data_creator.adb_client)
    operator.inner_task_logic = types.MethodType(mock_inner_task_logic, operator)

    await operator.run_task()

    # Get Task Info
    task_info = await db_data_creator.adb_client.get_task_info(task_id=operator.task_id)

    # Check that 3 urls were linked to the task
    assert len(task_info.urls) == 3

    # Check that error info is empty
    assert task_info.error_info is None

    # Check that the task was marked as complete
    assert task_info.task_status == BatchStatus.COMPLETE

    # Check that the task type is HTML
    assert task_info.task_type == TaskType.HTML


    # Check that updated_at is not null
    assert task_info.updated_at is not None

@pytest.mark.asyncio
async def test_example_task_failure(db_data_creator: DBDataCreator):
    operator = ExampleTaskOperator(adb_client=db_data_creator.adb_client)

    def mock_inner_task_logic(self):
        raise ValueError("test error")

    operator.inner_task_logic = types.MethodType(mock_inner_task_logic, operator)
    await operator.run_task()

    # Get Task Info
    task_info = await db_data_creator.adb_client.get_task_info(task_id=operator.task_id)

    # Check that there are no URLs associated
    assert len(task_info.urls) == 0

    # Check that the task was marked as errored
    assert task_info.task_status == BatchStatus.ERROR

    # Check that the task type is HTML
    assert task_info.task_type == TaskType.HTML

    # Check error
    assert "test error" in task_info.error_info



