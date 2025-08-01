import pytest

from src.db.enums import TaskType
from src.db.models.instantiations.url.core import URL
from src.db.models.instantiations.url.error_info import URLErrorInfo
from src.db.models.instantiations.url.suggestion.relevant.auto import AutoRelevantSuggestion
from tests.automated.integration.tasks.asserts import assert_prereqs_not_met, assert_task_has_expected_run_info, \
    assert_prereqs_met
from tests.automated.integration.tasks.url.auto_relevant.setup import setup_operator, setup_urls


@pytest.mark.asyncio
async def test_url_auto_relevant_task(db_data_creator):

    operator = await setup_operator(adb_client=db_data_creator.adb_client)
    await assert_prereqs_not_met(operator)

    url_ids = await setup_urls(db_data_creator)
    await assert_prereqs_met(operator)

    task_id = await db_data_creator.adb_client.initiate_task(task_type=TaskType.RELEVANCY)

    run_info = await operator.run_task(task_id)

    assert_task_has_expected_run_info(run_info, url_ids)

    adb_client = db_data_creator.adb_client
    # Get URLs, confirm one is marked as error
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 3
    statuses = [url.outcome for url in urls]
    assert sorted(statuses) == sorted(["pending", "pending", "error"])

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



