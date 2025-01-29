from unittest.mock import MagicMock

import pytest

from collector_db.enums import TaskType
from collector_db.models import URLMetadata
from core.classes.URLRecordTypeTaskOperator import URLRecordTypeTaskOperator
from core.enums import RecordType, BatchStatus
from tests.helpers.DBDataCreator import DBDataCreator
from tests.helpers.assert_functions import assert_database_has_no_tasks
from llm_api_logic.DeepSeekRecordClassifier import DeepSeekRecordClassifier

@pytest.mark.asyncio
async def test_url_record_type_task(db_data_creator: DBDataCreator):

    mock_classifier = MagicMock(spec=DeepSeekRecordClassifier)
    mock_classifier.classify_url.side_effect = [RecordType.ACCIDENT_REPORTS, "Error"]
    mock_classifier.model_name = "test_notes"

    operator = URLRecordTypeTaskOperator(
        adb_client=db_data_creator.adb_client,
        classifier=mock_classifier
    )
    await operator.run_task()

    # No task should have been created due to not meeting prerequisites
    await assert_database_has_no_tasks(db_data_creator.adb_client)

    batch_id = db_data_creator.batch()
    iui = db_data_creator.urls(batch_id=batch_id, url_count=2)
    url_ids = [iui.url_mappings[0].url_id, iui.url_mappings[1].url_id]
    await db_data_creator.html_data(url_ids)

    await operator.run_task()

    # Task should have been created
    task_info = await db_data_creator.adb_client.get_task_info(task_id=operator.task_id)
    assert task_info.error_info is None
    assert task_info.task_status == BatchStatus.COMPLETE

    response = await db_data_creator.adb_client.get_tasks()
    tasks = response.tasks
    assert len(tasks) == 1
    task = tasks[0]
    assert task.type == TaskType.RECORD_TYPE
    assert task.url_count == 2
    assert task.url_error_count == 1

    # Get metadata
    metadata_results = await db_data_creator.adb_client.get_all(URLMetadata)
    for metadata_row in metadata_results:
        assert metadata_row.notes == "test_notes"
        assert metadata_row.value == RecordType.ACCIDENT_REPORTS.value

