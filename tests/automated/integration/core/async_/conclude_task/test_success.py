import pytest

from src.core.enums import BatchStatus
from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.db.enums import TaskType
from tests.automated.integration.core.async_.conclude_task.helpers import setup_run_info
from tests.automated.integration.core.async_.conclude_task.setup_info import TestAsyncCoreSetupInfo
from tests.automated.integration.core.async_.helpers import setup_async_core
from tests.helpers.db_data_creator import DBDataCreator


@pytest.mark.asyncio
async def test_conclude_task_success(
    db_data_creator: DBDataCreator,
    setup: TestAsyncCoreSetupInfo
):
    ddc = db_data_creator

    run_info = setup_run_info(
        setup_info=setup,
        outcome=TaskOperatorOutcome.SUCCESS
    )

    core = setup_async_core(db_data_creator.adb_client)
    await core.task_manager.conclude_task(run_info=run_info)

    task_info = await ddc.adb_client.get_task_info(task_id=setup.task_id)

    assert task_info.task_status == BatchStatus.READY_TO_LABEL
    assert len(task_info.urls) == 3
