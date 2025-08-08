import pytest

from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.probe.v2.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.probe.v2.setup.manager import TestURLProbeSetupManager


@pytest.mark.asyncio
async def test_url_probe_task_no_redirect_ok(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    """
    If a URL returns a 200 OK response,
    the task should add web metadata response to the database
    with
    - the correct status
    - the correct content_type
    - accessed = True
    - error_message = None
    """
    operator = setup_manager.setup_operator(
        response_or_responses=setup_manager.setup_no_redirect_probe_response(
            status_code=200,
            content_type="text/html",
            error=None
        )
    )
    assert not await operator.meets_task_prerequisites()
    url_id = await setup_manager.setup_url(URLStatus.PENDING)
    assert await operator.meets_task_prerequisites()
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)
    assert not await operator.meets_task_prerequisites()
    await check_manager.check_url(
        url_id=url_id,
        expected_status=URLStatus.PENDING
    )
    await check_manager.check_web_metadata(
        url_id=url_id,
        status_code=200,
        content_type="text/html",
        accessed=True,
        error=None
    )
    




