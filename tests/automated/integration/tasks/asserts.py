from src.core.tasks.url.enums import TaskOperatorOutcome


async def assert_prereqs_not_met(operator):
    meets_prereqs = await operator.meets_task_prerequisites()
    assert not meets_prereqs


def assert_task_has_expected_run_info(run_info, url_ids: list[int]):
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS
    assert run_info.linked_url_ids == url_ids
