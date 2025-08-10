import pytest

from src.collectors.enums import URLStatus
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.probe.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.impl.probe.setup.manager import TestURLProbeSetupManager


@pytest.mark.asyncio
async def test_url_probe_task_redirect_two_urls_same_dest(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    """
    If two URLs:
    - return a redirect response to the same URL
    Two links to that URL should be added to the database, one for each URL
    """

    operator = setup_manager.setup_operator(
        response_or_responses=[
            setup_manager.setup_redirect_probe_response(
                redirect_status_code=307,
                dest_status_code=200,
                dest_content_type=None,
                dest_error=None,
            ),
            setup_manager.setup_redirect_probe_response(
                redirect_status_code=308,
                dest_status_code=200,
                dest_content_type=None,
                dest_error=None,
                source_url="https://example.com/2",
            ),
        ]
    )
    source_url_id_1 = await setup_manager.setup_url(URLStatus.PENDING)
    source_url_id_2 = await setup_manager.setup_url(URLStatus.PENDING, url="https://example.com/2")
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)
    await check_manager.check_url(
        url_id=source_url_id_1,
        expected_status=URLStatus.PENDING
    )
    await check_manager.check_url(
        url_id=source_url_id_2,
        expected_status=URLStatus.PENDING
    )
    redirect_url_id_1 = await check_manager.check_redirect(
        source_url_id=source_url_id_1
    )
    redirect_url_id_2 = await check_manager.check_redirect(
        source_url_id=source_url_id_2
    )
    assert redirect_url_id_1 == redirect_url_id_2

