from unittest.mock import AsyncMock

import pytest

from src.core.tasks.scheduled.huggingface.operator import PushToHuggingFaceTaskOperator
from src.core.tasks.scheduled.huggingface.queries.get.model import GetForLoadingToHuggingFaceOutput
from tests.automated.integration.tasks.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.scheduled.huggingface.setup.manager import PushToHuggingFaceTestSetupManager
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_happy_path(
    operator: PushToHuggingFaceTaskOperator,
    db_data_creator: DBDataCreator
):
    hf_client = operator.hf_client
    push_function: AsyncMock = hf_client.push_data_sources_raw_to_hub

    # Check, prior to adding URLs, that task does not run
    task_info = await operator.run_task(1)
    assert_task_ran_without_error(task_info)
    push_function.assert_not_called()

    # Add URLs
    manager = PushToHuggingFaceTestSetupManager(adb_client=db_data_creator.adb_client)
    await manager.setup()

    # Run task
    task_info = await operator.run_task(2)
    assert_task_ran_without_error(task_info)
    push_function.assert_called_once()

    call_args: list[GetForLoadingToHuggingFaceOutput] = push_function.call_args.args[0]

    # Check for calls to HF Client
    manager.check_results(call_args)

    # Test that after update, running again yields no results
    task_info = await operator.run_task(3)
    assert_task_ran_without_error(task_info)
    push_function.assert_called_once()