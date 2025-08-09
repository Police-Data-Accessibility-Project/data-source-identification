import pytest

from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.url.probe.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.probe.constants import TEST_URL
from tests.automated.integration.tasks.url.probe.setup.manager import TestURLProbeSetupManager


@pytest.mark.asyncio
async def test_url_probe_task_redirect_infinite(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    """
    If a URL:
    - returns a redirect response to itself
    The task should add a link that points to itself
    as well as web metadata response to the database URL
    """

    operator = setup_manager.setup_operator(
        response_or_responses=setup_manager.setup_redirect_probe_response(
            redirect_status_code=303,
            dest_status_code=303,
            dest_content_type=None,
            dest_error=None,
            redirect_url=TEST_URL
        )
    )
    url_id = await setup_manager.setup_url(URLStatus.PENDING)
    run_info = await operator.run_task(1)
    await check_manager.check_url(
        url_id=url_id,
        expected_status=URLStatus.PENDING
    )
    await check_manager.check_web_metadata(
        url_id=url_id,
        status_code=303,
        content_type=None,
        error=None,
        accessed=True
    )
    redirect_url_id = await check_manager.check_redirect(
        source_url_id=url_id,
    )
    assert redirect_url_id == url_id
