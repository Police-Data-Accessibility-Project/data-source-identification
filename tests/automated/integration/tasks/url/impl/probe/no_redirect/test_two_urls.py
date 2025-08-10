import pytest

from src.collectors.enums import URLStatus
from src.db.models.instantiations.url.core.sqlalchemy import URL
from tests.automated.integration.tasks.url.impl.asserts import assert_task_ran_without_error
from tests.automated.integration.tasks.url.impl.probe.check.manager import TestURLProbeCheckManager
from tests.automated.integration.tasks.url.impl.probe.setup.manager import TestURLProbeSetupManager


@pytest.mark.asyncio
async def test_two_urls(
    setup_manager: TestURLProbeSetupManager,
    check_manager: TestURLProbeCheckManager
):
    url_1 = "https://example.com/1"
    url_2 = "https://example.com/2"
    operator = setup_manager.setup_operator(
        response_or_responses=[
            setup_manager.setup_no_redirect_probe_response(
                status_code=200,
                content_type="text/html",
                error=None,
                url=url_1
            ),
            setup_manager.setup_no_redirect_probe_response(
                status_code=200,
                content_type="text/html",
                error=None,
                url=url_2
            )
        ]
    )
    assert not await operator.meets_task_prerequisites()
    url_id_1 = await setup_manager.setup_url(URLStatus.PENDING, url=url_1)
    url_id_2 = await setup_manager.setup_url(URLStatus.NOT_RELEVANT, url=url_2)
    assert await operator.meets_task_prerequisites()
    run_info = await operator.run_task(1)
    assert_task_ran_without_error(run_info)
    assert not await operator.meets_task_prerequisites()

    urls = await check_manager.adb_client.get_all(URL)
    assert len(urls) == 2
