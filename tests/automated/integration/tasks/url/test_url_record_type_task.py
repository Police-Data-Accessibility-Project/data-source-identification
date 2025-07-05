from unittest.mock import MagicMock

import pytest

from src.db.enums import TaskType
from src.db.models.instantiations.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.core.tasks.url.enums import TaskOperatorOutcome
from src.core.tasks.url.operators.record_type.core import URLRecordTypeTaskOperator
from src.core.enums import RecordType
from tests.helpers.db_data_creator import DBDataCreator
from src.core.tasks.url.operators.record_type.llm_api.record_classifier.deepseek import DeepSeekRecordClassifier

@pytest.mark.asyncio
async def test_url_record_type_task(db_data_creator: DBDataCreator):

    mock_classifier = MagicMock(spec=DeepSeekRecordClassifier)
    mock_classifier.classify_url.side_effect = [RecordType.ACCIDENT_REPORTS, "Error"]
    mock_classifier.model_name = "test_notes"

    operator = URLRecordTypeTaskOperator(
        adb_client=db_data_creator.adb_client,
        classifier=mock_classifier
    )

    # Should not meet prerequisites
    meets_prereqs = await operator.meets_task_prerequisites()
    assert not meets_prereqs

    batch_id = db_data_creator.batch()
    iui = db_data_creator.urls(batch_id=batch_id, url_count=2)
    url_ids = [iui.url_mappings[0].url_id, iui.url_mappings[1].url_id]
    await db_data_creator.html_data(url_ids)

    assert await operator.meets_task_prerequisites()
    task_id = await db_data_creator.adb_client.initiate_task(task_type=TaskType.RECORD_TYPE)

    run_info = await operator.run_task(task_id)
    assert run_info.outcome == TaskOperatorOutcome.SUCCESS

    # Task should have been created
    task_info = await db_data_creator.adb_client.get_task_info(task_id=operator.task_id)
    assert task_info.error_info is None

    response = await db_data_creator.adb_client.get_tasks()
    tasks = response.tasks
    assert len(tasks) == 1
    task = tasks[0]
    assert task.type == TaskType.RECORD_TYPE
    assert run_info.linked_url_ids == url_ids
    assert task.url_error_count == 1

    # Get metadata
    suggestions = await db_data_creator.adb_client.get_all(AutoRecordTypeSuggestion)
    for suggestion in suggestions:
        assert suggestion.record_type == RecordType.ACCIDENT_REPORTS.value

