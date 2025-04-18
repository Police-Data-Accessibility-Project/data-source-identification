from unittest.mock import MagicMock

import pytest

from collector_db.AsyncDatabaseClient import AsyncDatabaseClient
from collector_db.DTOs.URLWithHTML import URLWithHTML
from collector_db.models import AutoRelevantSuggestion
from core.DTOs.TaskOperatorRunInfo import TaskOperatorRunInfo, TaskOperatorOutcome
from core.classes.task_operators.URLRelevanceHuggingfaceTaskOperator import URLRelevanceHuggingfaceTaskOperator
from tests.helpers.assert_functions import assert_database_has_no_tasks
from hugging_face.HuggingFaceInterface import HuggingFaceInterface


@pytest.mark.asyncio
async def test_url_relevancy_huggingface_task(db_data_creator):


    def num_to_bool(num: int) -> bool:
        if num == 0:
            return True
        else:
            return False

    async def mock_get_url_relevancy(
        urls_with_html: list[URLWithHTML],
        threshold: float = 0.8
    ) -> list[bool]:
        results = []
        for url_with_html in urls_with_html:
            num = url_with_html.url_id % 2
            results.append(num_to_bool(num))

        return results

    mock_hf_interface = MagicMock(spec=HuggingFaceInterface)
    mock_hf_interface.get_url_relevancy_async = mock_get_url_relevancy

    task_operator = URLRelevanceHuggingfaceTaskOperator(
        adb_client=AsyncDatabaseClient(),
        huggingface_interface=mock_hf_interface
    )
    meets_task_prerequisites = await task_operator.meets_task_prerequisites()
    assert not meets_task_prerequisites

    await assert_database_has_no_tasks(db_data_creator.adb_client)

    batch_id = db_data_creator.batch()
    url_mappings = db_data_creator.urls(batch_id=batch_id, url_count=3).url_mappings
    url_ids = [url_info.url_id for url_info in url_mappings]
    await db_data_creator.html_data(url_ids)

    run_info: TaskOperatorRunInfo = await task_operator.run_task(1)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS, run_info.message


    results = await db_data_creator.adb_client.get_all(AutoRelevantSuggestion)

    assert len(results) == 3
    for result in results:
        assert result.url_id in url_ids
        assert result.relevant == num_to_bool(result.url_id % 2)
