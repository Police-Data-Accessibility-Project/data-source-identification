import pytest

from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.probe.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.impl.probe.setup.manager import TestURLProbeSetupManager


@pytest.mark.asyncio
async def test_url_probe_task_not_found(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    """
    If a URL returns a 404 error response,
    the task should add web metadata response to the database
    with
    - the correct status
    - content_type = None
    - accessed = False
    - error_message = "Not found."
    """

    operator = setup_manager.setup_operator(
        response_or_responses=setup_manager.setup_no_redirect_probe_response(
            status_code=404,
            content_type=None,
            error="Not found."
        )
    )
    assert not await operator.meets_task_prerequisites()
    url_id = await setup_manager.setup_url(URLStatus.NOT_RELEVANT)
    assert await operator.meets_task_prerequisites()
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)
    assert not await operator.meets_task_prerequisites()
    await check_manager.check_url(
        url_id=url_id,
        expected_status=URLStatus.NOT_RELEVANT
    )
    await check_manager.check_web_metadata(
        url_id=url_id,
        status_code=404,
        content_type=None,
        error="Not found.",
        accessed=False
    )