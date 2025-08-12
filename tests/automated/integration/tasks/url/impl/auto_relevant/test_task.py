from collections import Counter

import pytest

from src.collectors.enums import URLStatus
from src.db.enums import TaskType
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.error_info.sqlalchemy import URLErrorInfo
from src.db.models.impl.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from tests.automated.integration.tasks.url.impl.asserts import assert_prereqs_not_met, assert_url_task_has_expected_run_info, \
    assert_prereqs_met
from tests.automated.integration.tasks.url.impl.auto_relevant.setup import setup_operator, setup_urls


@pytest.mark.asyncio
async def test_url_auto_relevant_task(db_data_creator):

    operator = await setup_operator(adb_client=db_data_creator.adb_client)
    await assert_prereqs_not_met(operator)

    url_ids = await setup_urls(db_data_creator)
    await assert_prereqs_met(operator)

    task_id = await db_data_creator.adb_client.initiate_task(task_type=TaskType.RELEVANCY)

    run_info = await operator.run_task(task_id)

    assert_url_task_has_expected_run_info(run_info, url_ids)

    adb_client = db_data_creator.adb_client
    # Get URLs, confirm one is marked as error
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 3
    counter = Counter([url.status for url in urls])
    assert counter[URLStatus.ERROR] == 1
    assert counter[URLStatus.PENDING] == 2

    # Confirm two annotations were created
    suggestions: list[AutoRelevantSuggestion] = await adb_client.get_all(AutoRelevantSuggestion)
    assert len(suggestions) == 2
    for suggestion in suggestions:
        assert suggestion.url_id in url_ids
        assert suggestion.relevant is not None
        assert suggestion.confidence == 0.5
        assert suggestion.model_name == "test_model"

    # Confirm presence of url error
    errors = await adb_client.get_all(URLErrorInfo)
    assert len(errors) == 1



