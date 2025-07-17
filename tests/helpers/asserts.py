from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.enums import TaskOperatorOutcome


def assert_task_run_success(run_info: TaskOperatorRunInfo):
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message