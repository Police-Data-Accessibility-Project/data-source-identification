import pytest

from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.probe.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.probe.setup.manager import TestURLProbeSetupManager


@pytest.mark.asyncio
async def test_url_probe_task_redirect_dest_new_ok(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    """
    If a URL
    - returns a redirect response to a new URL,
    - and the new URL returns a 200 OK response and does not exist in the database,
    the task
    - should add the new URL to the database
    - along with web metadata response to the database
    - and the link between the original URL and the new URL.
    """
    operator = setup_manager.setup_operator(
        response_or_responses=setup_manager.setup_redirect_probe_response(
            redirect_status_code=301,
            dest_status_code=200,
            dest_content_type="text/html",
            dest_error=None
        )
    )
    source_url_id = await setup_manager.setup_url(URLStatus.PENDING)
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)
    await check_manager.check_url(
        url_id=source_url_id,
        expected_status=URLStatus.PENDING
    )
    await check_manager.check_web_metadata(
        url_id=source_url_id,
        status_code=301,
        content_type=None,
        error=None,
        accessed=True
    )
    dest_url_id = await check_manager.check_redirect(source_url_id)
    await check_manager.check_url(
        url_id=dest_url_id,
        expected_status=URLStatus.PENDING
    )
    await check_manager.check_web_metadata(
        url_id=dest_url_id,
        status_code=200,
        content_type="text/html",
        error=None,
        accessed=True
    )