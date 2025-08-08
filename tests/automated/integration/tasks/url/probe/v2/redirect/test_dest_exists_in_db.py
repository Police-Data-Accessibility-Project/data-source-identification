import pytest

from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.web_metadata.insert import URLWebMetadataPydantic
from tests.automated.integration.tasks.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.probe.v2.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.probe.v2.constants import TEST_DEST_URL
from tests.automated.integration.tasks.url.probe.v2.setup.manager import TestURLProbeSetupManager


@pytest.mark.asyncio
async def test_url_probe_task_redirect_dest_exists_in_db(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    """
    If a URL:
    - returns a redirect response to a new URL,
    - and the new URL already exists in the database,
    the task should add web metadata response to the database URL
    and a link between the original URL and the new URL.

    """
    operator = setup_manager.setup_operator(
        response_or_responses=setup_manager.setup_redirect_probe_response(
            redirect_status_code=302,
            dest_status_code=200,
            dest_content_type="text/html",
            dest_error=None
        )
    )
    source_url_id = await setup_manager.setup_url(URLStatus.INDIVIDUAL_RECORD)
    dest_url_id = await setup_manager.setup_url(URLStatus.PENDING, url=TEST_DEST_URL)
    # Add web metadata for destination URL, to prevent it from being pulled
    web_metadata = URLWebMetadataPydantic(
        url_id=dest_url_id,
        status_code=200,
        content_type="text/html",
        error_message=None,
        accessed=True
    )
    await setup_manager.adb_client.bulk_insert([web_metadata])
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)
    await check_manager.check_url(
        url_id=source_url_id,
        expected_status=URLStatus.INDIVIDUAL_RECORD
    )
    await check_manager.check_url(
        url_id=dest_url_id,
        expected_status=URLStatus.PENDING
    )
    await check_manager.check_web_metadata(
        url_id=source_url_id,
        status_code=302,
        content_type=None,
        error=None,
        accessed=True
    )
    await check_manager.check_web_metadata(
        url_id=dest_url_id,
        status_code=200,
        content_type="text/html",
        error=None,
        accessed=True
    )
    redirect_url_id = await check_manager.check_redirect(
        source_url_id=source_url_id
    )
    assert redirect_url_id == dest_url_id