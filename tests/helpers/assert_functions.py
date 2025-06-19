from src.core.tasks.dtos.run_info import TaskOperatorRunInfo
from src.core.tasks.enums import TaskOperatorOutcome


def assert_task_run_success(run_info: TaskOperatorRunInfo):
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message