from datetime import datetime, timedelta

from collector_db.DTOs.BatchInfo import BatchInfo
from collector_db.DTOs.DuplicateInfo import DuplicateInfo
from collector_db.DTOs.LogInfo import LogInfo
from collector_db.DTOs.URLMapping import URLMapping
from collector_db.DTOs.URLInfo import URLInfo
from core.enums import BatchStatus
from tests.helpers.DBDataCreator import DBDataCreator


def test_insert_urls(db_client_test):
    # Insert batch
    batch_info = BatchInfo(
        strategy="ckan",
        status=BatchStatus.IN_PROCESS,
        parameters={},
        user_id=1
    )
    batch_id = db_client_test.insert_batch(batch_info)

    urls = [
        URLInfo(
            url="https://example.com/1",
            url_metadata={"name": "example_1"},
        ),
        URLInfo(
            url="https://example.com/2",
        ),
        # Duplicate
        URLInfo(
            url="https://example.com/1",
            url_metadata={"name": "example_duplicate"},
        )
    ]
    insert_urls_info = db_client_test.insert_urls(
        url_infos=urls,
        batch_id=batch_id
    )

    assert insert_urls_info.url_mappings == [
        URLMapping(
            url="https://example.com/1",
            url_id=1
        ),
        URLMapping(
            url="https://example.com/2",
            url_id=2
        )
    ]
    assert insert_urls_info.original_count == 2
    assert insert_urls_info.duplicate_count == 1


def test_insert_logs(db_data_creator: DBDataCreator):
    batch_id_1 = db_data_creator.batch()
    batch_id_2 = db_data_creator.batch()

    db_client = db_data_creator.db_client
    db_client.insert_logs(
        log_infos=[
            LogInfo(log="test log", batch_id=batch_id_1),
            LogInfo(log="test log", batch_id=batch_id_1),
            LogInfo(log="test log", batch_id=batch_id_2),
        ]
    )

    logs = db_client.get_logs_by_batch_id(batch_id_1)
    assert len(logs) == 2

    logs = db_client.get_logs_by_batch_id(batch_id_2)
    assert len(logs) == 1

def test_delete_old_logs(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()

    old_datetime = datetime.now() - timedelta(days=1)
    db_client = db_data_creator.db_client
    log_infos = []
    for i in range(3):
        log_infos.append(LogInfo(log="test log", batch_id=batch_id, created_at=old_datetime))
    db_client.insert_logs(log_infos=log_infos)
    assert len(db_client.get_all_logs()) == 3
    db_client.delete_old_logs()

    logs = db_client.get_all_logs()
    assert len(logs) == 0