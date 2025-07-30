from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.dtos.run_info import URLTaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome


async def assert_prereqs_not_met(operator):
    meets_prereqs = await operator.meets_task_prerequisites()
    assert not meets_prereqs

async def assert_prereqs_met(operator):
    meets_prereqs = await operator.meets_task_prerequisites()
    assert meets_prereqs

def assert_task_ran_without_error(run_info: TaskOperatorRunInfo):
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message

def assert_url_task_has_expected_run_info(run_info: URLTaskOperatorRunInfo, url_ids: list[int]):
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message
    assert run_info.linked_url_ids == url_ids
