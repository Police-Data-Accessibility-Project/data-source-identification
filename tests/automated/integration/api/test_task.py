import pytest

from db.enums import TaskType
from tests.automated.integration.api.conftest import APITestHelper


async def task_setup(ath: APITestHelper) -> int:
    iui = ath.db_data_creator.urls(batch_id=ath.db_data_creator.batch(), url_count=3)
    url_ids = [url.url_id for url in iui.url_mappings]

    task_id = await ath.db_data_creator.task(url_ids=url_ids)
    await ath.db_data_creator.error_info(url_ids=[url_ids[0]], task_id=task_id)

    return task_id

@pytest.mark.asyncio
async def test_get_task_info(api_test_helper):
    ath = api_test_helper

    task_id = await task_setup(ath)

    task_info = ath.request_validator.get_task_info(task_id=task_id)

    assert len(task_info.urls) == 3
    assert len(task_info.url_errors) == 1

    assert task_info.task_type == TaskType.HTML

@pytest.mark.asyncio
async def test_get_tasks(api_test_helper):
    ath = api_test_helper
    for i in range(2):
        await task_setup(ath)

    response = ath.request_validator.get_tasks(page=1, task_type=None, task_status=None)

    assert len(response.tasks) == 2
    for task in response.tasks:
        assert task.type == TaskType.HTML
        assert task.url_count == 3
        assert task.url_error_count == 1

@pytest.mark.asyncio
async def test_get_task_status(api_test_helper):
    ath = api_test_helper

    response = await ath.request_validator.get_current_task_status()

    assert response.status == TaskType.IDLE

    for task in [task for task in TaskType]:
        await ath.async_core.task_manager.set_task_status(task)
        response = await ath.request_validator.get_current_task_status()

        assert response.status == task
