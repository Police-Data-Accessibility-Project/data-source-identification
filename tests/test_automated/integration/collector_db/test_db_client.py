import time
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
            collector_metadata={"name": "example_1"},
        ),
        URLInfo(
            url="https://example.com/2",
        ),
        # Duplicate
        URLInfo(
            url="https://example.com/1",
            collector_metadata={"name": "example_duplicate"},
        )
    ]
    insert_urls_info = db_client_test.insert_urls(
        url_infos=urls,
        batch_id=batch_id
    )

    url_mappings = insert_urls_info.url_mappings
    assert len(url_mappings) == 2
    assert url_mappings[0].url == "https://example.com/1"
    assert url_mappings[1].url == "https://example.com/2"


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
    logs = db_client.get_logs_by_batch_id(batch_id=batch_id)
    assert len(logs) == 3
    db_client.delete_old_logs()

    logs = db_client.get_logs_by_batch_id(batch_id=batch_id)
    assert len(logs) == 0

def test_delete_url_updated_at(db_data_creator: DBDataCreator):
    batch_id = db_data_creator.batch()
    url_id = db_data_creator.urls(batch_id=batch_id, url_count=1).url_mappings[0].url_id

    db_client = db_data_creator.db_client
    url_info = db_client.get_urls_by_batch(batch_id=batch_id, page=1)[0]

    old_updated_at = url_info.updated_at


    db_client.update_url(
        url_info=URLInfo(
            id=url_id,
            url="dg",
            collector_metadata={"test_metadata": "test_metadata"},
        )
    )

    url = db_client.get_urls_by_batch(batch_id=batch_id, page=1)[0]
    assert url.updated_at > old_updated_at
